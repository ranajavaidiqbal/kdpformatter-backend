import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table as RLTable, TableStyle
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from .fonts import register_fonts
from .margins import calculate_kdp_margins

def generate_pdf(
    output_path,
    manuscript_file_path,
    heading_font,
    body_font,
    heading_size,
    body_size,
    trim_size,
    bleed,
    gutter,
    page_count=None  # <-- allow page count to be passed in!
):
    # Register fonts (if not already done at startup)
    register_fonts()

    # Estimate page count if not provided (very rough)
    if page_count is None:
        with open(manuscript_file_path, 'rb') as f:
            word_count = len(f.read().decode(errors="ignore").split())
        page_count = max(1, word_count // 300)  # average 300 words/page

    # Get margins/gutter for KDP
    margins = calculate_kdp_margins(trim_size, page_count, bleed)
    left_margin = (margins['left'] + margins['gutter']) * inch
    right_margin = margins['right'] * inch
    top_margin = margins['top'] * inch
    bottom_margin = margins['bottom'] * inch

    # Define page size (support only common sizes here)
    page_sizes = {
        '6x9': (6 * inch, 9 * inch),
        '5x8': (5 * inch, 8 * inch)
        # Add more as needed
    }
    pagesize = page_sizes.get(trim_size, (6 * inch, 9 * inch))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=pagesize,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BookHeading',
                              fontName=heading_font,
                              fontSize=heading_size,
                              alignment=TA_CENTER,
                              spaceAfter=24,
                              spaceBefore=24))
    styles.add(ParagraphStyle(name='BookBody',
                              fontName=body_font,
                              fontSize=body_size,
                              alignment=TA_JUSTIFY,
                              spaceAfter=12))

    # Read manuscript and add basic content
    story = []

    # You should call your own docx_parse method here, which returns "parsed" paragraphs for headings, body, etc.
    # For example:
    from .docx_parse import parse_docx_to_story
    story += parse_docx_to_story(manuscript_file_path, styles=styles)

    doc.build(story)

    return output_path
