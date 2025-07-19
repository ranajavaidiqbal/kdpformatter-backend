import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import inch

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "pdfs"  # make sure this matches your bucket!


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
    heading_size: int = 18,
    body_size: int = 12,
    trim_size: str = "6x9"
):
    trim_sizes = {
        "5x8": (5 * inch, 8 * inch),
        "5.5x8.5": (5.5 * inch, 8.5 * inch),
        "6x9": (6 * inch, 9 * inch),
        "7x10": (7 * inch, 10 * inch),
        "8.5x11": (8.5 * inch, 11 * inch),
    }
    page_size = trim_sizes.get(trim_size, (6 * inch, 9 * inch))

    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size

    # Draw heading
    y = height - inch * 1
    c.setFont(heading_font, heading_size)
    c.drawString(inch, y, "Your Book Title")

    # Draw body text
    y -= heading_size + 0.3 * inch
    c.setFont(body_font, body_size)
    for line in manuscript_text.split("\n"):
        if y < inch:
            c.showPage()
            y = height - inch
            c.setFont(body_font, body_size)
        c.drawString(inch, y, line.strip())
        y -= body_size + 2

    c.save()
    print(f"✅ PDF generated at: {output_path}")


def upload_pdf_to_supabase(pdf_path, pdf_filename):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    with open(pdf_path, "rb") as f:
        # Overwrite if exists: upsert True
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(
            pdf_filename, f, {"content-type": "application/pdf", "upsert": True})
    # Build public URL for file
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{pdf_filename}"
    return public_url
