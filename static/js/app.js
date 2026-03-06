/* ============================================================
   app.js — Minimal JavaScript
   - Sidebar toggle
   - Step-by-step animation
   - Preset loading via fetch
   - Dynamic form rows (segmentation)
   ============================================================ */

// ═══════════════════════════════════════════════════════════
// Sidebar Toggle
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');

    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Close sidebar on outside click (mobile)
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                e.target !== toggle) {
                sidebar.classList.remove('open');
            }
        });
    }
});


// ═══════════════════════════════════════════════════════════
// Step-by-Step Table Animation
// ═══════════════════════════════════════════════════════════

let animationTimers = {};

function animateTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    // Cancel any running animation on this table
    if (animationTimers[tableId]) {
        clearInterval(animationTimers[tableId]);
    }

    const rows = table.querySelectorAll('tbody .animate-row');

    // Hide all rows first
    rows.forEach(row => {
        row.classList.add('hidden-row');
        row.classList.remove('visible-row', 'highlight-row');
        row.style.display = 'none';
    });

    let currentIndex = 0;

    animationTimers[tableId] = setInterval(() => {
        if (currentIndex >= rows.length) {
            clearInterval(animationTimers[tableId]);
            animationTimers[tableId] = null;
            return;
        }

        // Remove highlight from previous row
        if (currentIndex > 0) {
            rows[currentIndex - 1].classList.remove('highlight-row');
        }

        // Show and highlight current row
        const row = rows[currentIndex];
        row.style.display = '';
        row.classList.remove('hidden-row');
        row.classList.add('visible-row', 'highlight-row');

        // Scroll into view
        row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        currentIndex++;
    }, 500);
}

function showAllRows(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    // Cancel animation
    if (animationTimers[tableId]) {
        clearInterval(animationTimers[tableId]);
        animationTimers[tableId] = null;
    }

    const rows = table.querySelectorAll('tbody .animate-row');
    rows.forEach(row => {
        row.style.display = '';
        row.classList.remove('hidden-row', 'highlight-row');
        row.classList.add('visible-row');
    });
}


// ═══════════════════════════════════════════════════════════
// Preset Loading
// ═══════════════════════════════════════════════════════════

function loadPreset(presetName) {
    fetch(`/api/preset/${presetName}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error('Preset error:', data.error);
                return;
            }

            // Map preset fields to form inputs
            const fieldMap = {
                reference_string: ['reference_string'],
                num_frames:       ['num_frames'],
                algorithm:        ['algorithm'],
                page_size:        ['page_size'],
                page_table:       ['page_table'],
                logical_addresses:['logical_addresses'],
                block_sizes:      ['block_sizes'],
                process_sizes:    ['process_sizes'],
                strategy:         ['strategy'],
            };

            for (const [key, ids] of Object.entries(fieldMap)) {
                if (data[key] !== undefined) {
                    ids.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) {
                            el.value = data[key];
                        }
                    });
                }
            }
        })
        .catch(err => console.error('Failed to load preset:', err));
}

// Special preset loader for segmentation (dynamic rows)
function loadPresetSegmentation(presetName) {
    fetch(`/api/preset/${presetName}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) return;

            // Populate segments
            if (data.segments) {
                const container = document.getElementById('segments-container');
                if (container) {
                    container.innerHTML = '';
                    data.segments.forEach((seg, i) => {
                        addSegmentRowWithData(i, seg.name, seg.base, seg.limit);
                    });
                    document.getElementById('seg_count').value = data.segments.length;
                }
            }

            // Populate requests
            if (data.requests) {
                const container = document.getElementById('requests-container');
                if (container) {
                    container.innerHTML = '';
                    data.requests.forEach((req, i) => {
                        addRequestRowWithData(i, req.segment, req.offset);
                    });
                    document.getElementById('req_count').value = data.requests.length;
                }
            }
        })
        .catch(err => console.error('Failed to load preset:', err));
}


// ═══════════════════════════════════════════════════════════
// Dynamic Form Rows (Segmentation)
// ═══════════════════════════════════════════════════════════

function addSegmentRow() {
    const container = document.getElementById('segments-container');
    if (!container) return;

    const index = container.children.length;
    addSegmentRowWithData(index, '', '', '');
    document.getElementById('seg_count').value = container.children.length;
}

function addSegmentRowWithData(index, name, base, limit) {
    const container = document.getElementById('segments-container');
    const row = document.createElement('div');
    row.className = 'dynamic-row';
    row.dataset.index = index;
    row.innerHTML = `
        <input type="text" name="seg_name_${index}" class="input input-sm" placeholder="Name" value="${name}">
        <input type="number" name="seg_base_${index}" class="input input-sm" placeholder="Base" value="${base}">
        <input type="number" name="seg_limit_${index}" class="input input-sm" placeholder="Limit" value="${limit}">
        <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">×</button>
    `;
    container.appendChild(row);
}

function addRequestRow() {
    const container = document.getElementById('requests-container');
    if (!container) return;

    const index = container.children.length;
    addRequestRowWithData(index, '', '');
    document.getElementById('req_count').value = container.children.length;
}

function addRequestRowWithData(index, segment, offset) {
    const container = document.getElementById('requests-container');
    const row = document.createElement('div');
    row.className = 'dynamic-row';
    row.dataset.index = index;
    row.innerHTML = `
        <input type="text" name="req_seg_${index}" class="input input-sm" placeholder="Segment" value="${segment}">
        <input type="number" name="req_offset_${index}" class="input input-sm" placeholder="Offset" value="${offset}">
        <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">×</button>
    `;
    container.appendChild(row);
}

function removeRow(button) {
    const row = button.closest('.dynamic-row');
    const container = row.parentElement;
    row.remove();

    // Re-index remaining rows
    const rows = container.querySelectorAll('.dynamic-row');
    rows.forEach((r, i) => {
        r.dataset.index = i;
        r.querySelectorAll('input').forEach(input => {
            const name = input.getAttribute('name');
            if (name) {
                // Replace the last number in the name with the new index
                input.setAttribute('name', name.replace(/_\d+$/, `_${i}`));
            }
        });
    });

    // Update count
    const isSegment = container.id === 'segments-container';
    const countEl = document.getElementById(isSegment ? 'seg_count' : 'req_count');
    if (countEl) {
        countEl.value = rows.length;
    }
}
