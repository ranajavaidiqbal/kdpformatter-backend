import re
from docx import Document
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem, Table as RLTable

def is_bullet_paragraph(paragraph):
    if paragraph.style.name.lower().startswith('list'):
        return True
    if hasattr(paragraph, "numbering_format") and paragraph.numbering_format is not None:
        return True
    bullet_like = re.compile(r'^[•\-\*\u2022]')
    if bullet_like.match(paragraph.text.strip()):
        return True
    return False

def get_heading_level(paragraph):
    if paragraph.style.name.startswith("Heading"):
        match = re.match(r"Heading (\d+)", paragraph.style.name)
        if match:
            return int(match.group(1))
    return None

def parse_docx_to_story(
    docx_path,
    styles,
    body_font="Roboto-Regular",
    heading_font="Roboto-Regular",
    body_font_size=12.0,
    heading_font_size=18.0,
):
    doc = Document(docx_path)
    story = []
    list_buffer = []
    last_list_type = None

    def flush_list():
        nonlocal list_buffer, last_list_type
        if list_buffer:
            story.append(ListFlowable(list_buffer, bulletType=last_list_type or 'bullet', leftIndent=18))
            list_buffer = []
            last_list_type = None

    for block in iter_block_items(doc):
        if isinstance(block, DocxParagraph):
            style = block.style.name

            # Detect heading level
            heading_level = get_heading_level(block)
            if heading_level:
                flush_list()
                style_name = f"BookHeading{heading_level}"
                heading_style = styles.get(style_name, styles.get("BookHeading1"))
                story += [Spacer(1, 14), Paragraph(extract_rich_text(block), heading_style), Spacer(1, 10)]
                continue

            # Bullet/numbered lists
            if is_bullet_paragraph(block):
                list_type = 'bullet'
                if block.text.strip() and re.match(r'^\d+[\.\)]', block.text.strip()):
                    list_type = '1'  # ReportLab uses '1' for numbered
                if last_list_type != list_type and list_buffer:
                    flush_list()
                last_list_type = list_type
                item = ListItem(Paragraph(extract_rich_text(block), styles["BookBody"]))
                list_buffer.append(item)
                continue

            # Blank lines
            if not block.text.strip():
                flush_list()
                story.append(Spacer(1, 12))
                continue

            # Regular paragraph
            flush_list()
            story.append(Paragraph(extract_rich_text(block), styles["BookBody"]))

        elif isinstance(block, DocxTable):
            flush_list()
            rl_table = RLTable([[cell.text for cell in row.cells] for row in block.rows])
            story.append(Spacer(1, 16))
            story.append(rl_table)
            story.append(Spacer(1, 12))

    flush_list()
    return story

def extract_rich_text(paragraph):
    rich_text = ""
    for run in paragraph.runs:
        run_text = run.text.replace('\n', ' ')
        if not run_text:
            continue
        if run.bold:
            run_text = f"<b>{run_text}</b>"
        if run.italic:
            run_text = f"<i>{run_text}</i>"
        if run.underline:
            run_text = f"<u>{run_text}</u>"
        rich_text += run_text
    return rich_text or paragraph.text

def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag.endswith('}p'):
            yield DocxParagraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield DocxTable(child, parent)

def extract_book_title(docx_path):
    doc = Document(docx_path)
    for para in doc.paragraphs:
        if para.style.name.lower() in ("title", "heading 1", "heading1"):
            if para.text.strip():
                return para.text.strip()
    for para in doc.paragraphs:
        if para.text.strip():
            return para.text.strip()
    return "Your Book Title"
