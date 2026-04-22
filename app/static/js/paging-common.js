/**
 * paging-common.js — Shared logic for FIFO, LRU, and Optimal paging pages.
 *
 * All rendering, API calls, step playback, charts, and process source display
 * are handled here in one place.
 */

if (window.location.pathname.includes('fifo')) {
    window.ALGO = 'FIFO';
} else if (window.location.pathname.includes('lru')) {
    window.ALGO = 'LRU';
} else if (window.location.pathname.includes('optimal')) {
    window.ALGO = 'Optimal';
}

var result = null, curStep = -1, autoInt = null;
var allResults = null;
var cBelady = null, cTimeline = null;
var runTimer = null;
var realtimeRunInt = null;

function $(id) { return document.getElementById(id); }
function show(id) { $(id).style.display = ''; }
function hide(id) { $(id).style.display = 'none'; }

function getFC() { return parseInt($('fcSlider').value); }
function scheduleRun() {
  if (runTimer) clearTimeout(runTimer);
  runTimer = setTimeout(function() { runSim(); }, 350);
}
function getSpd() {
  var s = parseInt($('spdSlider').value);
  return Math.round(2200 - (s - 1) * (2100 / 9));
}

function updateBtns() {
  var ok = result !== null;
  var total = ok ? result.steps.length : 0;
  var s = curStep;
  $('stepBtn').disabled = !ok || s >= total - 1;
  $('autoBtn').disabled = !ok;
  $('autoBtn').textContent = autoInt ? '\u23F8 Pause' : '\u25B6 Auto';
}

function renderStep(si) {
  if (!result) return;
  var steps = result.steps;
  var frame_count = result.frame_count;
  var s = steps[si];
  var total = steps.length;

  $('sNum').textContent = (si + 1) + '/' + total;
  $('sPage').textContent = s.page;

  var pill = $('fPill');
  if (s.fault) {
    pill.className = 'fpill is-fault';
    pill.textContent = '\u25C6 FAULT';
  } else {
    pill.className = 'fpill is-hit';
    pill.textContent = '\u00B7 HIT';
  }

  var evStat = $('evStat');
  if (s.evicted !== null && s.evicted !== undefined) {
    evStat.style.display = '';
    $('sEvict').textContent = s.evicted;
  } else {
    evStat.style.display = 'none';
  }

  var faultsSoFar = 0;
  for (var k = 0; k <= si; k++) { if (steps[k].fault) faultsSoFar++; }
  $('sFaultsSoFar').textContent = faultsSoFar;

  var fr = $('framesRow');
  var prev = si > 0 ? steps[si - 1] : null;
  fr.innerHTML = '';
  for (var f = 0; f < frame_count; f++) {
    var page = s.frames[f];
    var prevPage = prev ? prev.frames[f] : null;
    var isNew = s.fault && page === s.page && page !== prevPage;
    var isEmpty = page === null;
    var box = document.createElement('div');
    box.className = 'fbox' + (isEmpty ? ' empty' : ' loaded') + (isNew ? ' newly' : '');
    box.innerHTML = '<span class="fidx">F' + f + '</span><span class="fpage">' + (isEmpty ? '\u2014' : page) + '</span>';
    fr.appendChild(box);
  }

  $('progFill').style.width = (((si + 1) / total) * 100) + '%';

  var rp = $('refPills');
  rp.innerHTML = '';
  for (var i = 0; i < steps.length; i++) {
    var st = steps[i];
    var p = document.createElement('div');
    var cls = 'rpill';
    if (i === si) cls += ' cur';
    else if (i < si) cls += st.fault ? ' fpast' : ' hpast';
    else cls += ' fut';
    p.className = cls;
    p.textContent = st.page;
    p.title = 'Step ' + (i+1) + ': Page ' + st.page + ' \u2014 ' + (st.fault ? 'FAULT' : 'HIT');
    (function(idx) { p.onclick = function() { curStep = idx; renderStep(idx); updateBtns(); }; })(i);
    rp.appendChild(p);
  }

  document.querySelectorAll('.ccol').forEach(function(el) { el.classList.remove('ccol'); });
  var colCells = document.querySelectorAll('.c' + si);
  for (var c = 0; c < colCells.length; c++) { colCells[c].classList.add('ccol'); }

  var nf = 0, nh = 0;
  for (var j = 0; j <= si; j++) { if (steps[j].fault) nf++; else nh++; }
  $('stAlgo').textContent = result.algorithm;
  $('stF').textContent = nf;
  $('stH').textContent = nh;
  $('stR').textContent = Math.round(nf / (si + 1) * 100) + '%';

  // DEMAND PAGING VISUALIZATION
  var allPagesFound = {};
  for (var pi = 0; pi < steps.length; pi++) { allPagesFound[steps[pi].page] = true; }
  var uniquePages = Object.keys(allPagesFound).sort(function(a,b){return parseInt(a)-parseInt(b)});

  var ptUI = $('pageTableUI');
  var bsUI = $('backingStoreUI');
  if (ptUI && bsUI) {
    var ptHtml = '';
    for (var k2 = 0; k2 < uniquePages.length; k2++) {
        var pg = uniquePages[k2];
        var isLoaded = s.frames.indexOf(parseFloat(pg)) !== -1 || s.frames.indexOf(String(pg)) !== -1 || s.frames.indexOf(+pg) !== -1;
        var vBit = isLoaded ? 'V' : 'I';
        var col = isLoaded ? '#10b981' : '#f43f5e';
        ptHtml += '<div style="border:1px solid '+col+';color:'+col+';padding:2px 4px;font-size:11px;border-radius:2px;">Pg ' + pg + ' : ' + vBit + '</div>';
    }
    ptUI.innerHTML = ptHtml;

    var bsHtml = '';
    for (var stepIdx = 0; stepIdx <= si; stepIdx++) {
       var st2 = steps[stepIdx];
       if (st2.fault) {
           bsHtml += '<div style="color:#10b981;">Step '+(stepIdx+1)+': [SWAP-IN] Page '+st2.page+' loaded from disk.</div>';
           if (st2.evicted !== null && st2.evicted !== undefined) {
               bsHtml += '<div style="color:#94a3b8;">Step '+(stepIdx+1)+': [SWAP-OUT] Page '+st2.evicted+' evicted to disk.</div>';
           }
       }
    }
    if (bsHtml === '') bsHtml = '<div style="color:var(--text-dimmer)">No swaps yet...</div>';
    bsUI.innerHTML = bsHtml;
    bsUI.scrollTop = bsUI.scrollHeight;
  }

  // Update timeline chart to track current step
  if (typeof renderTimelineChart === 'function' && cTimeline) renderTimelineChart();
}

function renderHistory() {
  if (!result) return;
  var steps = result.steps;
  var frame_count = result.frame_count;
  var h = '<table>';

  h += '<tr><td class="rl">&mdash;</td>';
  for (var i = 0; i < steps.length; i++) { h += '<th>' + (i + 1) + '</th>'; }
  h += '</tr>';

  h += '<tr><td class="rl">Page</td>';
  for (var i = 0; i < steps.length; i++) {
    h += '<td class="' + (steps[i].fault ? 'cf' : 'ch') + ' c' + i + '">' + steps[i].page + '</td>';
  }
  h += '</tr>';

  for (var f = 0; f < frame_count; f++) {
    h += '<tr><td class="rl">Frame ' + f + '</td>';
    for (var i = 0; i < steps.length; i++) {
      var page = steps[i].frames[f];
      if (page === null) h += '<td class="ce c' + i + '">&mdash;</td>';
      else if (steps[i].fault && page === steps[i].page) h += '<td class="cn c' + i + '">' + page + '</td>';
      else h += '<td class="ck c' + i + '">' + page + '</td>';
    }
    h += '</tr>';
  }

  h += '<tr><td class="rl">Evicted</td>';
  for (var i = 0; i < steps.length; i++) {
    if (steps[i].evicted !== null && steps[i].evicted !== undefined)
      h += '<td class="cv c' + i + '">' + steps[i].evicted + '</td>';
    else
      h += '<td class="cnd c' + i + '">&middot;</td>';
  }
  h += '</tr>';

  h += '<tr><td class="rl">Fault?</td>';
  for (var i = 0; i < steps.length; i++) {
    h += '<td class="' + (steps[i].fault ? 'cfy' : 'cfn') + ' c' + i + '">' + (steps[i].fault ? 'F' : '\u00B7') + '</td>';
  }
  h += '</tr></table>';
  $('histTable').innerHTML = h;
}

var CHART_FONT = "'JetBrains Mono','Courier New',monospace";
var CHART_AXIS = {
  ticks: { color:'#204768', font:{family:CHART_FONT, size: 12} },
  grid: { color:'rgba(37,99,235,.14)' },
  border: { color:'rgba(37,99,235,.36)' }
};

function triggerBeladyAnomaly() {
  // Classic reference string that triggers Bélády's Anomaly:
  // 3 frames → 9 faults, 4 frames → 10 faults
  var refEl = $('refIn');
  if (refEl) refEl.value = '1,2,3,4,1,2,5,1,2,3,4,5';
  var liveToggle = $('liveToggle');
  if (liveToggle) liveToggle.checked = false;
  if (typeof toggleSegMode === 'function') toggleSegMode();
  if (refEl) refEl.readOnly = false;
  runSim();
}

function renderCharts() {
  if (!allResults) return;

  if (cBelady) { cBelady.destroy(); cBelady = null; }
  if (cTimeline) { cTimeline.destroy(); cTimeline = null; }

  // ═══ Belady's Anomaly Chart ═══
  var bel = allResults.belady;
  var anomalyFs = {};
  for (var a = 0; a < bel.anomaly_at.length; a++) { anomalyFs[bel.anomaly_at[a][1]] = true; }
  $('anomalyBadge').style.display = bel.anomaly_found ? '' : 'none';
  var noAnomalyEl = $('beladyNoAnomaly');
  if (noAnomalyEl) noAnomalyEl.style.display = bel.anomaly_found ? 'none' : '';
  hide('beladyEmpty'); show('beladyWrap');

  var fLabels = Object.keys(bel.fault_counts).map(Number);
  var fData = [];
  var ptColors = [];
  var ptSizes = [];
  var ptStyles = [];
  for (var i = 0; i < fLabels.length; i++) {
    fData.push(bel.fault_counts[fLabels[i]]);
    var isAnomaly = anomalyFs[fLabels[i]];
    ptColors.push(isAnomaly ? '#dc2626' : '#2563eb');
    ptSizes.push(isAnomaly ? 8 : 4);
    ptStyles.push(isAnomaly ? 'triangle' : 'circle');
  }

  // Highlight the current frame count
  var curFC = getFC();
  var curFCIdx = fLabels.indexOf(curFC);

  cBelady = new Chart($('beladyChart'), {
    type:'line',
    data:{
      labels:fLabels,
      datasets:[
        {
          label:'Page Faults', data:fData,
          borderColor:'#1d4ed8',
          backgroundColor: function(ctx) {
            var c = ctx.chart.ctx;
            var g = c.createLinearGradient(0, 0, 0, ctx.chart.height);
            g.addColorStop(0, 'rgba(37,99,235,.25)');
            g.addColorStop(1, 'rgba(37,99,235,.02)');
            return g;
          },
          pointBackgroundColor:ptColors,
          pointBorderColor:ptColors,
          pointRadius:ptSizes,
          pointStyle:ptStyles,
          pointHoverRadius: 10,
          tension:.2, borderWidth:2.5, fill:true
        },
        // Current frame count marker
        curFCIdx >= 0 ? {
          label:'Current Frames',
          data: fLabels.map(function(f, idx) { return idx === curFCIdx ? fData[idx] : null; }),
          pointBackgroundColor: '#f59e0b',
          pointBorderColor: '#f59e0b',
          pointRadius: 10,
          pointStyle: 'star',
          pointHoverRadius: 14,
          borderWidth: 0,
          showLine: false
        } : null
      ].filter(Boolean)
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      interaction: { mode: 'index', intersect: false },
      plugins:{
        legend:{display:false},
        tooltip:{
          backgroundColor:'rgba(15,23,42,.92)',
          titleFont:{family:CHART_FONT, size:12},
          bodyFont:{family:CHART_FONT, size:11},
          padding:10,
          callbacks:{
            title: function(items) {
              var f = items[0].label;
              return f + ' Frame' + (f > 1 ? 's' : '');
            },
            label: function(item) {
              if (item.datasetIndex > 0) return '\u2605 Your current frame count';
              var faults = item.parsed.y;
              var frames = item.label;
              var prevFaults = item.dataIndex > 0 ? fData[item.dataIndex - 1] : null;
              var lines = [faults + ' page fault' + (faults !== 1 ? 's' : '')];
              if (prevFaults !== null) {
                var diff = faults - prevFaults;
                if (diff > 0) lines.push('\u26A0 +' + diff + ' more than ' + (frames-1) + ' frames (ANOMALY!)');
                else if (diff < 0) lines.push('\u2193 ' + Math.abs(diff) + ' fewer than ' + (frames-1) + ' frames');
                else lines.push('\u2192 Same as ' + (frames-1) + ' frames');
              }
              return lines;
            },
            labelColor: function(item) {
              if (item.datasetIndex > 0) return { borderColor:'#f59e0b', backgroundColor:'#f59e0b' };
              var isAn = anomalyFs[fLabels[item.dataIndex]];
              return { borderColor: isAn ? '#dc2626' : '#2563eb', backgroundColor: isAn ? '#dc2626' : '#2563eb' };
            }
          }
        }
      },
      scales:{
        x:Object.assign({}, CHART_AXIS, {title:{display:true,text:'Number of Frames',color:'#204768',font:{family:CHART_FONT,size: 11}}}),
        y:Object.assign({}, CHART_AXIS, {title:{display:true,text:'Page Faults',color:'#204768',font:{family:CHART_FONT,size: 11}}, beginAtZero:true})
      }
    }
  });

  // ═══ Fault Timeline Chart (bar per step + cumulative line) ═══
  hide('timelineEmpty'); show('timelineWrap');
  renderTimelineChart();
}

function renderTimelineChart() {
  if (!result || !result.steps) return;
  if (cTimeline) { cTimeline.destroy(); cTimeline = null; }

  var steps = result.steps;
  var stepLbls = [];
  var barData = [];
  var barColors = [];
  var cumData = [];
  var cnt = 0;
  var activeStep = curStep >= 0 ? curStep : steps.length - 1;

  for (var i = 0; i < steps.length; i++) {
    stepLbls.push(i + 1);
    if (steps[i].fault) {
      cnt++;
      barData.push(1);
      barColors.push(i <= activeStep ? 'rgba(239,68,68,.8)' : 'rgba(239,68,68,.2)');
    } else {
      barData.push(-0.3);
      barColors.push(i <= activeStep ? 'rgba(16,185,129,.7)' : 'rgba(16,185,129,.15)');
    }
    cumData.push(cnt);
  }

  cTimeline = new Chart($('timelineChart'), {
    type:'bar',
    data:{
      labels:stepLbls,
      datasets:[
        {
          label:'Fault / Hit',
          data:barData,
          backgroundColor:barColors,
          borderRadius: 2,
          borderSkipped: false,
          yAxisID:'y',
          order:2
        },
        {
          type:'line',
          label:'Total Faults',
          data:cumData,
          borderColor:'#2563eb',
          backgroundColor:'rgba(37,99,235,.08)',
          pointRadius: function(ctx) { return ctx.dataIndex === activeStep ? 7 : 2; },
          pointBackgroundColor: function(ctx) { return ctx.dataIndex === activeStep ? '#f59e0b' : '#2563eb'; },
          pointBorderColor: function(ctx) { return ctx.dataIndex === activeStep ? '#f59e0b' : '#2563eb'; },
          tension:0.15, borderWidth:2.5, fill:false,
          yAxisID:'y2',
          order:1
        }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      interaction: { mode: 'index', intersect: false },
      plugins:{
        legend:{
          display:true,
          labels:{ color:'#204768', font:{family:CHART_FONT, size:10}, boxWidth:12, padding:10,
            generateLabels: function() {
              return [
                { text: 'Fault', fillStyle:'rgba(239,68,68,.8)', strokeStyle:'transparent', lineWidth:0 },
                { text: 'Hit', fillStyle:'rgba(16,185,129,.7)', strokeStyle:'transparent', lineWidth:0 },
                { text: 'Cumulative', fillStyle:'transparent', strokeStyle:'#2563eb', lineWidth:2 }
              ];
            }
          }
        },
        tooltip:{
          backgroundColor:'rgba(15,23,42,.92)',
          titleFont:{family:CHART_FONT, size:12},
          bodyFont:{family:CHART_FONT, size:11},
          padding:10,
          callbacks:{
            title: function(items) {
              var idx = items[0].dataIndex;
              return 'Step ' + (idx+1) + ': Page ' + steps[idx].page;
            },
            label: function(item) {
              if (item.datasetIndex === 0) {
                return steps[item.dataIndex].fault
                  ? '\u25C6 PAGE FAULT — loaded from disk'
                  : '\u00B7 HIT — already in frame';
              }
              return 'Total faults so far: ' + item.parsed.y;
            },
            labelColor: function(item) {
              if (item.datasetIndex === 0) {
                var isFault = steps[item.dataIndex].fault;
                return { borderColor: isFault ? '#ef4444' : '#10b981', backgroundColor: isFault ? '#ef4444' : '#10b981' };
              }
              return { borderColor:'#2563eb', backgroundColor:'#2563eb' };
            }
          }
        }
      },
      scales:{
        x:Object.assign({}, CHART_AXIS, {title:{display:true,text:'Step (page reference)',color:'#204768',font:{family:CHART_FONT,size: 11}}}),
        y:{
          display:false,
          min:-0.5, max:1.2
        },
        y2:Object.assign({}, CHART_AXIS, {
          position:'right',
          title:{display:true,text:'Total Faults',color:'#204768',font:{family:CHART_FONT,size: 11}},
          beginAtZero:true,
          grid:{drawOnChartArea:false}
        })
      }
    }
  });
}


function runSim() {
  stopAuto();
  requestRealtimeRun({ showLoading: true, silent: false, force: true, resetStep: true });
}

function applyRealtimeRunPayload(payload, resetStep) {
  if (!payload || !payload.paging || !payload.paging.current) return;

  allResults = payload.paging;
  result = payload.paging.current;
  if (!result.steps || result.steps.length === 0) return;

  if (resetStep || curStep < 0) curStep = 0;
  else curStep = Math.min(curStep, result.steps.length - 1);

  hide('stepEmpty'); show('stepContent');
  hide('histEmpty'); show('histContent');
  renderHistory();
  renderStep(curStep);
  renderCharts();
  updateBtns();
}

function requestRealtimeRun(opts) {
  opts = opts || {};
  if (autoInt && !opts.force) return;

  var fc = getFC();
  var runBtn = document.querySelector('.bp');
  if (opts.showLoading && runBtn) {
    runBtn.innerHTML = '&#8987; Loading...';
    runBtn.disabled = true;
  }

  var useLive = $('liveToggle') && $('liveToggle').checked;
  var refEl = $('refIn');
  if (refEl) refEl.readOnly = useLive;

  var query =
    'frames=' + encodeURIComponent(fc) +
    '&algorithm=' + encodeURIComponent(window.ALGO) +
    '&max_belady_frames=10';
  if (useLive) {
    query += '&live=1&live_source=windows&window_size=12&max_page=9';
  } else {
    var refStr = refEl ? refEl.value.trim() : '';
    query += '&live=0' + (refStr ? '&reference_string=' + encodeURIComponent(refStr) : '');
  }

  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/api/realtime-algorithms?' + query, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      if (opts.showLoading && runBtn) {
        runBtn.innerHTML = '&#9654; Run';
        runBtn.disabled = false;
      }

      if (xhr.status === 200) {
        try {
          var payload = JSON.parse(xhr.responseText);
          if (payload.timestamp) applyRealtimeDateUI(payload.timestamp);
          if (payload.paging && payload.paging.meta && payload.paging.meta.reference_string) {
            $('refIn').value = payload.paging.meta.reference_string.join(',');
            if (payload.paging.meta.processes && payload.paging.meta.processes.length) {
              $('refIn').title = payload.paging.meta.processes
                .map(function(p) { return p.name + ' (' + p.pid + ')'; })
                .join(' | ');
              renderProcessSource(payload.paging.meta.processes);
            }
          }
          applyRealtimeRunPayload(payload, !!opts.resetStep);
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

function startRealtimeRunPolling() {
  if (realtimeRunInt) clearInterval(realtimeRunInt);
  realtimeRunInt = setInterval(function() {
    if (!autoInt) {
      requestRealtimeRun({ silent: true, resetStep: false });
    }
  }, 10000);
}

function stepFwd() {
  if (!result || curStep >= result.steps.length - 1) return;
  curStep++;
  renderStep(curStep);
  updateBtns();
}

function toggleAuto() { autoInt ? stopAuto() : startAuto(); }
function startAuto() {
  if (!result) return;
  autoInt = setInterval(function() {
    if (curStep >= result.steps.length - 1) { stopAuto(); return; }
    stepFwd();
  }, getSpd());
  updateBtns();
}
function stopAuto() {
  if (autoInt) { clearInterval(autoInt); autoInt = null; }
  updateBtns();
}

function resetSim() {
  stopAuto();
  result = null; allResults = null; curStep = -1;
  show('stepEmpty');  hide('stepContent');
  show('histEmpty');  hide('histContent');
  show('beladyEmpty'); hide('beladyWrap');
  show('timelineEmpty'); hide('timelineWrap');
  $('anomalyBadge').style.display = 'none';
  ['stAlgo','stF','stH','stR'].forEach(function(id) { $(id).textContent = '\u2014'; });
  if (cBelady) { cBelady.destroy(); cBelady = null; }
  if (cTimeline) { cTimeline.destroy(); cTimeline = null; }
  updateBtns();
  hide('procSrcPanel');
}

$('fcSlider').addEventListener('input', function() { $('fcDisp').textContent = this.value; });
$('refIn').addEventListener('keydown', function(e) { if (e.key === 'Enter') runSim(); });
$('fcSlider').addEventListener('change', scheduleRun);

function applyRealtimeDateUI(payload) {
  return;
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
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      try { applyRealtimeDateUI(JSON.parse(xhr.responseText)); } catch(e) {}
    }
  };
  xhr.send();
}

refreshRealtimeDate();
setInterval(refreshRealtimeDate, 30000);
requestRealtimeRun({ silent: true, force: true, resetStep: true });
startRealtimeRunPolling();
Chart.defaults.color = '#204768';
updateBtns();

function renderProcessSource(procs) {
  if (!procs || procs.length === 0) { hide('procSrcPanel'); return; }
  show('procSrcPanel');
  var psrcLabel = document.querySelector('.psrc-label');
  if (psrcLabel) {
    psrcLabel.textContent = 'Reference string generated from these real Windows processes:';
  }
  var html = '';
  for (var i = 0; i < procs.length; i++) {
    var p = procs[i];
    var memMB = p.mem_kb >= 1024*1024 ? (p.mem_kb/1024/1024).toFixed(1)+'GB' : Math.round(p.mem_kb/1024)+'MB';
    var volStr = p.volatility_label ? p.volatility_label : memMB;
    var pagesStr = p.pages ? p.pages.join(',') : (''+p.page);
    var pctStr = p.mem_pct ? ' ('+p.mem_pct+'% Activity)' : '';
    html += '<span class="proc-chip">' + p.name + ' <span class="pc-mem">' + volStr + pctStr + ' &rarr; Pages [' + pagesStr + ']</span></span>';
  }
  $('procSrcChips').innerHTML = html;
}
