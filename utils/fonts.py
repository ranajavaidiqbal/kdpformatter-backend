import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_fonts():
    # Use this if fonts is in project root:
    fonts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts"))
    if not os.path.isdir(fonts_dir):
        print("⚠️ No fonts directory found.")
        return

    for filename in os.listdir(fonts_dir):
        if not (filename.lower().endswith(".ttf") or filename.lower().endswith(".otf")):
            continue
        font_name = filename.rsplit(".", 1)[0]
        # Remove weight suffix if present
        base_name = font_name
        for weight in ['100','200','300','400','500','600','700','800','900']:
            if base_name.endswith(f"-{weight}"):
                base_name = base_name[:-len(weight)-1]
                break

        font_path = os.path.join(fonts_dir, filename)
        try:
            pdfmetrics.registerFont(TTFont(base_name, font_path))
            print(f"✅ Registered font: {base_name}")
        except Exception as e:
            print(f"❌ Could not register font {base_name}: {e}")

if __name__ == "__main__":
    register_fonts()
