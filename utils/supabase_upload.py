import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "pdfs"

def upload_pdf_to_supabase(pdf_path, pdf_filename):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    with open(pdf_path, "rb") as f:
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(
            pdf_filename, f, {"content-type": "application/pdf", "upsert": "true"})
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{pdf_filename}"
    return public_url
