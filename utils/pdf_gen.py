from reportlab.platypus import SimpleDocTemplate, ParagraphStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from .docx_parse import parse_docx_to_story, extract_book_title

def generate_pdf(
    output_path: str,
    manuscript_file_path: str,
    heading_font: str = "Roboto-Regular",
    body_font: str = "Roboto-Regular",
    heading_size: float = 18.0,
    body_size: float = 12.0,
    trim_size: str = "6x9",
    bleed: bool = False,
    gutter: float = 0.25
):
    trim_sizes = {
        "5x8": (5 * inch, 8 * inch),
        "5.5x8.5": (5.5 * inch, 8.5 * inch),
        "6x9": (6 * inch, 9 * inch),
        "7x10": (7 * inch, 10 * inch),
        "8.5x11": (8.5 * inch, 11 * inch),
    }
    page_size = trim_sizes.get(trim_size, (6 * inch, 9 * inch))
    width, height = page_size

    outer_margin = 0.75 * inch
    top_margin = 0.75 * inch
    bottom_margin = 0.75 * inch
    inner_margin = outer_margin + (gutter * inch)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="BookBody",
        fontName=body_font,
        fontSize=body_size,
        leading=body_size * 1.3,
        alignment=TA_JUSTIFY,
        firstLineIndent=body_size * 1.3,
        spaceAfter=body_size * 0.7,
    ))
    styles.add(ParagraphStyle(
        name="BookHeading",
        fontName=heading_font,
        fontSize=heading_size,
        alignment=TA_CENTER,
        spaceAfter=body_size * 1.2,
        leading=heading_size * 1.15,
    ))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(width, height),
        leftMargin=inner_margin,
        rightMargin=outer_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )

    book_title = extract_book_title(manuscript_file_path)
    story = []
    story.append(Spacer(1, height // 5))
    story.append(Paragraph(book_title, styles["BookHeading"]))
    story.append(PageBreak())

    story += parse_docx_to_story(
        manuscript_file_path, styles,
        body_font=body_font,
        heading_font=heading_font,
        body_font_size=body_size
    )

    def add_page_number(canvas, doc):
        page_num_text = "%d" % (doc.page)
        canvas.saveState()
        canvas.setFont(body_font, 10)
        canvas.drawCentredString(width / 2.0, 0.5 * inch, page_num_text)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"✅ PDF generated at: {output_path}")
