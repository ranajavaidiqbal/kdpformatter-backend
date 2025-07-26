from utils import (
    register_fonts,
    generate_pdf,
    upload_pdf_to_supabase
)
import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils import (
    register_fonts,
    generate_pdf,
    upload_pdf_to_supabase
)

app = FastAPI()

# Set CORS for your frontend domain
origins = [
    "https://kdpformatter.com",
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all fonts at startup
@app.on_event("startup")
def startup_event():
    register_fonts()

@app.post("/format")
async def format_book(
    file: UploadFile = File(...),
    heading_font: str = Form("Roboto-Regular"),
    body_font: str = Form("Roboto-Regular"),
    heading_size: float = Form(18.0),
    body_size: float = Form(12.0),
    trim_size: str = Form("6x9"),
    bleed: bool = Form(False)
):
    try:
        # Save uploaded file to a temp location
        temp_dir = "tmp"
        os.makedirs(temp_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[-1].lower()
        if file_ext != ".docx":
            return JSONResponse({"error": "Only .docx files are supported."}, status_code=400)
        docx_path = os.path.join(temp_dir, f"{uuid.uuid4()}.docx")
        with open(docx_path, "wb") as f:
            f.write(await file.read())

        # Output PDF path
        pdf_filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)

        # Generate PDF with formatted content
        generate_pdf(
            output_path=pdf_path,
            manuscript_file_path=docx_path,
            heading_font=heading_font,
            body_font=body_font,
            heading_size=heading_size,
            body_size=body_size,
            trim_size=trim_size,
            bleed=bleed
            
        )

        # Upload PDF to Supabase and get URL
        pdf_url = upload_pdf_to_supabase(pdf_path, pdf_filename)
        return {"pdf_url": pdf_url}

    except Exception as e:
        print("Error:", e)
        return JSONResponse({"error": f"Formatting failed: {e}"}, status_code=500)
