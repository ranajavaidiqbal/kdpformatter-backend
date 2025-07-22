import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from supabase import create_client, Client
from docx import Document

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "pdfs"

def register_fonts():
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    if not os.path.isdir(fonts_dir):
        print("⚠️ No fonts directory found.")
        return
    for filename in os.listdir(fonts_dir):
        if filename.lower().endswith(".ttf"):
            font_name = filename.rsplit(".", 1)[0]
            font_path = os.path.join(fonts_dir, filename)
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                print(f"✅ Registered font: {font_name}")
            except Exception as e:
                print(f"❌ Could not register font {font_name}: {e}")

def parse_docx_to_story(
    docx_path,
    styles,
    body_font="Roboto-Regular",
    heading_font="Roboto-Regular"
):
    doc = Document(docx_path)
    story = []
    list_buffer = []
    last_list_style = None

    def flush_list():
        nonlocal list_buffer, last_list_style
        if list_buffer:
            bullet_type = 'bullet' if last_list_style == 'ListBullet' else 'number'
            story.append(ListFlowable(
                list_buffer, 
                bulletType=bullet_type, 
                start='1' if bullet_type == 'number' else None,
                leftIndent=18
            ))
            list_buffer = []
            last_list_style = None

    for para in doc.paragraphs:
        text = ""
        # Compose text with inline formatting (HTML-style tags)
        for run in para.runs:
            t = run.text.replace('\n', ' ')
            if not t: continue
            if run.bold: t = f"<b>{t}</b>"
            if run.italic: t = f"<i>{t}</i>"
            if run.underline: t = f"<u>{t}</u>"
            text += t

        style = para.style.name if hasattr(para.style, 'name') else ""
        if style.startswith('Heading'):
            flush_list()
            story.append(Spacer(1, 14))
            story.append(Paragraph(text, styles["BookHeading"]))
            story.append(Spacer(1, 10))
        elif style in ("ListBullet", "List Number", "ListParagraph"):
            if last_list_style and style != last_list_style:
                flush_list()
            list_buffer.append(ListItem(Paragraph(text, styles["BookBody"])))
            last_list_style = style
        elif text.strip() == "":
            flush_list()
            story.append(Spacer(1, 8))
        else:
            flush_list()
            story.append(Paragraph(text, styles["BookBody"]))

    flush_list()
    return story

def generate_pdf(
    output_path: str,
    manuscript_file_path: str,   # Note: Now expects path to DOCX!
    heading_font: str = "Roboto-Regular",
    body_font: str = "Roboto-Regular",
    heading_size: float = 18.0,
    body_size: float = 12.0,
    trim_size: str = "6x9",
    bleed: bool = False,
    gutter: float = 0.25
):
    # --- KDP Trim Sizes ---
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

    story = []
    # --- Title Page (optional, could be improved) ---
    story.append(Spacer(1, height // 5))
    story.append(Paragraph("Your Book Title", styles["BookHeading"]))
    story.append(PageBreak())

    # --- Parse DOCX file to story (with formatting) ---
    story += parse_docx_to_story(manuscript_file_path, styles, body_font=body_font, heading_font=heading_font)

    # --- Page Numbers ---
    def add_page_number(canvas, doc):
        page_num_text = "%d" % (doc.page)
        canvas.saveState()
        canvas.setFont(body_font, 10)
        canvas.drawCentredString(width / 2.0, 0.5 * inch, page_num_text)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"✅ PDF generated at: {output_path}")

def upload_pdf_to_supabase(pdf_path, pdf_filename):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    with open(pdf_path, "rb") as f:
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(
            pdf_filename, f, {"content-type": "application/pdf", "upsert": "true"})
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{pdf_filename}"
    return public_url
