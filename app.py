from core.segmentation import simulate_fragmentation
from core.engine import translate_address
from flask import Flask, request, jsonify, render_template
from core.fifo import run_fifo, detect_beladys_anomaly
from core.lru import run_lru
from core.optimal import run_optimal

flask_app = Flask(__name__, template_folder='app', static_folder='app', static_url_path='')

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

@flask_app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json
    
    if not data or 'reference_string' not in data or 'frames' not in data or 'algorithm' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
        
    try:
        ref_string = [int(x) for x in data['reference_string']]
        frames = int(data['frames'])
        selected_algo = data['algorithm']
        max_belady_frames = int(data.get('max_belady_frames', 10))
        
        # Run all algorithms for charts
        fifo_res = run_fifo(ref_string, frames)
        lru_res = run_lru(ref_string, frames)
        optimal_res = run_optimal(ref_string, frames)
        
        # Detect Belady's anomaly
        belady_res = detect_beladys_anomaly(ref_string, max_belady_frames)
        
        # Determine the currently selected algorithm's result
        if selected_algo == 'FIFO':
            current_res = fifo_res
        elif selected_algo == 'LRU':
            current_res = lru_res
        elif selected_algo == 'Optimal':
            current_res = optimal_res
        else:
            return jsonify({'error': 'Invalid algorithm selected'}), 400
            
        return jsonify({
            'current': current_res,
            'fifo': fifo_res,
            'lru': lru_res,
            'optimal': optimal_res,
            'belady': belady_res
        })
    
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# =========================
# ADDRESS TRANSLATION ROUTE
# =========================

@flask_app.route('/api/translate', methods=['POST'])
def translate_api():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        virtual_address = data.get('virtual_address')
        page_size = data.get('page_size')

        if virtual_address is None or page_size is None:
            return jsonify({'error': 'virtual_address and page_size are required'}), 400

        virtual_address = int(virtual_address)
        page_size = int(page_size)

        page_number, offset = translate_address(virtual_address, page_size)

        return jsonify({
            'virtual_address': virtual_address,
            'page_size': page_size,
            'page_number': page_number,
            'offset': offset
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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

# Expose 'app' for Vercel serverless deployment
app = flask_app

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
