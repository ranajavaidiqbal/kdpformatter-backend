from reportlab.platypus import Paragraph, PageBreak
from reportlab.lib.styles import ParagraphStyle

def get_title_style(heading_font):
    return ParagraphStyle(
        "TitleStyle",
        fontName=heading_font,
        fontSize=44,
        alignment=1,
        spaceAfter=40,
        spaceBefore=180,
        leading=52,
    )

def get_subtitle_style(heading_font):
    return ParagraphStyle(
        "SubtitleStyle",
        fontName=heading_font,
        fontSize=24,
        alignment=1,
        spaceAfter=20,
        spaceBefore=5,
        leading=28,
    )

def get_author_style(heading_font):
    return ParagraphStyle(
        "AuthorStyle",
        fontName=heading_font,
        fontSize=22,
        alignment=1,
        spaceAfter=40,
        spaceBefore=30,
        leading=28,
    )

def get_dedication_style(body_font):
    return ParagraphStyle(
        "DedicationStyle",
        fontName=body_font,
        fontSize=18,
        alignment=1,
        italic=True,
        spaceBefore=180,
        spaceAfter=120,
        leading=26,
    )

def get_copyright_style(body_font):
    return ParagraphStyle(
        "CopyrightStyle",
        fontName=body_font,
        fontSize=12,
        alignment=1,
        spaceBefore=220,
        spaceAfter=100,
        leading=18,
    )

def build_front_matter(
    title, subtitle, author, dedication, copyright_text,
    heading_font, body_font
):
    pages = []

    # Title Page
    if title:
        page = []
        title_paragraph = Paragraph(title, get_title_style(heading_font))
        page.append(title_paragraph)
        if subtitle:
            subtitle_paragraph = Paragraph(subtitle, get_subtitle_style(heading_font))
            page.append(subtitle_paragraph)
        if author:
            author_paragraph = Paragraph(f"by {author}", get_author_style(heading_font))
            page.append(author_paragraph)
        pages += page + [PageBreak()]

    # Dedication Page
    if dedication:
        dedication_paragraph = Paragraph(dedication, get_dedication_style(body_font))
        pages += [dedication_paragraph, PageBreak()]

    # Copyright Page
    if copyright_text:
        copyright_paragraph = Paragraph(copyright_text, get_copyright_style(body_font))
        pages += [copyright_paragraph, PageBreak()]

    return pages
