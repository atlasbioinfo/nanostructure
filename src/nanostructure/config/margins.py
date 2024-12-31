"""Configuration for margins and spacing"""

margin_to_the_left = 100

MARGINS = {
    'title': {
        'top': 20,     # Top margin of title
        'bottom': 5,   # Bottom margin of title
        'left': margin_to_the_left,    # Left margin of title
        'right': 50,   # Right margin of title
        'height': 20   # Total height of title area
    },
    'axis': {
        'top': 10,     # Top margin of axis
        'bottom': 1,   # Bottom margin of axis
        'left': margin_to_the_left,    # Left margin of axis
        'right': 50,   # Right margin of axis
        'height': 20,  # Total height of axis area
        'label_spacing': {
            'chrom_to_axis': 15,    # Distance from chromosome name to axis
            'axis_to_coord': 15,    # Distance from axis to coordinate numbers
        }
    },
    'gene_model': {
        'top': 20,     # Top margin of gene model
        'bottom': 0,  # Bottom margin of gene model
        'left': margin_to_the_left,    # Left margin of gene model
        'right': 50,   # Right margin of gene model
        'height': 50   # Total height of gene model area
    },
    'reads': {
        'top': 20,     # Top margin of reads area
        'bottom': 30,  # Bottom margin of reads area
        'left': margin_to_the_left,    # Left margin of reads area
        'right': 50,   # Right margin of reads area
        'height': 200  # Total height of reads area
    }
}