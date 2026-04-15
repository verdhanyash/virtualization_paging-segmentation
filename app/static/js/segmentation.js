/* ══════════════════════════════════════════════
   *  STATE
   * ══════════════════════════════════════════════ */
  var state = {
    strategy: 'first_fit',
    totalMem: 16384,
    blockSize: 64,
    maxProcs: 8,
    processes: [],
    systemInfo: {},
    snapshots: [],
    extraOps: [],
    loading: false
  };
  var livePollInt = null;
  var pendingCustomOps = [];

  function toggleCoSize() {
    var act = document.getElementById('co-action').value;
    document.getElementById('co-size-container').style.display = (act === 'alloc') ? '' : 'none';
    if (act === 'compact') {
      document.getElementById('co-name').disabled = true;
      document.getElementById('co-name').value = '';
    } else {
      document.getElementById('co-name').disabled = false;
    }
  }

  function addCustomOp() {
    var act = document.getElementById('co-action').value;
    var nm = document.getElementById('co-name').value.trim();
    var sz = parseInt(document.getElementById('co-size').value, 10);
    
    if (act !== 'compact' && !nm) { alert('Process Name requires a value.'); return; }
    
    var op = { action: act };
    if (act !== 'compact') op.name = nm;
    if (act === 'alloc') {
      if (isNaN(sz) || sz <= 0) { alert('Size must be a positive integer.'); return; }
      op.size = sz;
    }
    
    pendingCustomOps.push(op);
    renderCustomOps();
  }

  function removeCustomOp(idx) {
    pendingCustomOps.splice(idx, 1);
    renderCustomOps();
  }

  function clearCustomOps() {
    pendingCustomOps = [];
    renderCustomOps();
  }

  function renderCustomOps() {
    var ul = document.getElementById('co-list');
    if (!ul) return;
    ul.innerHTML = '';
    for (var i = 0; i < pendingCustomOps.length; i++) {
        var op = pendingCustomOps[i];
        var li = document.createElement('li');
        li.style.padding = '4px 8px';
        li.style.borderBottom = '1px solid #1e293b';
        li.style.display = 'flex';
        li.style.justifyContent = 'space-between';
        
        var txt = '<strong>' + op.action.toUpperCase() + '</strong>';
        if (op.name) txt += ' \u2014 ' + op.name;
        if (op.size) txt += ' (' + op.size + 'B)';
        
        li.innerHTML = '<span>' + txt + '</span><span style="color:#ef4444;cursor:pointer" onclick="removeCustomOp(' + i + ')">\u2715</span>';
        ul.appendChild(li);
    }
  }

  /* ── Color system ── */
  var PROC_HUES = [190, 35, 280, 150, 320, 60, 220, 10, 100, 250];
  var procColorMap = {};
  var procColorIdx = 0;

  function getColorForProcess(name) {
    if (!(name in procColorMap)) {
      procColorMap[name] = PROC_HUES[procColorIdx % PROC_HUES.length];
      procColorIdx++;
    }
    var hue = procColorMap[name];
    return {
      main:  'hsl(' + hue + ',80%,50%)',
      dim:   'hsl(' + hue + ',50%,30%)',
      light: 'hsl(' + hue + ',90%,65%)',
      text:  'hsl(' + hue + ',80%,80%)'
    };
  }

  function parseSegName(name) {
    if (!name) return { proc: 'unknown', type: '' };
    var d = name.lastIndexOf('.');
    if (d > 0) return { proc: name.substring(0, d), type: name.substring(d) };
    return { proc: name, type: '' };
  }

  function formatProcessMemory(memKb) {
    var kb = Number(memKb);
    if (!isFinite(kb) || kb <= 0) return '0 MB';
    if (kb >= 1024 * 1024) return (kb / 1024 / 1024).toFixed(1) + ' GB';
    return Math.max(1, Math.round(kb / 1024)) + ' MB';
  }

  /* ══════════════════════════════════════════════
   *  API CALL
   * ══════════════════════════════════════════════ */
  function toggleSegMode() {
    var live = document.getElementById('liveToggleSeg').checked;
    document.getElementById('inp-custom-ops').style.display = live ? 'none' : 'block';
  }

  function loadLiveData() {
    if (state.loading) return;
    state.loading = true;
    updateButtonState();

    var useLive = document.getElementById('liveToggleSeg') && document.getElementById('liveToggleSeg').checked;
    
    if (useLive) {
      var q = 'strategy=' + encodeURIComponent(state.strategy) +
        '&total_memory=' + state.totalMem +
        '&block_size=' + state.blockSize +
        '&max_processes=' + state.maxProcs;

      if (state.extraOps.length > 0) {
        q += '&extra_ops=' + encodeURIComponent(JSON.stringify(state.extraOps));
      }

      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/live-segmentation?' + q, true);
      xhr.onreadystatechange = xhrCallback;
      xhr.send();
    } else {
      var customOps = pendingCustomOps.slice();
      var postData = {
        strategy: state.strategy,
        total_memory: state.totalMem,
        block_size: state.blockSize,
        operations: customOps
      };
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/segmentation', true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.onreadystatechange = xhrCallback;
      xhr.send(JSON.stringify(postData));
    }
    
    function xhrCallback() {
      if (xhr.readyState !== 4) return;
      state.loading = false;
      updateButtonState();

      if (xhr.status === 200) {
        try {
          var data = JSON.parse(xhr.responseText);
          state.processes = data.processes || [];
          state.systemInfo = data.system || {};
          state.snapshots = (data.snapshots || (data.simulation && data.simulation.snapshots)) ? (data.snapshots || data.simulation.snapshots) : [];

          /* rebuild color map from process order */
          procColorMap = {};
          procColorIdx = 0;
          for (var i = 0; i < state.processes.length; i++) {
            getColorForProcess(state.processes[i].name);
          }
          renderAll();
        } catch (e) {
          console.error('Parse error:', e);
        }
      } else {
        try {
          var errData = JSON.parse(xhr.responseText);
          alert('Segmentation error: ' + (errData.error || xhr.responseText));
        } catch (_) {
          console.error('API error', xhr.status, xhr.responseText);
        }
      }
    };
  }

  function updateButtonState() {
    var btn = document.getElementById('btn-start');
    if (state.loading) {
      btn.textContent = '⏳ LOADING…';
      btn.classList.add('loading');
      btn.disabled = true;
    } else {
      btn.innerHTML = 'START_SIMULATION <span>▶</span>';
      btn.classList.remove('loading');
      btn.disabled = false;
    }
  }

  /* ══════════════════════════════════════════════
   *  ACTIONS
   * ══════════════════════════════════════════════ */
  function setStrategy(s) {
    state.strategy = s;
    document.getElementById('active-strat-lbl').textContent = s.toUpperCase();
    var tabs = document.querySelectorAll('.strat-btn');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].classList.toggle('on', tabs[i].getAttribute('data-strategy') === s);
    }
    if (s === 'best_fit') document.getElementById('ax-lat').textContent = 'O(N)';
    else document.getElementById('ax-lat').textContent = 'O(N)';

    if (state.processes && state.processes.length > 0) {
      refreshLive();
    }
  }

  function startLivePolling() {
    if (livePollInt) clearInterval(livePollInt);
    livePollInt = setInterval(function () {
      if (!state.loading) loadLiveData();
    }, 10000);
  }

  function stopLivePolling() {
    if (livePollInt) {
      clearInterval(livePollInt);
      livePollInt = null;
    }
  }

  function refreshLive() {
    state.extraOps = [];
    procColorMap = {};
    procColorIdx = 0;
    loadLiveData();
    startLivePolling();
  }
  
  function triggerCompaction() {
    var op = { action: 'compact' };
    state.extraOps.push(op);
    loadLiveData();
  }

  function resetAll() {
    stopLivePolling();
    state.extraOps = [];
    state.snapshots = [];
    state.processes = [];
    procColorMap = {};
    procColorIdx = 0;
    renderAll();
  }

  /* ── Config listeners ── */
  document.getElementById('inp-total-mem').addEventListener('change', function () {
    var v = parseInt(this.value); if (v > 0) { state.totalMem = v; state.extraOps = []; }
  });
  document.getElementById('inp-block-size').addEventListener('change', function () {
    var v = parseInt(this.value); if (v > 0) { state.blockSize = v; state.extraOps = []; }
  });
  document.getElementById('inp-max-procs').addEventListener('change', function () {
    var v = parseInt(this.value); if (v >= 2 && v <= 12) { state.maxProcs = v; state.extraOps = []; }
  });

  /* ══════════════════════════════════════════════
   *  RENDER ALL
   * ══════════════════════════════════════════════ */
  function renderAll() {
    var snap = state.snapshots.length > 0 ? state.snapshots[state.snapshots.length - 1] : null;
    renderProcessList();
    renderStats(snap);
    renderCompositionBar(snap);
    renderBlockGrid(snap);
    renderSegmentTable(snap);
    renderHolesTable(snap);
    renderHistory();
  }

  /* ══════════════════════════════════════════════
   *  RENDER: Process List
   * ══════════════════════════════════════════════ */
  function renderProcessList() {
    var container = document.getElementById('proc-list');
    var badge = document.getElementById('proc-count-badge');

    if (!state.processes || state.processes.length === 0) {
      container.innerHTML = '<div class="empty">Click START_SIMULATION to load</div>';
      badge.textContent = '—';
      return;
    }

    badge.textContent = state.processes.length + ' of ' + (state.systemInfo.total_process_count || '?') + ' procs';

    var html = '';
    for (var i = 0; i < state.processes.length; i++) {
      var p = state.processes[i];
      var memLabel = formatProcessMemory(p.real_mem_kb);
      var segs = Object.keys(p.segments || {}).length;
      var c = getColorForProcess(p.name);
      var pid = (p.pids && p.pids.length > 0) ? p.pids[0] : '—';

      html += '<div class="proc-card proc-card-compact" style="border-color:' + c.dim + '" title="' + memLabel + ' · ' + segs + ' segments">' +
        '<div class="proc-card-accent" style="background:' + c.main + '"></div>' +
        '<div class="proc-card-top">' +
          '<div class="proc-name">' + p.name + '</div>' +
          '<div class="proc-pid" style="color:' + c.main + '">PID:' + pid + '</div>' +
        '</div>' +
      '</div>';
    }
    container.innerHTML = html;
  }

  /* ══════════════════════════════════════════════
   *  RENDER: Stats
   * ══════════════════════════════════════════════ */
  function renderStats(snap) {
    var ids = ['st-used','st-free','st-int','st-ext','st-holes','st-util'];
    if (!snap || !snap.fragmentation) {
      for (var i = 0; i < ids.length; i++) document.getElementById(ids[i]).textContent = '—';
      return;
    }
    var f = snap.fragmentation;
    document.getElementById('st-used').textContent = fmtB(f.used);
    document.getElementById('st-free').textContent = fmtB(f.total_free);

    var intEl = document.getElementById('st-int');
    intEl.textContent = fmtB(f.internal_frag);
    intEl.className = 'sc-val' + (f.internal_frag > 0 ? ' sc-warn' : '');

    var extEl = document.getElementById('st-ext');
    extEl.textContent = fmtB(f.external_frag);
    extEl.className = 'sc-val' + (f.external_frag > 0 ? ' sc-err' : '');

    var holeCount = (snap.free_holes) ? snap.free_holes.filter(function(h) {
      /* don't count trailing free as a "hole" */
      var lastSegEnd = 0;
      if (snap.memory_map) {
        for (var k = snap.memory_map.length - 1; k >= 0; k--) {
          if (snap.memory_map[k].type === 'segment') { lastSegEnd = snap.memory_map[k].base + snap.memory_map[k].size; break; }
        }
      }
      return (h.base + h.size) <= lastSegEnd;
    }).length : 0;
    var hEl = document.getElementById('st-holes');
    hEl.textContent = holeCount;
    hEl.className = 'sc-val' + (holeCount > 0 ? ' sc-err' : '');

    document.getElementById('st-util').textContent = f.utilization + '%';
  }

  function fmtB(b) {
    if (b >= 1048576) return (b / 1048576).toFixed(1) + ' MB';
    if (b >= 1024) return (b / 1024).toFixed(1) + ' KB';
    return b + ' B';
  }

  /* ══════════════════════════════════════════════
   *  RENDER: Composition Bar (Live Address Space)
   * ══════════════════════════════════════════════ */
  function renderCompositionBar(snap) {
    var bar = document.getElementById('comp-bar');
    var legend = document.getElementById('comp-legend');
    bar.innerHTML = '';
    legend.innerHTML = '';

    if (!snap || !snap.memory_map || snap.memory_map.length === 0) {
      bar.innerHTML = '<div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--text-dimmer);font-size: 9.6px;">No data — click START_SIMULATION</div>';
      return;
    }

    var totalMem = state.totalMem;
    var colorsSeen = {};

    for (var i = 0; i < snap.memory_map.length; i++) {
      var block = snap.memory_map[i];
      var pct = (block.size / totalMem * 100);
      if (pct < 0.05) continue;

      var div = document.createElement('div');
      div.style.width = pct + '%';

      if (block.type === 'segment') {
        var parsed = parseSegName(block.name);
        var c = getColorForProcess(parsed.proc);
        div.className = 'comp-seg';
        div.style.background = c.main;

        /* Label inside large segments */
        if (pct > 5) {
          div.textContent = parsed.proc.substring(0, 10).toUpperCase();
        }

        /* Tooltip */
        var tt = document.createElement('div');
        tt.className = 'comp-tooltip';
        tt.textContent = block.name + ' [' + block.size + 'B]';
        div.appendChild(tt);

        if (!colorsSeen[parsed.proc]) colorsSeen[parsed.proc] = c.main;

      } else if (block.type === 'hole') {
        div.className = 'comp-hole';
        div.style.position = 'relative';
        var ht = document.createElement('div');
        ht.className = 'comp-tooltip';
        ht.textContent = 'HOLE [' + block.size + 'B]';
        div.appendChild(ht);
      } else {
        div.className = 'comp-free';
      }
      bar.appendChild(div);
    }

    /* Legend */
    var lh = '';
    var pnames = Object.keys(colorsSeen);
    for (var k = 0; k < pnames.length; k++) {
      lh += '<div class="legend-item"><span class="legend-swatch" style="background:' + colorsSeen[pnames[k]] + '"></span>' + pnames[k] + '</div>';
    }
    lh += '<div class="legend-item"><span class="legend-swatch" style="background:repeating-linear-gradient(45deg,#331111,#331111 2px,#1a0808 2px,#1a0808 4px)"></span>HOLE</div>';
    lh += '<div class="legend-item"><span class="legend-swatch" style="background:var(--bg-panel);border:1px solid var(--border-mid)"></span>FREE</div>';
    legend.innerHTML = lh;
  }

  /* ══════════════════════════════════════════════
   *  RENDER: Block-Level Memory Map
   * ══════════════════════════════════════════════ */
  function renderBlockGrid(snap) {
    var container = document.getElementById('memory-grid');
    var countLbl = document.getElementById('block-count-lbl');
    container.innerHTML = '';

    if (!snap || !snap.memory_map) {
      countLbl.textContent = '—';
      return;
    }

    var totalBlocks = Math.ceil(state.totalMem / state.blockSize);
    countLbl.textContent = totalBlocks + ' blocks × ' + state.blockSize + 'B';

    var tooltip = document.getElementById('mem-tooltip');

    for (var j = 0; j < snap.memory_map.length; j++) {
      var item = snap.memory_map[j];
      var blocks = Math.ceil(item.size / state.blockSize);
      var parsed = parseSegName(item.name);
      var c = item.type === 'segment' ? getColorForProcess(parsed.proc) : null;

      /* Internal frag blocks for segments */
      var intFragBlocks = 0;
      if (item.type === 'segment' && item.internal_frag > 0) {
        intFragBlocks = Math.ceil(item.internal_frag / state.blockSize);
      }
      var usedBlocks = blocks - intFragBlocks;

      for (var b = 0; b < blocks; b++) {
        var cell = document.createElement('div');
        cell.className = 'mem-cell';

        if (item.type === 'segment') {
          if (b < usedBlocks) {
            cell.style.background = c.main;
          } else {
            /* internal frag blocks — hatched */
            cell.style.background = 'repeating-linear-gradient(45deg,' + c.dim + ',' + c.dim + ' 2px, transparent 2px, transparent 4px)';
          }
          cell.setAttribute('data-proc', parsed.proc);
          cell.setAttribute('data-seg', item.name);
          cell.setAttribute('data-info', item.name + ' | Base: ' + item.base + ' | Req: ' + (item.requested || item.size) + 'B | Alloc: ' + item.size + 'B | IntFrag: ' + (item.internal_frag || 0) + 'B');
        } else if (item.type === 'hole') {
          cell.className += ' mem-cell-hole';
          cell.setAttribute('data-info', 'HOLE | Base: ' + item.base + ' | Size: ' + item.size + 'B');
        } else {
          cell.className += ' mem-cell-free';
          cell.setAttribute('data-info', 'FREE | Base: ' + item.base + ' | Size: ' + item.size + 'B');
        }
        container.appendChild(cell);
      }
    }

    /* Hover tooltip with mousemove */
    container.onmousemove = function (e) {
      var t = e.target;
      if (t.classList.contains('mem-cell')) {
        tooltip.textContent = t.getAttribute('data-info') || '';
        tooltip.style.display = 'block';
        tooltip.style.left = (e.clientX + 14) + 'px';
        tooltip.style.top = (e.clientY - 10) + 'px';
      }
    };
    container.onmouseleave = function () {
      tooltip.style.display = 'none';
    };
  }

  /* ══════════════════════════════════════════════
   *  RENDER: Segment Table
   * ══════════════════════════════════════════════ */
  function renderSegmentTable(snap) {
    var emptyEl = document.getElementById('seg-table-empty');
    var tableEl = document.getElementById('segment-table');
    var countLbl = document.getElementById('seg-count-lbl');

    if (!snap || !snap.segments || Object.keys(snap.segments).length === 0) {
      emptyEl.style.display = 'block';
      tableEl.style.display = 'none';
      countLbl.textContent = '—';
      return;
    }

    emptyEl.style.display = 'none';
    

    var names = Object.keys(snap.segments);
    countLbl.textContent = names.length + ' segments';

    var tbody = document.getElementById('segment-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    tableEl.style.display = 'flex'; // override default table display
    
    for (var i = 0; i < names.length; i++) {
      var n = names[i];
      var seg = snap.segments[n];
      var parsed = parseSegName(n);
      var c = getColorForProcess(parsed.proc);

      var fragVal = seg.internal_frag || 0;
      var fragClass = fragVal > 0 ? 'color:var(--accent-red); font-weight:600;' : '';

      var isSystem = parsed.proc.toLowerCase().includes('system') || parsed.proc.toLowerCase().includes('svchost') || parsed.proc.toLowerCase().includes('csrss') || parsed.proc.toLowerCase().includes('kernel');
      var icon = isSystem ? '⚙' : '🏷️';
      if (parsed.type.includes('.text')) icon = '📝';
      else if (parsed.type.includes('.data')) icon = '🗃️';
      else if (parsed.type.includes('.heap')) icon = '📦';
      else if (parsed.type.includes('.stack')) icon = '📚';

      var div = document.createElement('div');
      div.className = 'seg-row-card';
      div.innerHTML = `
        <div class="seg-row-indicator" style="background:${c.main}"></div>
        <div class="seg-row-name-col">
          <div class="seg-icon-box" style="color:${c.main}; border-color:${c.dim}">${icon}</div>
          <div class="seg-title-wrap">
             <div class="seg-title">${parsed.proc}</div>
             <div class="seg-subtitle">PROCESS SEGMENT</div>
          </div>
        </div>
        <div class="seg-val-col" style="color:${c.text}">${parsed.type}</div>
        <div class="seg-val-col">${seg.base}</div>
        <div class="seg-val-col">${seg.limit}</div>
        <div class="seg-hl-col" style="color:${c.main}">${seg.allocated_size}</div>
        <div class="seg-val-col" style="${fragClass}">${fragVal > 0 ? fragVal : '-'}</div>
        <div class="action-menu">⋮</div>
      `;
      tbody.appendChild(div);
    }
  }

  /* ══════════════════════════════════════════════
   *  RENDER: Free Holes Table
   * ══════════════════════════════════════════════ */
  function renderHolesTable(snap) {
    var emptyEl = document.getElementById('holes-table-empty');
    var tableEl = document.getElementById('holes-table');
    emptyEl.textContent = 'No holes — memory is contiguous';

    if (!snap || !snap.free_holes || snap.free_holes.length === 0) {
      emptyEl.textContent = 'Run START_SIMULATION to inspect free holes';
      emptyEl.style.display = 'block';
      tableEl.style.display = 'none';
      return;
    }

    /* Filter: only show actual holes between segments, not trailing free */
    var lastSegEnd = 0;
    if (snap.memory_map) {
      for (var m = snap.memory_map.length - 1; m >= 0; m--) {
        if (snap.memory_map[m].type === 'segment') {
          lastSegEnd = snap.memory_map[m].base + snap.memory_map[m].size;
          break;
        }
      }
    }

    var realHoles = [];
    for (var k = 0; k < snap.free_holes.length; k++) {
      var h = snap.free_holes[k];
      if ((h.base + h.size) <= lastSegEnd) realHoles.push(h);
    }

    if (realHoles.length === 0) {
      emptyEl.textContent = 'No holes — memory is contiguous';
      emptyEl.style.display = 'block';
      tableEl.style.display = 'none';
      return;
    }

    emptyEl.style.display = 'none';
    

    var tbody = tableEl.querySelector('tbody');
    tbody.innerHTML = '';

    for (var i = 0; i < realHoles.length; i++) {
      var hole = realHoles[i];
      var pct = ((hole.size / state.totalMem) * 100).toFixed(1);
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td>#' + (i + 1) + '</td>' +
        '<td class="num">' + hole.base + '</td>' +
        '<td class="num">' + hole.size + ' B</td>' +
        '<td class="num">' + pct + '%</td>';
      tbody.appendChild(tr);
    }

    tableEl.style.display = 'table';
  }

  /* ══════════════════════════════════════════════
   *  RENDER: Operation History
   * ══════════════════════════════════════════════ */
  function renderHistory() {
    var histLog = document.getElementById('history-log');
    var histEmpty = document.getElementById('hist-empty');
    var countLbl = document.getElementById('ops-count-lbl');

    if (!state.snapshots || state.snapshots.length === 0) {
      histEmpty.style.display = 'block';
      countLbl.textContent = '—';
      /* clear old rows */
      var old = histLog.querySelectorAll('.hist-row');
      for (var x = 0; x < old.length; x++) old[x].remove();
      return;
    }

    histEmpty.style.display = 'none';
    countLbl.textContent = state.snapshots.length + ' ops';

    /* Clear existing rows */
    var existing = histLog.querySelectorAll('.hist-row');
    for (var y = 0; y < existing.length; y++) existing[y].remove();

    for (var i = 0; i < state.snapshots.length; i++) {
      var snap = state.snapshots[i];
      var op = snap.operation;
      if (!op) continue;

      var isOk = (snap.error === null || snap.error === undefined);
      var parsed = parseSegName(op.name || '');

      /* Format operation text */
      var opText = '';
      if (op.action === 'alloc') {
        opText = '<span class="h-action">alloc</span> <span class="h-proc">' + parsed.proc + '</span>' +
                 '<span class="h-type">' + parsed.type + '</span> <span class="h-size">(' + (op.size || '?') + 'B)</span>';
      } else if (op.action === 'free') {
        opText = '<span class="h-action">free</span> <span class="h-proc">' + parsed.proc + '</span>' +
                 '<span class="h-type">' + parsed.type + '</span>';
      } else if (op.action === 'compact') {
        opText = '<span class="h-action">compact</span> <span class="h-proc">SYSTEM DEFRAG</span>';
      } else {
        opText = '<span class="h-action">' + op.action + '</span>';
      }

      var statusText = isOk
        ? '<span style="color:var(--accent-green)">✓ OK</span>'
        : '<span style="color:var(--accent-red)">✗ ERR</span>';

      var row = document.createElement('div');
      row.className = 'hist-row ' + (isOk ? 'hist-ok' : 'hist-err');
      row.innerHTML =
        '<div class="h-num">#' + (i + 1) + '</div>' +
        '<div class="h-op">' + opText + '</div>' +
        '<div class="h-status">' + statusText + '</div>';

      if (!isOk) {
        row.title = 'Error: ' + snap.error;
      }

      histLog.appendChild(row);
    }

    /* Auto-scroll to bottom */
    histLog.scrollTop = histLog.scrollHeight;
  }

  /* ══════════════════════════════════════════════
   *  BOOT — page loads clean, user clicks START
   * ══════════════════════════════════════════════ */
  window.onload = function () {
    renderAll();
    // Don't auto-start — wait for user to click START_SIMULATION
  };
