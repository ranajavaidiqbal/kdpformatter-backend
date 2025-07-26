from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.lib.pagesizes import inch
from utils.docx_parse import parse_docx_to_story
from utils.styles import get_styles
from utils.margins import get_margin_tuple
from utils.toc import build_static_toc
from utils.frontmatter import build_front_matter  # <--- new import!

TRIM_SIZE_MAP = {
    "6x9": (6 * inch, 9 * inch),
    "5x8": (5 * inch, 8 * inch),
    "5.06x7.81": (5.06 * inch, 7.81 * inch),
    "5.25x8": (5.25 * inch, 8 * inch),
    "5.5x8.5": (5.5 * inch, 8.5 * inch),
    "6.14x9.21": (6.14 * inch, 9.21 * inch),
    "6.69x9.61": (6.69 * inch, 9.61 * inch),
    "7x10": (7 * inch, 10 * inch),
    "7.44x9.69": (7.44 * inch, 9.69 * inch),
    "7.5x9.25": (7.5 * inch, 9.25 * inch),
    "8x10": (8 * inch, 10 * inch),
    "8.25x6": (8.25 * inch, 6 * inch),
    "8.25x8.25": (8.25 * inch, 8.25 * inch),
    "8.5x8.5": (8.5 * inch, 8.5 * inch),
    "8.5x11": (8.5 * inch, 11 * inch),
    "5.5x8.5 - Hardcover": (5.5 * inch, 8.5 * inch),
    "6x9 - Hardcover": (6 * inch, 9 * inch),
    "6.14x9.21 - Hardcover": (6.14 * inch, 9.21 * inch),
    "7x10 - Hardcover": (7 * inch, 10 * inch),
    "8.25x10.5 - Hardcover": (8.25 * inch, 10.5 * inch),
}

def clean_trim_size(ts):
    ts = ts.replace('"', '').replace("in", '').replace("(", '').replace(")", '')
    ts = ts.replace(' - Most Common', '').replace('Paperback & Hardcover', '')
    ts = ts.replace(' ', '').strip()
    ts = ts.replace('x ', 'x').replace(' x', 'x').replace('x', 'x')
    if 'cm' in ts:
        ts = ts.split('cm')[0]
        ts = ts.strip().replace('.', '')
    return ts

def estimate_page_count(story, trim_size):
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
    generate_toc=False,
    book_title="",            # New: from frontend
    book_subtitle="",         # New: from frontend
    author_name="",           # New: from frontend
    dedication="",            # New: from frontend
    copyright_notice="",      # New: from frontend
    **kwargs
):
    # --- TRIM SIZE LOGIC ---
    key = clean_trim_size(trim_size)
    width, height = TRIM_SIZE_MAP.get(key, (6 * inch, 9 * inch))

    # Get styles
    styles = get_styles(
        heading_font=heading_font,
        heading_size=heading_size,
        body_font=body_font,
        body_size=body_size
    )

    # --- Build front matter pages using new module ---
    front_matter_pages = build_front_matter(
        title=book_title,
        subtitle=book_subtitle,
        author=author_name,
        dedication=dedication,
        copyright_text=copyright_notice,
        heading_font=heading_font,
        body_font=body_font
    )

    # Parse manuscript
    story, headings = parse_docx_to_story(
        manuscript_file_path,
        styles
    )

    # Estimate page count for gutter calculation
    page_count = estimate_page_count(story, key)
    left_margin, right_margin, top_margin, bottom_margin, gutter = get_margin_tuple(key, page_count, bleed)

    # --- Conditional Table of Contents ---
    if generate_toc and headings and hasattr(headings, "__iter__"):
        toc = build_static_toc(headings, styles)
        story = toc + story

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(width, height),
        leftMargin=left_margin * inch,
        rightMargin=right_margin * inch,
        topMargin=top_margin * inch,
        bottomMargin=bottom_margin * inch,
        title="KDP Formatted Book",
        author=author_name or ""
    )

    full_story = front_matter_pages + story
    doc.build(full_story)
