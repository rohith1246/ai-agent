import re
import io
from datetime import datetime
from fpdf import FPDF


class ResearchPDF(FPDF):
    def __init__(self, topic: str):
        super().__init__()
        self.topic = topic
        self.set_margins(20, 22, 20)
        self.set_auto_page_break(auto=True, margin=22)

    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(160, 110, 10)
        self.cell(0, 5, "AI RESEARCH AGENT  \u00b7  ROHITH BUILDS LABS", align="L")
        self.ln(4)
        self.set_draw_color(210, 210, 210)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        date_str = datetime.now().strftime("%B %d, %Y")
        self.cell(
            0, 8,
            f"Generated {date_str}  \u00b7  Page {self.page_no()}  \u00b7  rohith-builds-labs.onrender.com",
            align="C",
        )


def _safe(text: str) -> str:
    """Encode text safely for FPDF core fonts (latin-1)."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf(topic: str, report_text: str, sources: list = None) -> bytes:
    """Convert a report string into a branded PDF. Returns raw bytes."""
    pdf = ResearchPDF(topic)
    pdf.add_page()

    # ── Title block ──────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 11, _safe(topic.title()), align="L")
    pdf.ln(1)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"Research Report  \u00b7  {datetime.now().strftime('%B %d, %Y')}", align="L")
    pdf.ln(8)

    pdf.set_draw_color(210, 210, 210)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)

    # ── Report body ──────────────────────────────────────────────
    for line in report_text.split("\n"):
        stripped = line.strip()

        if not stripped:
            pdf.ln(2)
            continue

        if stripped.startswith("## "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(160, 110, 10)
            pdf.multi_cell(0, 7, _safe(stripped[3:]), align="L")
            pdf.ln(1)

        elif stripped.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 6, _safe(stripped[4:]), align="L")

        elif stripped.startswith(("- ", "\u2022 ")):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 6, _safe("\u2022  " + stripped[2:]), align="L")

        else:
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 6, _safe(clean), align="L")

    # ── Sources ──────────────────────────────────────────────────
    if sources:
        pdf.ln(8)
        pdf.set_draw_color(210, 210, 210)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(6)

        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(160, 110, 10)
        pdf.cell(0, 7, "Sources", align="L")
        pdf.ln(9)

        for i, src in enumerate(sources[:8], 1):
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 5, _safe(f"{i}. {src['title']}"), align="L")

            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(60, 100, 180)
            pdf.multi_cell(0, 5, _safe(src["url"]), align="L")
            pdf.ln(3)

    return bytes(pdf.output())