from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.lib.pagesizes import inch
from utils.docx_parse import parse_docx_to_story
from utils.styles import get_styles

def generate_pdf(
    output_path,
    manuscript_file_path,
    heading_font,
    body_font,
    heading_size,
    body_size,
    trim_size,
    bleed,
    gutter=0.25
):
    # Set up page size
    width, height = {
        "6x9": (6 * inch, 9 * inch),
        "5x8": (5 * inch, 8 * inch),
        "8.5x11": (8.5 * inch, 11 * inch),
        # Add more as needed
    }.get(trim_size, (6 * inch, 9 * inch))

    # Get styles from the central styles.py
    styles = get_styles(
        heading_font=heading_font,
        heading_size=heading_size,
        body_font=body_font,
        body_size=body_size
    )

    # Parse manuscript
    story, headings = parse_docx_to_story(
        manuscript_file_path,
        styles
    )

    # Generate PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=(width, height),
        leftMargin=0.75 * inch + (gutter * inch if not bleed else 0),
        rightMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
        title="KDP Formatted Book",
        author=""
    )

    doc.build(story)
