from fastapi.responses import FileResponse
import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks
from utils import register_fonts, generate_pdf
from docx import Document

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# ---- 1. Register fonts at startup ----
register_fonts()

# ---- 2. FastAPI app & CORS ----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kdpformatter.com",
                   "http://localhost:3000"],  # Edit if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 3. Helper: Parse DOCX ----


def docx_to_text(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

# ---- 4. Helper: Remove PDF after 24h ----


def schedule_file_removal(file_path: str):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Could not delete file {file_path}: {e}")

# ---- 5. Main PDF formatting endpoint ----


@app.post("/format")
async def format_book(
    file: UploadFile = File(None),
    pasted_text: str = Form(None),
    heading_font: str = Form("Roboto-Regular"),
    body_font: str = Form("Roboto-Regular"),
    heading_size: int = Form(18),
    body_size: int = Form(12),
    trim_size: str = Form("6x9"),
    background_tasks: BackgroundTasks = None
):
    # Accept either file (.docx) or pasted_text
    manuscript_text = ""
    if file:
        # Save the uploaded docx to a temp path
        tmp_docx = f"/tmp/{uuid.uuid4()}.docx"
        with open(tmp_docx, "wb") as f:
            f.write(await file.read())
        manuscript_text = docx_to_text(tmp_docx)
        os.remove(tmp_docx)
    elif pasted_text:
        manuscript_text = pasted_text
    else:
        return JSONResponse({"error": "No manuscript provided."}, status_code=400)

    # Output PDF path
    output_id = uuid.uuid4()
    pdf_path = f"/tmp/{output_id}.pdf"
    generate_pdf(
        output_path=pdf_path,
        manuscript_text=manuscript_text,
        heading_font=heading_font,
        body_font=body_font,
        heading_size=heading_size,
        body_size=body_size,
        trim_size=trim_size,
    )

    # Upload to Supabase Storage (implement this as needed)
    # Example: pdf_url = upload_to_supabase(pdf_path, output_id)

    # For now, serve locally (for testing)
    download_url = f"/download/{output_id}"

    # Schedule file removal in 24h (not persistent! For prod, use cloud jobs)
    if background_tasks:
        background_tasks.add_task(schedule_file_removal, pdf_path)

    return JSONResponse({"pdf_url": download_url})

# ---- 6. Serve generated PDF for download (testing only, not for prod) ----


@app.get("/download/{pdf_id}")
def download_pdf(pdf_id: str):
    file_path = f"/tmp/{pdf_id}.pdf"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename="formatted-manuscript.pdf", media_type="application/pdf")
    return JSONResponse({"error": "File not found"}, status_code=404)
