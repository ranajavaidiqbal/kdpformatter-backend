import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from supabase import create_client, Client

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


def generate_pdf(
    output_path: str,
    manuscript_text: str,
    heading_font: str = "Roboto-Regular",
    body_font: str = "Roboto-Regular",
    heading_size: float = 18.0,
    body_size: float = 12.0,
    trim_size: str = "6x9",
    bleed: bool = False,
    # inches, default gutter (KDP typical is 0.25-0.375 for most books)
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

    # --- Margins (KDP typical: 0.75" outer/top/bottom, 0.25" inner/gutter) ---
    outer_margin = 0.75 * inch
    top_margin = 0.75 * inch
    bottom_margin = 0.75 * inch
    inner_margin = outer_margin + (gutter * inch)
    # Bleed: not used for now; set all to "no bleed" default

    # --- Setup Styles ---
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

    # --- Title Page (simple version) ---
    story.append(Spacer(1, height // 5))
    story.append(Paragraph("Your Book Title", styles["BookHeading"]))
    story.append(PageBreak())

    # --- Main Body ---
    for para in manuscript_text.split("\n"):
        para = para.strip()
        if not para:
            story.append(Spacer(1, body_size))
        else:
            story.append(Paragraph(para, styles["BookBody"]))

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
