# utils/margins.py

def calculate_kdp_margins(trim_size: str, page_count: int, bleed: bool, is_color: bool = False):
    """
    Returns a dictionary with left, right, top, bottom, and gutter (inches) based on KDP rules.
    Arguments:
        trim_size: e.g. '6x9', '5x8', etc.
        page_count: total number of pages in the book
        bleed: whether the book uses bleed or not
        is_color: (optional) if the interior is color (may affect some margin rules)
    Returns:
        dict: {'top': float, 'bottom': float, 'left': float, 'right': float, 'gutter': float}
    """
    # KDP minimums and recommended defaults (as of 2024)
    size_defaults = {
        '6x9':  {'top': 0.75, 'bottom': 0.75, 'left': 0.75, 'right': 0.75},
        '5x8':  {'top': 0.75, 'bottom': 0.75, 'left': 0.625, 'right': 0.625},
        '8.5x11': {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0},
        # Add more as needed
    }
    base = size_defaults.get(trim_size, size_defaults['6x9']).copy()

    # KDP gutter (inside margin) rules (updated)
    if page_count <= 150:
        gutter = 0.375
    elif page_count <= 300:
        gutter = 0.5
    elif page_count <= 500:
        gutter = 0.625
    elif page_count <= 700:
        gutter = 0.75
    else:
        gutter = 0.875  # For up to 828 pages (KDP max for most sizes)

    # Bleed adjustment: add 0.125" to all outer margins if bleed is on
    if bleed:
        for side in ['top', 'bottom', 'left', 'right']:
            base[side] += 0.125

    base['gutter'] = gutter
    return base

def get_margin_tuple(trim_size: str, page_count: int, bleed: bool) -> tuple:
    """
    Returns (left, right, top, bottom, gutter) in inches, for direct use in PDF generation.
    """
    m = calculate_kdp_margins(trim_size, page_count, bleed)
    return m['left'], m['right'], m['top'], m['bottom'], m['gutter']
