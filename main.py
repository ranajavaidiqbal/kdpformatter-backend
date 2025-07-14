from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils import generate_pdf, upload_to_supabase
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kdpformatter.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/format")
async def format_book(
    file: UploadFile = File(None),
    pasted_text: str = Form(None),
    heading_font: str = Form(...),
    body_font: str = Form(...),
    heading_size: float = Form(...),
    body_size: float = Form(...),
    trim_size: str = Form(...),
):
    content = await file.read() if file else pasted_text.encode()

    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = f"/tmp/{pdf_filename}"

    generate_pdf(content, heading_font, body_font,
                 heading_size, body_size, trim_size, pdf_path)

    pdf_url = upload_to_supabase(pdf_filename, pdf_path)

    return JSONResponse({"pdf_url": pdf_url})
