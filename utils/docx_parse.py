import os
from docx import Document
from reportlab.platypus import Paragraph, Spacer
from .bullets import parse_bullet_lists
from .tables import parse_tables
from .images import parse_images

def parse_docx_to_story(docx_path, styles):
    """
    Parses a DOCX file and returns (story, headings).
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

        para_style_name = para.style.name.lower()

        # Bullet/list/numbered
        if "list" in para_style_name or "bullet" in para_style_name or "number" in para_style_name:
            list_block = []
            while i < len(doc.paragraphs):
                para2 = doc.paragraphs[i]
                para2_style_name = para2.style.name.lower()
                if "list" in para2_style_name or "bullet" in para2_style_name or "number" in para2_style_name:
                    list_block.append(para2)
                    i += 1
                else:
                    break
            flowables = parse_bullet_lists(list_block, styles)
            # Defensive: ensure it's always a list of Flowables
            if isinstance(flowables, list):
                story.extend([f for f in flowables if hasattr(f, 'wrap')])
            i -= 1  # adjust for outer loop increment
        # Book title (first "Title" style paragraph)
        elif not title_found and para_style_name.startswith('title'):
            story.append(Paragraph(text, styles['heading']))
            story.append(Spacer(1, 18))
            title_found = True
        # Heading (for TOC)
        elif para.style.name.startswith('Heading') and not (
            "list" in para_style_name or "bullet" in para_style_name or "number" in para_style_name
        ):
            try:
                level = int(para.style.name.replace('Heading', '').strip() or "1")
            except Exception:
                level = 1
            headings.append((text, level))
            story.append(Paragraph(text, styles['heading']))
            story.append(Spacer(1, 12))
        else:
            # Inline formatting (bold/italic) support for body
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
            story.append(Paragraph(paragraph_text, styles['body']))
        story.append(Spacer(1, 6))
        i += 1

    # Add tables and images, but always check type
    tables = parse_tables(doc, styles)
    if isinstance(tables, list):
        story.extend([t for t in tables if hasattr(t, 'wrap')])

    images = parse_images(doc, styles)
    if isinstance(images, list):
        story.extend([img for img in images if hasattr(img, 'wrap')])

    return story, headings

def extract_book_title(docx_path):
    """Returns the first non-empty paragraph, or 'Untitled Book'."""
    doc = Document(docx_path)
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            return text
    return "Untitled Book"
