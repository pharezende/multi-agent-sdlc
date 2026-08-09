from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def export_plan_to_pdf(
    text: str,
    output_path: Path,
) -> Path:
    if not text.strip():
        raise ValueError("PDF text cannot be empty.")

    output_path = output_path.with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    body_style = styles["BodyText"]

    elements = []

    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # ReportLab Paragraph interprets text as a limited XML-like format.
        safe_paragraph = (
            paragraph.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )

        elements.append(Paragraph(safe_paragraph, body_style))
        elements.append(Spacer(1, 4 * mm))

    document.build(elements)

    if not output_path.exists():
        raise RuntimeError("The PDF file was not created.")

    return output_path
