# utils/styles.py

def get_heading_style(heading_font, heading_size):
    """
    Returns a style dict for headings.
    """
    return {
        "fontName": heading_font,
        "fontSize": heading_size,
        "leading": heading_size + 2,
        "spaceAfter": heading_size // 2,
        "spaceBefore": heading_size // 2,
        "bold": "Bold" in heading_font or "bold" in heading_font.lower(),
    }

def get_body_style(body_font, body_size):
    """
    Returns a style dict for body text.
    """
    return {
        "fontName": body_font,
        "fontSize": body_size,
        "leading": body_size + 2,
        "spaceAfter": body_size // 2,
        "spaceBefore": body_size // 2,
        "bold": False,
    }

def get_styles(heading_font, heading_size, body_font, body_size):
    """
    Returns a dict with both heading and body styles.
    """
    return {
        "heading": get_heading_style(heading_font, heading_size),
        "body": get_body_style(body_font, body_size),
    }
