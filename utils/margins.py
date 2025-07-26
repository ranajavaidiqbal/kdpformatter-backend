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
    # KDP margin/gutter values: https://kdp.amazon.com/en_US/help/topic/G200735480
    size_defaults = {
        '6x9':  {'top': 0.75, 'bottom': 0.75, 'left': 0.75, 'right': 0.75},
        '5x8':  {'top': 0.75, 'bottom': 0.75, 'left': 0.625, 'right': 0.625},
        # Add more sizes as needed!
    }
    base = size_defaults.get(trim_size, size_defaults['6x9']).copy()

    # Gutter calculation (KDP recommendations, update as needed)
    if page_count < 151:
        gutter = 0.25
    elif page_count < 401:
        gutter = 0.375
    elif page_count < 601:
        gutter = 0.5
    else:
        gutter = 0.625

    # Bleed adjustment (add 0.125" per KDP for bleed books)
    if bleed:
        base['top'] += 0.125
        base['bottom'] += 0.125
        base['left'] += 0.125
        base['right'] += 0.125

    base['gutter'] = gutter
    return base
