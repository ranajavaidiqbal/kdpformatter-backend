import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from starlette.background import BackgroundTasks
from utils import register_fonts, generate_pdf, upload_pdf_to_supabase
from docx import Document

# ---- 1. Register fonts at startup ----
register_fonts()

# ---- 2. FastAPI app & CORS ----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kdpformatter.com",
                   "http://localhost:3000"],  # Add more as needed
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

# ---- 4. Main PDF formatting endpoint ----


@app.post("/format")
async def format_book(
    file: UploadFile = File(None),
    pasted_text: str = Form(None),
    heading_font: str = Form("Roboto-Regular"),
    body_font: str = Form("Roboto-Regular"),
    heading_size: float = Form(18.0),      # Accepts decimals!
    body_size: float = Form(12.0),         # Accepts decimals!
    trim_size: str = Form("6x9"),
    background_tasks: BackgroundTasks = None
):
    manuscript_text = ""
    if file:
        tmp_docx = f"/tmp/{uuid.uuid4()}.docx"
        with open(tmp_docx, "wb") as f:
            f.write(await file.read())
        manuscript_text = docx_to_text(tmp_docx)
        os.remove(tmp_docx)
    elif pasted_text:
        manuscript_text = pasted_text
    else:
        return JSONResponse({"error": "No manuscript provided."}, status_code=400)

    # Output PDF path and filename for supabase
    output_id = uuid.uuid4()
    pdf_filename = f"{output_id}.pdf"
    pdf_path = f"/tmp/{pdf_filename}"
    generate_pdf(
        output_path=pdf_path,
        manuscript_text=manuscript_text,
        heading_font=heading_font,
        body_font=body_font,
        heading_size=heading_size,
        body_size=body_size,
        trim_size=trim_size,
    )

    # ---- Upload to Supabase Storage ----
    try:
        pdf_url = upload_pdf_to_supabase(pdf_path, pdf_filename)
    except Exception as e:
        print(f"Error uploading PDF to Supabase: {e}")
        return JSONResponse({"error": "PDF upload failed"}, status_code=500)

    # (Optional) Delete local PDF file after upload
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return JSONResponse({"pdf_url": pdf_url})

# ---- 5. (Optional) Local file download endpoint for testing only ----


@app.get("/download/{pdf_id}")
def download_pdf(pdf_id: str):
    file_path = f"/tmp/{pdf_id}.pdf"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename="formatted-manuscript.pdf", media_type="application/pdf")
    return JSONResponse({"error": "File not found"}, status_code=404)
