import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "pdfs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_pdf(content, heading_font, body_font, heading_size, body_size, trim_size, path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont(heading_font, heading_size)
    c.drawString(100, 800, "Heading (sample)")
    c.setFont(body_font, body_size)
    c.drawString(100, 780, content.decode()[:500])  # Sample preview
    c.save()

def upload_to_supabase(filename, local_path):
    with open(local_path, "rb") as f:
        supabase.storage.from_(SUPABASE_BUCKET).upload(f"generated/{filename}", f, {"content-type": "application/pdf"})
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/generated/{filename}"
