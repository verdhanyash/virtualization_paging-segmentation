var allResults = null;
    var cComp = null, cBelady = null, cRace = null;
    var compareTimer = null;
    var realtimeCompareInt = null;

    function $(id) { return document.getElementById(id); }

    function getFC() { return parseInt($('fcSlider').value); }

    function scheduleCompare() {
      if (compareTimer) clearTimeout(compareTimer);
      compareTimer = setTimeout(function () {
        runCompare();
      }, 350);
    }

    $('fcSlider').addEventListener('input', function () { $('fcDisp').textContent = this.value; });
    $('refIn').addEventListener('keydown', function (e) { if (e.key === 'Enter') runCompare(); });
    $('fcSlider').addEventListener('change', scheduleCompare);
    $('refIn').addEventListener('input', scheduleCompare);

    var CHART_FONT = "'JetBrains Mono','Courier New',monospace";
    var CHART_AXIS = {
      ticks: { color: '#204768', font: { family: CHART_FONT, size: 12 } },
      grid: { color: 'rgba(37,99,235,.14)' },
      border: { color: 'rgba(37,99,235,.36)' }
    };

    function runCompare() {
      requestRealtimeCompare({ showLoading: true, silent: false });
    }

    function requestRealtimeCompare(opts) {
      opts = opts || {};

      var fc = getFC();
      var btn = document.querySelector('.bp');
      if (opts.showLoading && btn) {
        btn.innerHTML = '&#8987; Loading...';
        btn.disabled = true;
      }

      var useLive = $('liveToggle') && $('liveToggle').checked;
      $('refIn').readOnly = useLive;
      var query =
        '&frames=' + encodeURIComponent(fc) +
        '&algorithm=FIFO' +
        '&max_belady_frames=10';
      if (useLive) {
        query += '&live=1&live_source=windows&window_size=12&max_page=9';
      } else {
        query += '&live=0&reference_string=' + encodeURIComponent($('refIn').value);
      }

      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/realtime-algorithms?' + query.replace(/^&/, ''), true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          if (opts.showLoading && btn) {
            btn.innerHTML = '&#9654; Start Simulation';
            btn.disabled = false;
          }

          if (xhr.status === 200) {
            try {
              var payload = JSON.parse(xhr.responseText);
              if (payload.timestamp) applyRealtimeDateUI(payload.timestamp);
              if (payload.paging) {
                if (payload.paging.meta && payload.paging.meta.reference_string) {
                  $('refIn').value = payload.paging.meta.reference_string.join(',');
                  if (payload.paging.meta.processes && payload.paging.meta.processes.length) {
                    $('refIn').title = payload.paging.meta.processes
                      .map(function (p) { return p.name + ' (' + p.pid + ')'; })
                      .join(' | ');
                    renderProcessSource(payload.paging.meta.processes);
                  }
                }
                allResults = payload.paging;
                renderComparison();
              }
            } catch (e) {
              console.error('Failed to parse API response:', e);
              if (!opts.silent) alert('Error parsing server response.');
            }
          } else if (!opts.silent) {
            try {
              var errData = JSON.parse(xhr.responseText);
              alert('Error: ' + (errData.error || xhr.responseText));
            } catch (_) {
              alert('Error: ' + xhr.responseText);
            }
          }
        }
      };
      xhr.send();
    }

    function startRealtimeComparePolling() {
      if (realtimeCompareInt) clearInterval(realtimeCompareInt);
      realtimeCompareInt = setInterval(function () {
        requestRealtimeCompare({ silent: true });
      }, 10000);
    }

    function renderComparison() {
      if (!allResults) return;

      $('cmpEmpty').style.display = 'none';
      $('cmpResults').style.display = '';

      var fifo = allResults.fifo;
      var lru = allResults.lru;
      var opt = allResults.optimal;

      // Find best
      var minF = Math.min(fifo.total_faults, lru.total_faults, opt.total_faults);

      // Update cards
      $('cf-fifo').textContent = fifo.total_faults;
      $('cs-fifo').textContent = fifo.total_faults + ' faults / ' + fifo.total_hits + ' hits (' + Math.round(fifo.total_faults / fifo.steps.length * 100) + '%)';
      $('cc-fifo').className = 'cmp-card' + (fifo.total_faults === minF ? ' cc-best' : '');

      $('cf-lru').textContent = lru.total_faults;
      $('cs-lru').textContent = lru.total_faults + ' faults / ' + lru.total_hits + ' hits (' + Math.round(lru.total_faults / lru.steps.length * 100) + '%)';
      $('cc-lru').className = 'cmp-card' + (lru.total_faults === minF ? ' cc-best' : '');

      $('cf-opt').textContent = opt.total_faults;
      $('cs-opt').textContent = opt.total_faults + ' faults / ' + opt.total_hits + ' hits (' + Math.round(opt.total_faults / opt.steps.length * 100) + '%)';
      $('cc-opt').className = 'cmp-card' + (opt.total_faults === minF ? ' cc-best' : '');

      // Destroy old charts
      if (cComp) { cComp.destroy(); cComp = null; }
      if (cBelady) { cBelady.destroy(); cBelady = null; }
      if (cRace) { cRace.destroy(); cRace = null; }

      // Comparison bar chart
      cComp = new Chart($('compChart'), {
        type: 'bar',
        data: {
          labels: ['FIFO', 'LRU', 'Optimal'],
          datasets: [{
            label: 'Faults',
            data: [fifo.total_faults, lru.total_faults, opt.total_faults],
            backgroundColor: ['#2563EB', '#0EA5E9', '#7C3AED'],
            borderRadius: 2, borderSkipped: false
          }, {
            label: 'Hits',
            data: [fifo.total_hits, lru.total_hits, opt.total_hits],
            backgroundColor: ['rgba(37,99,235,.15)', 'rgba(14,165,233,.16)', 'rgba(124,58,237,.16)'],
            borderColor: ['rgba(37,99,235,.38)', 'rgba(14,165,233,.4)', 'rgba(124,58,237,.4)'],
            borderWidth: 1, borderRadius: 2, borderSkipped: false
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { x: CHART_AXIS, y: CHART_AXIS }
        }
      });

      // Belady's chart
      var bel = allResults.belady;
      var anomalyFs = {};
      for (var a = 0; a < bel.anomaly_at.length; a++) { anomalyFs[bel.anomaly_at[a][1]] = true; }
      $('anomalyBadge').style.display = bel.anomaly_found ? '' : 'none';

      var fLabels = Object.keys(bel.fault_counts).map(Number);
      var fData = [], ptColors = [], ptSizes = [];
      for (var i = 0; i < fLabels.length; i++) {
        fData.push(bel.fault_counts[fLabels[i]]);
        ptColors.push(anomalyFs[fLabels[i]] ? '#DC2626' : '#2563EB');
        ptSizes.push(anomalyFs[fLabels[i]] ? 7 : 3);
      }

      cBelady = new Chart($('beladyChart'), {
        type: 'line',
        data: {
          labels: fLabels, datasets: [{
            label: 'Faults', data: fData,
            borderColor: '#1D4ED8', backgroundColor: 'rgba(37,99,235,.1)',
            pointBackgroundColor: ptColors, pointBorderColor: ptColors, pointRadius: ptSizes,
            tension: .2, borderWidth: 2.2, fill: true
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: Object.assign({}, CHART_AXIS, { title: { display: true, text: 'Frames', color: '#204768', font: { family: CHART_FONT, size: 11 } } }),
            y: Object.assign({}, CHART_AXIS, { title: { display: true, text: 'Faults', color: '#204768', font: { family: CHART_FONT, size: 11 } } })
          }
        }
      });

      // Fault race chart
      function cumFaults(r) {
        var arr = [], c = 0;
        for (var i = 0; i < r.steps.length; i++) { if (r.steps[i].fault) c++; arr.push(c); }
        return arr;
      }
      var stepLbls = [];
      for (var i = 0; i < fifo.steps.length; i++) { stepLbls.push(i + 1); }

      cRace = new Chart($('raceChart'), {
        type: 'line',
        data: {
          labels: stepLbls,
          datasets: [
            { label: 'FIFO', data: cumFaults(fifo), borderColor: '#2563EB', pointRadius: 0, tension: 0.08, borderWidth: 2.2 },
            { label: 'LRU', data: cumFaults(lru), borderColor: '#0EA5E9', pointRadius: 0, tension: 0.08, borderWidth: 2.2 },
            { label: 'Optimal', data: cumFaults(opt), borderColor: '#7C3AED', pointRadius: 0, tension: 0.08, borderWidth: 2.2 }
          ]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: Object.assign({}, CHART_AXIS, { title: { display: true, text: 'Step', color: '#204768', font: { family: CHART_FONT, size: 11 } }, ticks: Object.assign({}, CHART_AXIS.ticks, { maxTicksLimit: 14 }) }),
            y: Object.assign({}, CHART_AXIS, { title: { display: true, text: 'Cumulative Faults', color: '#204768', font: { family: CHART_FONT, size: 11 } } })
          }
        }
      });
    }

    function resetCompare() {
      allResults = null;
      $('cmpEmpty').style.display = '';
      $('cmpResults').style.display = 'none';
      if (cComp) { cComp.destroy(); cComp = null; }
      if (cBelady) { cBelady.destroy(); cBelady = null; }
      if (cRace) { cRace.destroy(); cRace = null; }
      $('anomalyBadge').style.display = 'none';
    }

    Chart.defaults.color = '#204768';

    // --- Segmentation Strategy Comparison (Live Process Data) ---
    var STRATEGIES = ['first_fit', 'best_fit', 'worst_fit', 'next_fit'];
    var STRAT_LABELS = { 'first_fit': 'First-Fit', 'best_fit': 'Best-Fit', 'worst_fit': 'Worst-Fit', 'next_fit': 'Next-Fit' };
    var cSegExt = null, cSegUtil = null;
    var segCompareInt = null;

    function runSegCompare() {
      var btn = document.getElementById('segLiveBtn');
      if (btn) { btn.innerHTML = '&#8987; Loading...'; btn.disabled = true; }

      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/live-seg-compare?total_memory=4096&block_size=16', true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState !== 4) return;
        if (btn) { btn.innerHTML = '&#9654; Live Compare'; btn.disabled = false; }

        if (xhr.status === 200) {
          try {
            var data = JSON.parse(xhr.responseText);
            renderSegComparison(data);
          } catch (e) {
            console.error('Seg compare parse error', e);
            alert('Error parsing segmentation comparison response: ' + e.message);
          }
        } else {
          try {
            var errData = JSON.parse(xhr.responseText);
            alert('Segmentation compare error: ' + (errData.error || xhr.responseText));
          } catch (_) {
            alert('Segmentation compare error (HTTP ' + xhr.status + '): ' + xhr.responseText);
          }
        }
      };
      xhr.send();
    }

    function renderSegComparison(data) {
      $('segEmpty').style.display = 'none';
      $('segResults').style.display = '';

      // Show process source chips
      var srcEl = $('segProcSrc');
      if (srcEl && data.process_source) {
        var srcHtml = '';
        for (var p = 0; p < data.process_source.length; p++) {
          var ps = data.process_source[p];
          var memKb = (typeof ps.mem_kb === 'number' && Number.isFinite(ps.mem_kb)) ? ps.mem_kb : 0;
          var memMB = memKb > 0 ? Math.round(memKb / 1024) + 'MB' : '—';
          srcHtml += '<span class="proc-chip">' + ps.name + ' <span class="pc-mem">' + memMB + '</span></span>';
        }
        srcEl.innerHTML = srcHtml;
        srcEl.style.display = '';
      }

      var cards = $('segCards');
      cards.innerHTML = '';

      var minExt = Infinity;
      var stratData = [];
      for (var i = 0; i < STRATEGIES.length; i++) {
        var strat = STRATEGIES[i];
        var stratResult = data.strategies[strat];
        var f = stratResult && stratResult.fragmentation ? stratResult.fragmentation : null;
        var ext = f ? f.external_frag : 0;
        if (ext < minExt) minExt = ext;
        stratData.push({ strat: strat, frag: f, ext: ext });
      }

      var extData = [], utilData = [], labels = [];
      for (var i = 0; i < stratData.length; i++) {
        var d = stratData[i];
        var f = d.frag;
        var isBest = d.ext === minExt;
        labels.push(STRAT_LABELS[d.strat]);
        extData.push(f ? f.external_frag : 0);
        utilData.push(f ? f.utilization : 0);

        var card = document.createElement('div');
        card.className = 'seg-card' + (isBest ? ' best-card' : '');
        var intFrag = f ? f.internal_frag : 0;
        var used = f ? f.used : 0;
        var total = f ? f.total : 0;
        var util = f ? f.utilization : 0;
        card.innerHTML = '<div class="seg-card-name">' + STRAT_LABELS[d.strat] + '</div>' +
          '<div class="seg-card-val">' + (d.ext) + 'B</div>' +
          '<div class="seg-card-sub">external fragmentation</div>' +
          '<div class="seg-detail-row">' +
          '<div class="seg-detail warn">Int.Frag: <span>' + intFrag + 'B</span></div>' +
          '<div class="seg-detail">Used: <span>' + used + '/' + total + '</span></div>' +
          '</div>' +
          '<div class="seg-detail-row">' +
          '<div class="seg-detail">Util: <span>' + util + '%</span></div>' +
          '<div class="seg-detail">' + (isBest ? '\u2605 BEST' : '') + '</div>' +
          '</div>';
        cards.appendChild(card);
      }

      // Charts
      if (cSegExt) { cSegExt.destroy(); cSegExt = null; }
      if (cSegUtil) { cSegUtil.destroy(); cSegUtil = null; }

      var barColors = ['#2563EB', '#0EA5E9', '#7C3AED', '#1D4ED8'];

      cSegExt = new Chart($('segExtChart'), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{ label: 'Ext.Frag (bytes)', data: extData, backgroundColor: barColors, borderRadius: 2, borderSkipped: false }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { x: CHART_AXIS, y: Object.assign({}, CHART_AXIS, { title: { display: true, text: 'Bytes', color: '#204768', font: { family: CHART_FONT, size: 11 } } }) }
        }
      });

      cSegUtil = new Chart($('segUtilChart'), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{ label: 'Utilization %', data: utilData, backgroundColor: barColors, borderRadius: 2, borderSkipped: false }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { x: CHART_AXIS, y: Object.assign({}, CHART_AXIS, { title: { display: true, text: '%', color: '#204768', font: { family: CHART_FONT, size: 11 } }, max: 100 }) }
        }
      });
    }

    function resetSegCompare() {
      $('segEmpty').style.display = '';
      $('segResults').style.display = 'none';
      $('segCards').innerHTML = '';
      var srcEl = $('segProcSrc');
      if (srcEl) srcEl.style.display = 'none';
      if (cSegExt) { cSegExt.destroy(); cSegExt = null; }
      if (cSegUtil) { cSegUtil.destroy(); cSegUtil = null; }
    }

    // Auto-run live compare on page load and poll every 30s
    runSegCompare();
    segCompareInt = setInterval(runSegCompare, 30000);

    function applyRealtimeDateUI(payload) {
      var nav = document.querySelector('nav');
      if (!nav || !payload) return;

      var badge = document.getElementById('realtimeDateBadge');
      if (!badge) {
        badge = document.createElement('span');
        badge.id = 'realtimeDateBadge';
        badge.style.marginLeft = 'auto';
        badge.style.fontSize = '10px';
        badge.style.letterSpacing = '.06em';
        badge.style.textTransform = 'uppercase';
        badge.style.padding = '4px 10px';
        badge.style.border = '1px solid var(--border-mid)';
        badge.style.borderRadius = '3px';
        badge.style.color = 'var(--text-dimmer)';
        nav.appendChild(badge);
      }

      badge.textContent = 'Live ' + payload.display;

      if (payload.theme === 'day') {
        document.documentElement.style.setProperty('--b3', '#5a5a5a');
        document.documentElement.style.setProperty('--bg2', '#141414');
      } else {
        document.documentElement.style.setProperty('--b3', '#444');
        document.documentElement.style.setProperty('--bg2', '#111');
      }
    }

    function refreshRealtimeDate() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/realtime-date', true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
          try { applyRealtimeDateUI(JSON.parse(xhr.responseText)); } catch(e) {}
        }
      };
      xhr.send();
    }

    refreshRealtimeDate();
    setInterval(refreshRealtimeDate, 30000);
    requestRealtimeCompare({ silent: true });
    startRealtimeComparePolling();

    function renderProcessSource(procs) {
      var c = $('procSrcChips');
      if (!c || !procs || procs.length === 0) return;
      var html = '';
      for (var i = 0; i < procs.length; i++) {
        var p = procs[i];
        var memMB = Math.round(p.mem_kb / 1024);
        html += '<span class="proc-chip">' + p.name + ' <span class="pc-mem">PID:' + p.pid + ' &middot; ' + memMB + 'MB</span></span>';
      }
      c.innerHTML = html;
    }
