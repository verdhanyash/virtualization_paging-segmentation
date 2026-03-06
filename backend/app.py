# ============================================================
# Module 12 — Flask App & Routes
# Purpose: Central Flask application with routes for every
#          simulator tab, preset loading, and CSV/PDF export.
# ============================================================

import os
import sys
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, Response, jsonify,
)
from flask_cors import CORS

# ── Backend modules ──────────────────────────────────────────
from config import HOST, PORT, DEBUG
from utils import (
    validate_ref_string, validate_num_frames, validate_algorithm,
    validate_page_size, validate_page_table, validate_segments,
    validate_memory_blocks, validate_process_requests,
)
from lru import simulate_lru, lru_fault_curve
from optimal import simulate_optimal, optimal_fault_curve
from paging import run_paging_simulation
from segmentation import run_segmentation_simulation
from fragmentation import simulate_fragmentation, compare_strategies
from demand_paging import simulate_demand_paging
from chart_generator import (
    fault_comparison_bar, fault_curve_line, frame_heatmap,
    fragmentation_bar, fragmentation_comparison_bar, working_set_line,
)
from export_module import export_csv, export_pdf
from presets import get_preset, get_presets_for_tab

# ── App setup ────────────────────────────────────────────────
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")

app = Flask(
    __name__,
    template_folder=os.path.abspath(template_dir),
    static_folder=os.path.abspath(static_dir),
)
app.secret_key = "vm-sim-secret-key-2024"
CORS(app)


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Redirect to the page replacement tab."""
    return redirect(url_for("page_replacement"))


# ---------------------------------------------------------------------------
# Page Replacement (LRU / Optimal)
# ---------------------------------------------------------------------------

@app.route("/page-replacement", methods=["GET", "POST"])
def page_replacement():
    presets = get_presets_for_tab("page_replacement")
    context = {"presets": presets}

    if request.method == "POST":
        try:
            ref_str = request.form.get("reference_string", "")
            num_frames = request.form.get("num_frames", "3")
            algorithm = request.form.get("algorithm", "both")

            ref = validate_ref_string(ref_str)
            frames = validate_num_frames(num_frames)
            algo = validate_algorithm(algorithm)

            lru_result = None
            opt_result = None
            charts = {}

            if algo in ("lru", "both"):
                lru_result = simulate_lru(ref, frames)
            if algo in ("optimal", "both"):
                opt_result = simulate_optimal(ref, frames)

            # Charts
            if lru_result and opt_result:
                charts["comparison_bar"] = fault_comparison_bar(
                    lru_result["total_faults"], opt_result["total_faults"],
                    lru_result["total_hits"], opt_result["total_hits"],
                )
                lru_curve = lru_fault_curve(ref)
                opt_curve = optimal_fault_curve(ref)
                charts["fault_curve"] = fault_curve_line(lru_curve, opt_curve)
            elif lru_result:
                lru_curve = lru_fault_curve(ref)
                charts["fault_curve"] = fault_curve_line(lru_curve)

            if lru_result:
                charts["lru_heatmap"] = frame_heatmap(lru_result["steps"], frames)
            if opt_result:
                charts["opt_heatmap"] = frame_heatmap(opt_result["steps"], frames)

            context.update({
                "lru_result":       lru_result,
                "opt_result":       opt_result,
                "charts":           charts,
                "input_ref":        ref_str,
                "input_frames":     num_frames,
                "input_algorithm":  algorithm,
            })

        except ValueError as e:
            flash(str(e), "error")

    return render_template("page_replacement.html", **context)


# ---------------------------------------------------------------------------
# Paging (Address Translation)
# ---------------------------------------------------------------------------

@app.route("/paging", methods=["GET", "POST"])
def paging():
    presets = get_presets_for_tab("paging")
    context = {"presets": presets}

    if request.method == "POST":
        try:
            page_size_str = request.form.get("page_size", "512")
            pt_str = request.form.get("page_table", "")
            addr_str = request.form.get("logical_addresses", "")

            page_size = validate_page_size(page_size_str)

            # Parse page table from "0:5, 1:6, 2:1" format
            pt_entries = {}
            for entry in pt_str.replace(",", " ").split():
                entry = entry.strip()
                if ":" in entry:
                    parts = entry.split(":")
                    pt_entries[int(parts[0])] = int(parts[1])
            page_table = validate_page_table(pt_entries)

            # Parse addresses
            addresses = [int(a.strip()) for a in addr_str.replace(",", " ").split() if a.strip()]

            result = run_paging_simulation(addresses, page_size, page_table)

            context.update({
                "result":         result,
                "input_page_size": page_size_str,
                "input_pt":       pt_str,
                "input_addrs":    addr_str,
            })

        except ValueError as e:
            flash(str(e), "error")

    return render_template("paging.html", **context)


# ---------------------------------------------------------------------------
# Segmentation
# ---------------------------------------------------------------------------

@app.route("/segmentation", methods=["GET", "POST"])
def segmentation():
    presets = get_presets_for_tab("segmentation")
    context = {"presets": presets}

    if request.method == "POST":
        try:
            # Parse segments from form
            seg_count = int(request.form.get("seg_count", "0"))
            segments = []
            for i in range(seg_count):
                name = request.form.get(f"seg_name_{i}", "").strip()
                base = request.form.get(f"seg_base_{i}", "0")
                limit = request.form.get(f"seg_limit_{i}", "0")
                if name:
                    segments.append({"name": name, "base": int(base), "limit": int(limit)})

            # Parse requests from form
            req_count = int(request.form.get("req_count", "0"))
            requests_list = []
            for i in range(req_count):
                seg = request.form.get(f"req_seg_{i}", "").strip()
                offset = request.form.get(f"req_offset_{i}", "0")
                if seg:
                    requests_list.append({"segment": seg, "offset": int(offset)})

            result = run_segmentation_simulation(requests_list, segments)

            context.update({
                "result":   result,
                "segments": segments,
                "requests": requests_list,
            })

        except ValueError as e:
            flash(str(e), "error")

    return render_template("segmentation.html", **context)


# ---------------------------------------------------------------------------
# Fragmentation
# ---------------------------------------------------------------------------

@app.route("/fragmentation", methods=["GET", "POST"])
def fragmentation():
    presets = get_presets_for_tab("fragmentation")
    context = {"presets": presets}

    if request.method == "POST":
        try:
            blocks_str = request.form.get("block_sizes", "")
            procs_str = request.form.get("process_sizes", "")
            strategy = request.form.get("strategy", "first_fit")

            blocks = validate_memory_blocks(
                [int(b.strip()) for b in blocks_str.replace(",", " ").split() if b.strip()]
            )
            procs = validate_process_requests(
                [int(p.strip()) for p in procs_str.replace(",", " ").split() if p.strip()]
            )

            charts = {}

            if strategy == "all":
                comparison = compare_strategies(blocks, procs)
                charts["comparison"] = fragmentation_comparison_bar(comparison)
                # Also show individual results
                for strat_name, strat_result in comparison.items():
                    charts[f"bar_{strat_name}"] = fragmentation_bar(strat_result)
                context.update({
                    "comparison": comparison,
                    "charts":    charts,
                })
            else:
                result = simulate_fragmentation(blocks, procs, strategy)
                charts["bar"] = fragmentation_bar(result)
                context.update({
                    "result": result,
                    "charts": charts,
                })

            context.update({
                "input_blocks":   blocks_str,
                "input_procs":    procs_str,
                "input_strategy": strategy,
            })

        except ValueError as e:
            flash(str(e), "error")

    return render_template("fragmentation.html", **context)


# ---------------------------------------------------------------------------
# Demand Paging
# ---------------------------------------------------------------------------

@app.route("/demand-paging", methods=["GET", "POST"])
def demand_paging():
    presets = get_presets_for_tab("demand_paging")
    context = {"presets": presets}

    if request.method == "POST":
        try:
            ref_str = request.form.get("reference_string", "")
            num_frames = request.form.get("num_frames", "3")

            ref = validate_ref_string(ref_str)
            frames = validate_num_frames(num_frames)

            result = simulate_demand_paging(ref, frames)

            charts = {
                "working_set": working_set_line(result["steps"]),
                "heatmap":     frame_heatmap(result["steps"], frames),
            }

            context.update({
                "result":       result,
                "charts":       charts,
                "input_ref":    ref_str,
                "input_frames": num_frames,
            })

        except ValueError as e:
            flash(str(e), "error")

    return render_template("demand_paging.html", **context)


# ---------------------------------------------------------------------------
# Export Routes
# ---------------------------------------------------------------------------

@app.route("/export/csv", methods=["POST"])
def export_csv_route():
    """Export last simulation results as CSV."""
    try:
        data = request.get_json(force=True)
        steps = data.get("steps", [])
        title = data.get("title", "simulation")

        csv_bytes = export_csv(steps, title=title)

        return Response(
            csv_bytes,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={title}.csv"},
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/export/pdf", methods=["POST"])
def export_pdf_route():
    """Export last simulation results as PDF report."""
    try:
        data = request.get_json(force=True)
        steps = data.get("steps", [])
        title = data.get("title", "Simulation Report")
        summary = data.get("summary", {})

        pdf_bytes = export_pdf(title, summary, steps)

        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={title}.pdf"},
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------------------------------------------------------------------------
# Preset API
# ---------------------------------------------------------------------------

@app.route("/api/preset/<name>")
def api_preset(name):
    """Return preset data as JSON for client-side form population."""
    try:
        preset = get_preset(name)
        return jsonify(preset)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
