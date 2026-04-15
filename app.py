import json
import csv
import io
import os
import subprocess
from datetime import datetime
from core.segmentation import simulate_fragmentation
from flask import Flask, request, jsonify, render_template
from core.fifo import run_fifo, detect_beladys_anomaly
from core.lru import run_lru
from core.optimal import run_optimal

flask_app = Flask(__name__, template_folder='app/templates', static_folder='app/static', static_url_path='/static')

VALID_ALGOS = {'FIFO', 'LRU', 'Optimal'}
VALID_SEGMENTATION_STRATEGIES = {'first_fit', 'best_fit', 'worst_fit', 'next_fit'}


def _parse_tasklist_mem_kb(mem_text):
    digits = ''.join(ch for ch in str(mem_text) if ch.isdigit())
    return int(digits) if digits else 0


def _get_windows_process_snapshot(limit=96):
    if os.name != 'nt':
        return []

    try:
        # Use PowerShell to get CPU usage (most volatile metric) along with memory
        ps_cmd = (
            "Get-Process | Where-Object { $_.CPU -gt 0 } | "
            "Sort-Object CPU -Descending | Select-Object -First " + str(int(limit)) + " "
            "ProcessName, Id, CPU, @{N='WS';E={$_.WorkingSet64}}, "
            "@{N='BaseAddr';E={try{$_.MainModule.BaseAddress.ToInt64()}catch{0}}} | ConvertTo-Json -Compress"
        )
        tasklist = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_cmd],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5,
            check=False
        )
    except Exception:
        return []

    if tasklist.returncode != 0 or not tasklist.stdout.strip():
        return []

    rows = []
    try:
        raw_data = json.loads(tasklist.stdout)
        if isinstance(raw_data, dict):
            raw_data = [raw_data]
            
        for p in raw_data:
            # We treat CPU as the volatility weight. Fallback to WS if CPU missing.
            cpu = float(p.get('CPU') or 0)
            ws_kb = int(p.get('WS') or 0) // 1024
            base_addr = int(p.get('BaseAddr') or 0)
            rows.append({
                'name': p.get('ProcessName', 'Unknown'),
                'pid': p.get('Id', 0),
                'mem_kb': ws_kb,
                'cpu': cpu,
                'volatility': cpu if cpu > 0 else (ws_kb / 1024.0),
                'base_addr': base_addr
            })
    except json.JSONDecodeError:
        pass

    rows.sort(key=lambda p: p['volatility'], reverse=True)
    return rows


def _build_windows_live_reference(window_size=12, max_page=9):
    """
    Generate a realistic page reference string from real Windows processes.

    Each process's working set memory is divided into virtual pages
    numbered as small integers (compatible with paging algorithms).
    Larger/more active processes occupy more pages. The reference string
    simulates CPU scheduling: processes take turns, and each access
    shows locality of reference (spatial and temporal).
    """
    import random

    window_size = max(4, int(window_size))
    max_page = max(2, int(max_page))

    process_rows = _get_windows_process_snapshot(limit=max(window_size * 6, 60))
    if not process_rows:
        return None

    tick = _get_realtime_tick()
    rng = random.Random(tick // 5)

    # --- Step 1: Group by process name to avoid flooding with duplicates ---
    grouped = {}
    for p in process_rows:
        base = p['name'].replace('.exe', '').strip()
        if not base:
            continue
        if base not in grouped:
            grouped[base] = {
                'name': p['name'], 'pid': p['pid'],
                'mem_kb': 0, 'cpu': 0, 'volatility': 0, 'base_pid': p['pid'],
                'base_addr': p.get('base_addr', 0)
            }
        grouped[base]['mem_kb'] += p['mem_kb']
        grouped[base]['cpu'] += p['cpu']
        grouped[base]['volatility'] += p['volatility']

    top_procs = sorted(grouped.values(), key=lambda g: g['volatility'], reverse=True)
    top_procs = top_procs[:min(8, max(3, max_page - 1))]
    if not top_procs:
        return None

    # --- Step 2: Assign integer page ranges proportional to volatility ---
    total_vol = sum(p['volatility'] for p in top_procs) or 1
    page_assignments = {}  # process_name -> list of integer page numbers
    process_meta = []      # for UI display
    next_page = 1          # integer page counter

    for proc in top_procs:
        proportion = proc['volatility'] / total_vol
        num_pages = max(1, round(proportion * max_page))

        pages = list(range(next_page, next_page + num_pages))
        next_page += num_pages

        page_assignments[proc['name']] = pages
        process_meta.append({
            'name': proc['name'],
            'pid': proc['base_pid'],
            'mem_kb': proc['mem_kb'],
            'cpu': proc['cpu'],
            'pages': pages,
            'page': pages[0],
            'num_pages': len(pages),
            'mem_pct': round(proportion * 100, 1),
            'volatility_label': f"{proc['cpu']:.1f}s CPU" if proc['cpu'] > 0 else f"{proc['mem_kb']//1024} MB"
        })

    # --- Step 3: Build reference string simulating CPU scheduling + locality ---
    all_pages = []
    for v in page_assignments.values():
        all_pages.extend(v)

    reference_string = []
    proc_list = list(page_assignments.keys())
    recent_pages = []

    for i in range(window_size):
        weights = [grouped.get(p.replace('.exe', '').strip(), {}).get('volatility', 1)
                   for p in proc_list]
        total_w = sum(weights) or 1
        weights = [w / total_w for w in weights]

        chosen_proc = rng.choices(proc_list, weights=weights, k=1)[0]
        available_pages = page_assignments[chosen_proc]

        roll = rng.random()

        if roll < 0.20 and recent_pages:
            # Temporal locality: revisit a recent page
            page = rng.choice(recent_pages[-4:])
        elif roll < 0.90 and len(available_pages) > 1:
            # Spatial locality: nearby page in this process
            page = rng.choice(available_pages)
        else:
            # Random access: pick any page from any process (cache miss)
            page = rng.choice(all_pages)

        reference_string.append(page)
        recent_pages.append(page)
        if len(recent_pages) > 8:
            recent_pages.pop(0)

    return {
        'reference_string': reference_string,
        'tick': tick,
        'process_count': len(process_rows),
        'process_window': process_meta,
        'process_rows': process_rows
    }


def _size_from_process_mem(mem_kb):
    # Fit process-derived allocations into simulator memory limits.
    return 64 + ((int(mem_kb) // 128) % 20) * 16


def _build_windows_segmentation_operations(process_rows, live_tick):
    if not process_rows:
        return []

    ops = []
    top = process_rows[:5]

    for idx, proc in enumerate(top[:4]):
        ops.append({
            'action': 'alloc',
            'name': f'P{idx + 1}',
            'size': _size_from_process_mem(proc['mem_kb'])
        })

    if len(top) >= 2:
        ops.append({'action': 'free', 'name': 'P2'})

    if live_tick % 2 == 0:
        ops.append({'action': 'compact'})

    tail_mem = top[4]['mem_kb'] if len(top) >= 5 else top[0]['mem_kb']
    ops.append({'action': 'alloc', 'name': 'P5', 'size': _size_from_process_mem(tail_mem)})

    return ops


def _get_realtime_date_payload():
    now = datetime.now()
    hour = now.hour
    return {
        'source': 'system',
        'iso': now.isoformat(timespec='seconds'),
        'display': now.strftime('%a, %d %b %Y %H:%M:%S'),
        'hour': hour,
        'theme': 'day' if 6 <= hour < 18 else 'night'
    }


def _get_realtime_tick():
    return int(datetime.now().timestamp())


def _is_truthy(value):
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}





def _normalize_reference_string(raw_reference):
    if isinstance(raw_reference, str):
        tokens = raw_reference.replace(',', ' ').split()
        if not tokens:
            raise ValueError('reference_string must contain at least one page number')
        reference = [int(token, 0) if token.startswith('0x') or token.startswith('0X') else int(token) for token in tokens]
    elif isinstance(raw_reference, list):
        if not raw_reference:
            raise ValueError('reference_string must contain at least one page number')
        reference = []
        for x in raw_reference:
            if isinstance(x, str) and (x.startswith('0x') or x.startswith('0X')):
                reference.append(int(x, 16))
            else:
                reference.append(int(x))
    else:
        raise ValueError('reference_string must be a list or a comma-separated string')

    if any(page < 0 for page in reference):
        raise ValueError('reference_string cannot contain negative page numbers')

    return reference


def _build_paging_payload(reference_string, frames, selected_algo, max_belady_frames):
    if frames <= 0:
        raise ValueError('frames must be greater than 0')

    if selected_algo not in VALID_ALGOS:
        raise ValueError('Invalid algorithm selected')

    if max_belady_frames < 2:
        raise ValueError('max_belady_frames must be at least 2')

    fifo_res = run_fifo(reference_string, frames)
    lru_res = run_lru(reference_string, frames)
    optimal_res = run_optimal(reference_string, frames)
    belady_res = detect_beladys_anomaly(reference_string, max_belady_frames)

    current_res_map = {
        'FIFO': fifo_res,
        'LRU': lru_res,
        'Optimal': optimal_res
    }

    return {
        'current': current_res_map[selected_algo],
        'fifo': fifo_res,
        'lru': lru_res,
        'optimal': optimal_res,
        'belady': belady_res,
        'meta': {
            'reference_string': reference_string,
            'frames': frames,
            'algorithm': selected_algo,
            'max_belady_frames': max_belady_frames
        }
    }

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/fifo')
def fifo_page():
    return render_template('fifo.html')

@flask_app.route('/lru')
def lru_page():
    return render_template('lru.html')

@flask_app.route('/optimal')
def optimal_page():
    return render_template('optimal.html')


@flask_app.route('/api/realtime-date', methods=['GET'])
def realtime_date_api():
    return jsonify(_get_realtime_date_payload())


@flask_app.route('/api/realtime-algorithms', methods=['GET'])
def realtime_algorithms_api():
    try:
        live_mode = _is_truthy(request.args.get('live', '0'))
        live_source = str(request.args.get('live_source', 'windows')).strip().lower()
        live_tick = None
        live_source_used = 'manual'
        windows_process_rows = []
        windows_process_window = []
        windows_process_count = 0

        if live_mode:
            if live_source != 'windows':
                raise ValueError('Only live_source=windows is supported in live mode')

            windows_live = _build_windows_live_reference(
                window_size=request.args.get('window_size', 12),
                max_page=request.args.get('max_page', 9)
            )

            if not windows_live:
                raise ValueError('Could not retrieve Windows process data. Live mode requires Windows OS with running processes.')

            ref_string = windows_live['reference_string']
            live_tick = windows_live['tick']
            windows_process_rows = windows_live['process_rows']
            windows_process_window = windows_live['process_window']
            windows_process_count = windows_live['process_count']
            live_source_used = 'windows'
        else:
            ref_string = _normalize_reference_string(
                request.args.get('reference_string', '7,0,1,2,0,3,0,4,2,3,0,3,2')
            )

        frames = int(request.args.get('frames', 3))
        selected_algo = request.args.get('algorithm', 'FIFO')
        max_belady_frames = int(request.args.get('max_belady_frames', 10))

        paging_payload = _build_paging_payload(
            reference_string=ref_string,
            frames=frames,
            selected_algo=selected_algo,
            max_belady_frames=max_belady_frames
        )
        paging_payload['meta']['live'] = live_mode
        paging_payload['meta']['live_source'] = live_source_used
        if live_tick is not None:
            paging_payload['meta']['live_tick'] = live_tick
        if windows_process_count:
            paging_payload['meta']['process_count'] = windows_process_count
            paging_payload['meta']['processes'] = windows_process_window

        payload = {
            'timestamp': _get_realtime_date_payload(),
            'paging': paging_payload
        }

        operations_json = request.args.get('operations')
        if operations_json or live_mode:
            strategy = request.args.get('strategy', 'first_fit')
            if strategy not in VALID_SEGMENTATION_STRATEGIES:
                raise ValueError('Invalid strategy')

            if operations_json:
                operations = json.loads(operations_json)
            else:
                operations = _build_windows_segmentation_operations(
                    windows_process_rows,
                    live_tick or _get_realtime_tick()
                )

            if not isinstance(operations, list):
                raise ValueError('Operations must be a list')

            total_memory = int(request.args.get('total_memory', 4096))
            block_size = int(request.args.get('block_size', 16))

            snapshots = simulate_fragmentation(
                operations=operations,
                strategy=strategy,
                total_memory=total_memory,
                block_size=block_size
            )

            payload['segmentation'] = {
                'strategy': strategy,
                'total_memory': total_memory,
                'block_size': block_size,
                'live': live_mode,
                'live_source': live_source_used,
                'operations': operations,
                'snapshots': snapshots,
                'latest': snapshots[-1] if snapshots else None
            }

        return jsonify(payload)

    except json.JSONDecodeError:
        return jsonify({'error': 'operations must be valid JSON'}), 400
    except ValueError as e:
        return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flask_app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json
    
    if not data or 'reference_string' not in data or 'frames' not in data or 'algorithm' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        ref_string = _normalize_reference_string(data['reference_string'])
        frames = int(data['frames'])
        selected_algo = data['algorithm']
        max_belady_frames = int(data.get('max_belady_frames', 10))

        return jsonify(_build_paging_payload(
            reference_string=ref_string,
            frames=frames,
            selected_algo=selected_algo,
            max_belady_frames=max_belady_frames
        ))

    except ValueError as e:
        return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    # =========================
# T18: SEGMENTATION ROUTES
# =========================

@flask_app.route('/segmentation')
def segmentation_page():
    return render_template('segmentation.html')


@flask_app.route('/api/segmentation', methods=['POST'])
def segmentation_api():
    try:
        data = request.json

        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        operations = data.get('operations')
        strategy = data.get('strategy')
        total_memory = data.get('total_memory', 4096)
        block_size = data.get('block_size', 16)

        # Validate strategy
        valid_strategies = ['first_fit', 'best_fit', 'worst_fit', 'next_fit']
        if strategy not in valid_strategies:
            return jsonify({'error': 'Invalid strategy'}), 400

        # Validate operations
        if not isinstance(operations, list):
            return jsonify({'error': 'Operations must be a list'}), 400

        # Call core segmentation logic
        result = simulate_fragmentation(
            operations=operations,
            strategy=strategy,
            total_memory=total_memory,
            block_size=block_size
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# =========================
# T19: LIVE SEGMENTATION (REAL PROCESSES)
# =========================

@flask_app.route('/api/live-segmentation', methods=['GET'])
def live_segmentation_api():
    """Segmentation simulation driven by real Windows process data."""
    try:
        strategy = request.args.get('strategy', 'first_fit')
        if strategy not in VALID_SEGMENTATION_STRATEGIES:
            raise ValueError('Invalid segmentation strategy')

        total_memory = int(request.args.get('total_memory', 16384))
        block_size = int(request.args.get('block_size', 64))
        max_procs = min(int(request.args.get('max_processes', 8)), 12)
        extra_ops_raw = request.args.get('extra_ops', None)

        # --- Fetch real Windows processes ---
        raw = _get_windows_process_snapshot(limit=96)

        if not raw:
            raise ValueError('Could not retrieve Windows process data. Live segmentation requires Windows OS with running processes.')

        # Group by base process name and aggregate memory
        groups = {}
        for p in raw:
            base_name = p['name'].replace('.exe', '').strip()
            if not base_name:
                continue
            if base_name not in groups:
                groups[base_name] = {
                    'name': base_name, 'mem_kb': 0,
                    'count': 0, 'pids': []
                }
            groups[base_name]['mem_kb'] += p['mem_kb']
            groups[base_name]['count'] += 1
            groups[base_name]['pids'].append(p['pid'])

        top = sorted(
            groups.values(), key=lambda g: g['mem_kb'], reverse=True
        )[:max_procs]
        total_real_kb = sum(g['mem_kb'] for g in top) or 1

        # --- Build proportional segment allocations ---
        target_used = total_memory * 0.72
        operations = []
        proc_details = []

        for gp in top:
            proportion = gp['mem_kb'] / total_real_kb
            budget = max(block_size * 4, int(target_used * proportion))

            segs = {}
            for seg_type, frac in [
                ('.text', 0.15), ('.heap', 0.50),
                ('.data', 0.12), ('.stack', 0.08)
            ]:
                seg_name = gp['name'] + seg_type
                seg_size = max(block_size, int(budget * frac))
                segs[seg_name] = seg_size
                operations.append({
                    'action': 'alloc',
                    'name': seg_name,
                    'size': seg_size
                })

            proc_details.append({
                'name': gp['name'],
                'real_mem_kb': gp['mem_kb'],
                'real_mem_mb': round(gp['mem_kb'] / 1024, 1),
                'pids': gp['pids'][:5],
                'instances': gp['count'],
                'segments': segs,
                'budget': budget,
            })

        # --- Append extra user operations (free / compact / alloc) ---
        if extra_ops_raw:
            extra = json.loads(extra_ops_raw)
            if isinstance(extra, list):
                operations.extend(extra)

        # --- Run the segmentation simulation ---
        snapshots = simulate_fragmentation(
            operations=operations,
            total_memory=total_memory,
            strategy=strategy,
            block_size=block_size,
        )

        return jsonify({
            'processes': proc_details,
            'system': {
                'total_process_count': len(raw),
                'selected_count': len(top),
                'total_real_mem_kb': total_real_kb,
                'total_real_mem_mb': round(total_real_kb / 1024, 1),
            },
            'simulation': {
                'strategy': strategy,
                'total_memory': total_memory,
                'block_size': block_size,
                'operations': operations,
                'snapshots': snapshots,
            },
            'timestamp': _get_realtime_date_payload(),
        })

    except json.JSONDecodeError:
        return jsonify({'error': 'extra_ops must be valid JSON'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flask_app.route('/api/live-seg-compare', methods=['GET'])
def live_seg_compare_api():
    """
    Run the SAME operations across all 4 segmentation strategies using
    real Windows process data.  The operation sequence is designed to
    create multiple holes of different sizes so the strategies diverge.
    """
    try:
        total_memory = int(request.args.get('total_memory', 4096))
        block_size = int(request.args.get('block_size', 16))

        # --- Fetch real Windows processes ---
        raw = _get_windows_process_snapshot(limit=96)
        if not raw:
            raise ValueError('Cannot retrieve Windows process snapshot')

        # Group by base process name
        groups = {}
        for p in raw:
            base_name = p['name'].replace('.exe', '').strip()
            if not base_name:
                continue
            if base_name not in groups:
                groups[base_name] = {'name': base_name, 'mem_kb': 0, 'cpu': 0}
            groups[base_name]['mem_kb'] += p['mem_kb']
            groups[base_name]['cpu'] += p.get('cpu', 0)

        top = sorted(groups.values(), key=lambda g: g['mem_kb'], reverse=True)[:8]
        if len(top) < 3:
            raise ValueError('Not enough processes for comparison')

        total_real_kb = sum(g['mem_kb'] for g in top) or 1

        # --- Build operations that create multiple different-sized holes ---
        # Phase 1: Allocate all processes proportionally
        operations = []
        alloc_names = []
        target_used = total_memory * 0.80
        proc_info = []

        for i, gp in enumerate(top):
            proportion = gp['mem_kb'] / total_real_kb
            seg_size = max(block_size * 2, int(target_used * proportion))
            name = gp['name']
            operations.append({'action': 'alloc', 'name': name, 'size': seg_size})
            alloc_names.append(name)
            proc_info.append({
                'name': name,
                'mem_kb': gp['mem_kb'],
                'cpu': gp['cpu'],
                'seg_size': seg_size
            })

        # Phase 2: Free ALTERNATING processes to create holes of different sizes
        # This is the key: freeing every other process creates multiple holes
        # of varying sizes, which is exactly what makes strategies diverge.
        freed = []
        for i in range(0, len(alloc_names), 2):
            operations.append({'action': 'free', 'name': alloc_names[i]})
            freed.append(alloc_names[i])

        # Phase 3: Allocate 2 new small segments that must pick among the holes
        # These sizes are chosen to be smaller than the freed holes so there
        # are multiple valid placements — each strategy picks differently.
        if freed:
            small1 = max(block_size, proc_info[0]['seg_size'] // 3)
            small2 = max(block_size, proc_info[0]['seg_size'] // 5)
            operations.append({'action': 'alloc', 'name': 'NEW_A', 'size': small1})
            operations.append({'action': 'alloc', 'name': 'NEW_B', 'size': small2})

        # --- Run all 4 strategies on the SAME operations ---
        strategies = ['first_fit', 'best_fit', 'worst_fit', 'next_fit']
        results = {}
        for strat in strategies:
            snapshots = simulate_fragmentation(
                operations=operations,
                strategy=strat,
                total_memory=total_memory,
                block_size=block_size
            )
            final = snapshots[-1] if snapshots else None
            results[strat] = {
                'snapshots': snapshots,
                'final': final,
                'fragmentation': final['fragmentation'] if final else None,
            }

        return jsonify({
            'strategies': results,
            'operations': operations,
            'total_memory': total_memory,
            'block_size': block_size,
            'process_source': proc_info,
            'timestamp': _get_realtime_date_payload(),
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Expose 'app' for Vercel serverless deployment
app = flask_app

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
