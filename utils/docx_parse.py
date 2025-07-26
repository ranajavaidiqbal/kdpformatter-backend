import os
from docx import Document
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from .bullets import parse_bullet_lists
from .tables import parse_tables
from .images import parse_images  # NEW IMPORT

def parse_docx_to_story(docx_path, styles):
    """
    Parses a DOCX file and returns a tuple:
      (story, headings)
    - story: List of ReportLab Flowables (Paragraphs, Tables, Images, etc.)
    - headings: List of (heading_text, heading_level)
    """
    doc = Document(docx_path)
    story = []
    headings = []
    title_found = False

    i = 0
    while i < len(doc.paragraphs):
        para = doc.paragraphs[i]
        text = para.text.strip()
        if not text:
            i += 1
            continue

        para_style = para.style.name.lower()

        # Block of contiguous list/bullet/numbered paragraphs
        if "list" in para_style or "bullet" in para_style or "number" in para_style:
            list_block = []
            while i < len(doc.paragraphs):
                para2 = doc.paragraphs[i]
                para2_style = para2.style.name.lower()
                if "list" in para2_style or "bullet" in para2_style or "number" in para2_style:
                    list_block.append(para2)
                    i += 1
                else:
                    break
            story.extend(parse_bullet_lists(list_block, styles))
            continue  # already incremented i

        # Title detection (first non-empty para, before any heading)
        if not title_found and para_style.startswith('title'):
            story.append(Paragraph(text, styles['BookHeading']))
            story.append(Spacer(1, 18))
            title_found = True
            i += 1
            continue

        # Heading detection (for TOC)
        if para.style.name.startswith('Heading') and not (
            "list" in para_style or "bullet" in para_style or "number" in para_style
        ):
            try:
                level = int(para.style.name.replace('Heading', '').strip() or "1")
            except Exception:
                level = 1
            headings.append((text, level))
            story.append(Paragraph(text, styles['BookHeading']))
            story.append(Spacer(1, 12))
        else:
            # Inline formatting (bold/italic) support
            run_fragments = []
            for run in para.runs:
                run_text = run.text.replace('\n', '')
                if not run_text:
                    continue
                if run.bold and run.italic:
                    run_fragments.append(f'<b><i>{run_text}</i></b>')
                elif run.bold:
                    run_fragments.append(f'<b>{run_text}</b>')
                elif run.italic:
                    run_fragments.append(f'<i>{run_text}</i>')
                else:
                    run_fragments.append(run_text)
            paragraph_text = ''.join(run_fragments)
            story.append(Paragraph(paragraph_text, styles['BookBody']))
        story.append(Spacer(1, 6))
        i += 1

    # Table handling (now modularized)
    story.extend(parse_tables(doc, styles))

    # Image handling (now modularized)
    story.extend(parse_images(doc, styles))

    return story, headings

def extract_book_title(docx_path):
    """Returns the first non-empty paragraph, or 'Untitled Book'."""
    doc = Document(docx_path)
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            return text
    return "Untitled Book"
