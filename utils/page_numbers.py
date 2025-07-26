# utils/page_numbers.py

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def add_page_numbers(canvas_obj, doc, style="normal", skip_first_n=0):
    """
    Adds page numbers to the PDF.
    Args:
        canvas_obj: The reportlab canvas object.
        doc: The SimpleDocTemplate (or similar).
        style: "normal", "roman", etc. (future expansion).
        skip_first_n: Skip numbering on the first N pages.
    """
    page_num = canvas_obj.getPageNumber()
    if page_num > skip_first_n:
        text = str(page_num)
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawCentredString(
            0.5 * (doc.leftMargin + doc.pagesize[0] - doc.rightMargin),
            0.5 * inch,
            text
        )
