var ALGO = 'Optimal';
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
  for (var p = 0; p < steps.length; p++) { allPagesFound[steps[p].page] = true; }
  var uniquePages = Object.keys(allPagesFound).sort(function(a,b){return parseInt(a)-parseInt(b)});
  
  var ptUI = $('pageTableUI');
  var bsUI = $('backingStoreUI');
  if (ptUI && bsUI) {
    var ptHtml = '';
    for (var k = 0; k < uniquePages.length; k++) {
        var pg = uniquePages[k];
        var isLoaded = s.frames.indexOf(parseFloat(pg)) !== -1 || s.frames.indexOf(String(pg)) !== -1 || s.frames.indexOf(+pg) !== -1;
        var vBit = isLoaded ? 'V' : 'I';
        var col = isLoaded ? '#10b981' : '#f43f5e';
        ptHtml += '<div style="border:1px solid '+col+';color:'+col+';padding:2px 4px;font-size:11px;border-radius:2px;">Pg ' + pg + ' : ' + vBit + '</div>';
    }
    ptUI.innerHTML = ptHtml;
    
    var bsHtml = '';
    for (var stepIdx = 0; stepIdx <= si; stepIdx++) {
       var st = steps[stepIdx];
       if (st.fault) {
           bsHtml += '<div style="color:#10b981;">Step '+(stepIdx+1)+': [SWAP-IN] Page '+st.page+' loaded from disk.</div>';
           if (st.evicted !== null && st.evicted !== undefined) {
               bsHtml += '<div style="color:#94a3b8;">Step '+(stepIdx+1)+': [SWAP-OUT] Page '+st.evicted+' evicted to disk.</div>';
           }
       }
    }
    if (bsHtml === '') bsHtml = '<div style="color:var(--text-dimmer)">No swaps yet...</div>';
    bsUI.innerHTML = bsHtml;
    bsUI.scrollTop = bsUI.scrollHeight;
  }
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

function renderCharts() {
  if (!allResults) return;

  if (cBelady) { cBelady.destroy(); cBelady = null; }
  if (cTimeline) { cTimeline.destroy(); cTimeline = null; }

  // Belady's anomaly chart
  var bel = allResults.belady;
  var anomalyFs = {};
  for (var a = 0; a < bel.anomaly_at.length; a++) { anomalyFs[bel.anomaly_at[a][1]] = true; }
  $('anomalyBadge').style.display = bel.anomaly_found ? '' : 'none';
  hide('beladyEmpty'); show('beladyWrap');

  var fLabels = Object.keys(bel.fault_counts).map(Number);
  var fData = [];
  var ptColors = [];
  var ptSizes = [];
  for (var i = 0; i < fLabels.length; i++) {
    fData.push(bel.fault_counts[fLabels[i]]);
    ptColors.push(anomalyFs[fLabels[i]] ? '#dc2626' : '#2563eb');
    ptSizes.push(anomalyFs[fLabels[i]] ? 7 : 3);
  }

  cBelady = new Chart($('beladyChart'), {
    type:'line',
    data:{
      labels:fLabels,
      datasets:[{
        label:'Faults', data:fData,
        borderColor:'#1d4ed8',
        backgroundColor:'rgba(37,99,235,.1)',
        pointBackgroundColor:ptColors,
        pointBorderColor:ptColors,
        pointRadius:ptSizes,
        tension:.2, borderWidth:2.2, fill:true
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{
        x:Object.assign({}, CHART_AXIS, {title:{display:true,text:'Frames',color:'#204768',font:{family:CHART_FONT,size: 11}}}),
        y:Object.assign({}, CHART_AXIS, {title:{display:true,text:'Faults',color:'#204768',font:{family:CHART_FONT,size: 11}}})
      }
    }
  });

  // Fault timeline chart
  hide('timelineEmpty'); show('timelineWrap');
  var cumData = [];
  var c = 0;
  for (var i = 0; i < result.steps.length; i++) {
    if (result.steps[i].fault) c++;
    cumData.push(c);
  }
  var stepLbls = [];
  for (var i = 0; i < result.steps.length; i++) { stepLbls.push(i + 1); }

  cTimeline = new Chart($('timelineChart'), {
    type:'line',
    data:{
      labels:stepLbls,
      datasets:[{
        label:'Cumulative Faults', data:cumData,
        borderColor:'#2563eb',
        backgroundColor:'rgba(37,99,235,.14)',
        pointRadius:3,
        pointBackgroundColor:'#1d4ed8',
        tension:0.08, borderWidth:2.2, fill:true
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{
        x:Object.assign({}, CHART_AXIS, {title:{display:true,text:'Step',color:'#204768',font:{family:CHART_FONT,size: 11}}}),
        y:Object.assign({}, CHART_AXIS, {title:{display:true,text:'Cumulative Faults',color:'#204768',font:{family:CHART_FONT,size: 11}}})
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
    '&algorithm=' + encodeURIComponent(ALGO) +
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
      } else if (!opts.silent) {
        alert('Error: ' + xhr.responseText);
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
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      applyRealtimeDateUI(JSON.parse(xhr.responseText));
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
