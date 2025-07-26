# utils/docx_parse.py

import os
from docx import Document
from reportlab.platypus import Paragraph, Spacer, Table as RLTable, TableStyle
from reportlab.lib.styles import ParagraphStyle

def parse_docx_to_story(docx_path, styles):
    """
    Parses a DOCX file and returns a list of ReportLab Flowables.
    Args:
        docx_path: Path to the DOCX file.
        styles: A dict or stylesheet containing ReportLab styles (BookHeading, BookBody, etc.)
    Returns:
        List of Flowables (Paragraphs, Tables, etc.)
    """
    doc = Document(docx_path)
    story = []
    title_found = False

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Title detection (first non-empty para, before any heading)
        if not title_found and para.style.name.lower().startswith('title'):
            story.append(Paragraph(text, styles['BookHeading']))
            story.append(Spacer(1, 18))
            title_found = True
            continue

        # Heading detection
        if para.style.name.startswith('Heading'):
            story.append(Paragraph(text, styles['BookHeading']))
            story.append(Spacer(1, 12))
        # Bullet or numbered list
        elif para.style.name.lower().startswith('list'):
            story.append(Paragraph(f"&bull; {text}", styles['BookBody']))
        # Body text (default)
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

    # Table handling (place all tables after paragraphs for now)
    for table in doc.tables:
        data = []
        for row in table.rows:
            data.append([cell.text.strip() for cell in row.cells])
        rl_table = RLTable(data)
        rl_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
        ]))
        story.append(Spacer(1, 12))
        story.append(rl_table)
        story.append(Spacer(1, 12))

    return story
