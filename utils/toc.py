# utils/toc.py

from reportlab.platypus import Paragraph, Spacer, PageBreak

def build_static_toc(headings, styles):
    """
    Given a list of headings, returns a list of Flowables for the Table of Contents.
    Args:
        headings: List of tuples (heading_text, heading_level)
        styles: Dict or stylesheet with a TOC style
    Returns:
        List of Flowables for the TOC section
    """
    flowables = []
    flowables.append(PageBreak())
    flowables.append(Paragraph("Table of Contents", styles['BookHeading']))
    flowables.append(Spacer(1, 18))
    for text, level in headings:
        indent = 12 * (level - 1)  # indent sub-levels
        flowables.append(
            Paragraph(f'<para leftIndent={indent}>{text}</para>', styles['BookBody'])
        )
        flowables.append(Spacer(1, 6))
    flowables.append(PageBreak())
    return flowables
