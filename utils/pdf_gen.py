from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.lib.pagesizes import inch
from utils.docx_parse import parse_docx_to_story
from utils.styles import get_styles
from utils.margins import get_margin_tuple
from utils.toc import build_static_toc  # Make sure this import works!

def estimate_page_count(story, trim_size):
    """
    Estimate the number of pages for margin/gutter calculation.
    """
    words = 0
    for f in story:
        if hasattr(f, 'text'):
            words += len(f.text.split())
    if trim_size == '6x9':
        words_per_page = 350
    elif trim_size == '8.5x11':
        words_per_page = 600
    else:
        words_per_page = 350
    pages = max(1, int(words / words_per_page) + 1)
    return pages

def generate_pdf(
    output_path,
    manuscript_file_path,
    heading_font,
    body_font,
    heading_size,
    body_size,
    trim_size,
    bleed,
    generate_toc=False  # <-- new param, set by frontend
    **kwargs
):
    """
    Generate a KDP-ready PDF with conditional Table of Contents.
    """
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

    # Estimate page count for gutter calculation
    page_count = estimate_page_count(story, trim_size)
    left_margin, right_margin, top_margin, bottom_margin, gutter = get_margin_tuple(trim_size, page_count, bleed)

    # --- Conditional Table of Contents ---
    if generate_toc and headings and hasattr(headings, "__iter__"):
        toc = build_static_toc(headings, styles)
        story = toc + story  # Prepend TOC to the story

    # --- Build the PDF ---
    doc = SimpleDocTemplate(
        output_path,
        pagesize=(width, height),
        leftMargin=left_margin * inch,
        rightMargin=right_margin * inch,
        topMargin=top_margin * inch,
        bottomMargin=bottom_margin * inch,
        title="KDP Formatted Book",
        author=""
    )

    doc.build(story)
