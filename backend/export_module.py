# ============================================================
# Module 10 — Export Module
# Purpose: Export simulation results as CSV files or PDF reports
#          using the csv stdlib module and fpdf2.
# ============================================================

import csv
import io
from fpdf import FPDF


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_csv(steps, headers=None, title="simulation"):
    """
    Export a list of step dicts to a CSV byte string.

    Args:
        steps   (list[dict]): Simulation step data.
        headers (list[str]):  Column headers. If None, inferred from
                              the keys of the first step dict.
        title   (str):        Used for filename suggestion (not embedded).

    Returns:
        bytes: UTF-8 encoded CSV content.
    """
    if not steps:
        return b""

    if headers is None:
        headers = list(steps[0].keys())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()

    for step in steps:
        # Convert list values to comma-separated strings for CSV
        row = {}
        for key in headers:
            val = step.get(key, "")
            if isinstance(val, list):
                val = ", ".join(str(v) if v is not None else "—" for v in val)
            elif val is None:
                val = "—"
            row[key] = val
        writer.writerow(row)

    return output.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# PDF Export
# ---------------------------------------------------------------------------

class SimulationPDF(FPDF):
    """Custom PDF class with header/footer for simulation reports."""

    def __init__(self, report_title="Simulation Report"):
        super().__init__()
        self.report_title = report_title

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.report_title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def export_pdf(title, summary, steps, headers=None):
    """
    Export simulation results as a PDF report.

    Args:
        title   (str):        Report title.
        summary (dict):       Key-value summary statistics to display.
        steps   (list[dict]): Step-by-step data rows.
        headers (list[str]):  Column headers to include in the table.

    Returns:
        bytes: PDF file content.
    """
    pdf = SimulationPDF(report_title=title)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Summary Section ──────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    if summary:
        for key, value in summary.items():
            label = key.replace("_", " ").title()
            pdf.cell(60, 7, f"{label}:", new_x="RIGHT")
            pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # ── Step Table ──────────────────────────────────────────
    if steps:
        if headers is None:
            headers = list(steps[0].keys())

        # Filter out overly wide columns for readability
        display_headers = [h for h in headers if h not in ("frames_before", "frames_after", "action")]

        pdf.set_font("Helvetica", "B", 9)
        col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / max(len(display_headers), 1)

        # Header row
        for h in display_headers:
            label = h.replace("_", " ").title()
            pdf.cell(col_width, 7, label, border=1, align="C")
        pdf.ln()

        # Data rows
        pdf.set_font("Helvetica", "", 8)
        for step in steps:
            for h in display_headers:
                val = step.get(h, "")
                if isinstance(val, list):
                    val = ", ".join(str(v) if v is not None else "—" for v in val)
                elif val is None:
                    val = "—"
                elif isinstance(val, bool):
                    val = "Yes" if val else "No"
                pdf.cell(col_width, 6, str(val)[:15], border=1, align="C")
            pdf.ln()

    return pdf.output()
