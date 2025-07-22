from docx import Document as DocxDocument
from docx.table import _Cell, Table as DocxTable
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph as DocxParagraph
from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem, Table as RLTable, TableStyle, Flowable
from reportlab.lib import colors

def extract_book_title(docx_path):
    doc = DocxDocument(docx_path)
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading") and "1" in para.style.name and para.text.strip():
            return para.text.strip()
    for para in doc.paragraphs:
        if para.text.strip():
            return para.text.strip()
    return "Untitled Manuscript"

def is_bullet_paragraph(para):
    style = para.style.name if hasattr(para.style, 'name') else ""
    if "List" in style or "Bullet" in style or "Number" in style:
        return True
    try:
        if para._element.numPr is not None:
            return True
    except Exception:
        pass
    return False

class DropCapParagraph(Flowable):
    def __init__(self, first_letter, rest_text, style, dropcap_size=24):
        Flowable.__init__(self)
        self.first_letter = first_letter
        self.rest_text = rest_text
        self.style = style
        self.dropcap_size = dropcap_size

    def wrap(self, availWidth, availHeight):
        return availWidth, self.dropcap_size + 4

    def draw(self):
        self.canv.setFont(self.style.fontName, self.dropcap_size)
        self.canv.drawString(0, 0, self.first_letter)
        self.canv.setFont(self.style.fontName, self.style.fontSize)
        self.canv.drawString(self.dropcap_size * 0.6, 0, self.rest_text)

def iter_block_items(parent):
    from docx.document import Document as DocxDocumentType
    if isinstance(parent, DocxDocumentType):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        return
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield DocxParagraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield DocxTable(child, parent)

def parse_docx_to_story(docx_path, styles, body_font="Roboto-Regular",
                        heading_font="Roboto-Regular", body_font_size=12):
    doc = DocxDocument(docx_path)
    story, list_buffer, last_list_style, used_title = [], [], None, False

    def flush_list():
        nonlocal list_buffer, last_list_style
        if list_buffer:
            story.append(ListFlowable(list_buffer, bulletType='bullet', leftIndent=18))
            list_buffer, last_list_style = [], None

    book_title = extract_book_title(docx_path)

    for block in iter_block_items(doc):
        if isinstance(block, DocxParagraph):
            para, text = block, ""
            for run in para.runs:
                t = run.text.replace('\n', ' ')
                if not t:
                    continue
                if run.bold:
                    t = f"<b>{t}</b>"
                if run.italic:
                    t = f"<i>{t}</i>"
                if run.underline:
                    t = f"<u>{t}</u>"
                text += t
            style = para.style.name if hasattr(para.style, 'name') else ""
            if not used_title and text.strip() == book_title:
                used_title = True
                continue
            # You may comment this block to skip drop caps completely if you wish:
            # if "Drop Cap" in style:
            #     flush_list()
            #     if text.strip():
            #         first_letter, rest_text = text[0], text[1:]
            #         story.append(DropCapParagraph(first_letter, rest_text, styles["BookBody"], dropcap_size=body_font_size*2))
            #         story.append(Spacer(1, 6))
            #     continue
            if style.startswith('Heading'):
                flush_list()
                story += [Spacer(1, 14), Paragraph(text, styles["BookHeading"]), Spacer(1, 10)]
            elif is_bullet_paragraph(para):
                if last_list_style and style != last_list_style:
                    flush_list()
                list_buffer.append(ListItem(Paragraph(text, styles["BookBody"])))
                last_list_style = style
            elif not text.strip():
                flush_list()
                story.append(Spacer(1, 8))
            else:
                flush_list()
                story.append(Paragraph(text, styles["BookBody"]))
        elif isinstance(block, DocxTable):
            flush_list()
            data = [[cell.text for cell in row.cells] for row in block.rows]
            t = RLTable(data, hAlign='LEFT', style=TableStyle([
                ('FONTNAME', (0,0), (-1,-1), body_font),
                ('FONTSIZE', (0,0), (-1,-1), body_font_size),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ]))
            story += [Spacer(1, 8), t, Spacer(1, 8)]
    flush_list()
    return story
