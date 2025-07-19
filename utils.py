import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import inch


def register_fonts():
    """
    Automatically register all .ttf fonts in the ./fonts directory.
    The font name will be the file name without extension (e.g. Roboto-Regular).
    """
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
    """
    Generates a PDF file at output_path with given formatting options.
    """
    # KDP trim size mapping (in inches)
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
    y = height - inch * 1  # 1 inch margin from top
    c.setFont(heading_font, heading_size)
    c.drawString(inch, y, "Your Book Title")  # You can customize this

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

# Example usage:
# register_fonts()
# generate_pdf("output.pdf", "Hello world\nThis is a test.", heading_font="Lora-Regular", body_font="Roboto-Regular")
