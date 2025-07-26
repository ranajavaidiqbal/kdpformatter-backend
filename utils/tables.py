from reportlab.platypus import Table as RLTable, TableStyle, Spacer

def parse_tables(doc, styles):
    """
    Extracts all tables from a docx Document and returns
    a list of ReportLab flowables (tables and spacers).
    """
    flowables = []
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
        flowables.append(Spacer(1, 12))
        flowables.append(rl_table)
        flowables.append(Spacer(1, 12))
    return flowables
