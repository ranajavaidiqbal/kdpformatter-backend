import io
from reportlab.platypus import Image, Spacer

def parse_images(doc, styles):
    """
    Extracts inline images from a docx.Document object and returns a list of
    ReportLab Image flowables (with spacers).
    Only images found in paragraphs are included (not headers/footers).
    """
    flowables = []
    # Access the underlying document for images
    for rel in doc.part._rels:
        rel = doc.part._rels[rel]
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            # ReportLab can handle PNG/JPEG, but .docx images may vary
            try:
                img = Image(io.BytesIO(image_data))
                # Optional: Set max width/height for KDP (in points)
                img._restrictSize(400, 600)
                flowables.append(Spacer(1, 12))
                flowables.append(img)
                flowables.append(Spacer(1, 12))
            except Exception as e:
                print(f"Failed to process image: {e}")
    return flowables
