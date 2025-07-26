# utils/bullets.py

from reportlab.platypus import ListFlowable, ListItem, Paragraph
from reportlab.lib.styles import ParagraphStyle

def group_lists(docx_paragraphs):
    """
    Groups consecutive docx paragraphs that are part of a (possibly nested) list.
    Returns: List of ("list", list_items, level) or ("para", paragraph, 0) tuples.
    """
    blocks = []
    buffer = []
    prev_level = None

    for para in docx_paragraphs:
        style = para.style.name.lower()
        if "list" in style or "bullet" in style or "number" in style:
            # Detect level from style, e.g., "List Bullet 2"
            level = 1
            for token in style.split():
                if token.isdigit():
                    level = int(token)
            buffer.append((para, level))
            prev_level = level
        else:
            if buffer:
                blocks.append(("list", buffer.copy()))
                buffer.clear()
            blocks.append(("para", para))
    if buffer:
        blocks.append(("list", buffer.copy()))
    return blocks

def make_list_flowable(list_items, styles, ordered=False):
    """
    Creates a nested ListFlowable from list_items.
    list_items: List of (Paragraph, level)
    """
    # Recursive function to build nested lists
    def build_level(items, current_level):
        result = []
        while items:
            para, level = items[0]
            if level == current_level:
                result.append(
                    ListItem(
                        Paragraph(para.text, styles['body']),
                        leftIndent=12*(level-1)
                    )
                )
                items.pop(0)
            elif level > current_level:
                # Start nested sublist
                nested = build_level(items, level)
                result[-1].flowables.append(
                    ListFlowable(nested, bulletType='1' if ordered else 'bullet', leftIndent=12*level)
                )
            else:
                # Level up; return to previous recursion
                break
        return result

    result = build_level(list_items.copy(), list_items[0][1] if list_items else 1)
    return ListFlowable(result, bulletType='1' if ordered else 'bullet')

def parse_bullet_lists(docx_paragraphs, styles):
    """
    Consumes docx paragraphs and returns a list of Flowables, grouping lists as needed.
    """
    blocks = group_lists(docx_paragraphs)
    flowables = []
    for typ, data in blocks:
        if typ == "list":
            # Decide if it's ordered or unordered by style
            is_ordered = any("number" in p.style.name.lower() for p, _ in data)
            flowables.append(make_list_flowable(data, styles, ordered=is_ordered))
        else:  # "para"
            para = data
            flowables.append(Paragraph(para.text, styles['body']))
    return flowables
