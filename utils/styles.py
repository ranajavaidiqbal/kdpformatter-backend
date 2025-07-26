from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import black, HexColor

def get_heading_style(heading_font, heading_size):
    return ParagraphStyle(
        name="Heading",
        fontName=heading_font,
        fontSize=heading_size,
        leading=heading_size + 2,
        alignment=TA_CENTER,
        textColor=black,
        spaceAfter=heading_size // 2,
        spaceBefore=heading_size // 2,
    )

def get_body_style(body_font, body_size):
    return ParagraphStyle(
        name="Body",
        fontName=body_font,
        fontSize=body_size,
        leading=body_size + 2,
        alignment=TA_JUSTIFY,
        textColor=black,
        spaceAfter=body_size // 2,
        spaceBefore=body_size // 2,
    )

def get_bullet_style(body_font, body_size):
    return ParagraphStyle(
        name="Bullet",
        fontName=body_font,
        fontSize=body_size,
        leading=body_size + 2,
        alignment=TA_LEFT,
        textColor=black,
        leftIndent=24,
        bulletIndent=12,
        spaceAfter=body_size // 2,
        spaceBefore=body_size // 2,
    )

def get_styles(heading_font, heading_size, body_font, body_size):
    """
    Returns a dict with ParagraphStyle objects for heading, body, and bullet.
    """
    return {
        "heading": get_heading_style(heading_font, heading_size),
        "body": get_body_style(body_font, body_size),
        "bullet": get_bullet_style(body_font, body_size),
    }
