# utils/headings.py

from reportlab.platypus import Paragraph, Spacer

def map_heading_style(level, styles):
    """
    Returns the appropriate heading style object for the given heading level.
    Currently uses 'heading' for all, but you can expand for H2, H3, etc.
    """
    return styles.get('heading', None)

def process_heading(text, level, styles):
    """
    Creates a Paragraph for the heading, with spacing based on level.
    """
    style = map_heading_style(level, styles)
    if not style:
        raise ValueError("Heading style not found in styles dict.")
    # More spacing for top-level headings, less for sub-headings
    spacing = max(18 - (level-1)*4, 8)
    return [
        Paragraph(text, style),
        Spacer(1, spacing)
    ]
