"""Configuration for colors and styles"""

COLORS = {
    # Basic colors
    'background': 'white',
    'axis_color': 'black',
    'label': '#000000',
    'title_color': '#000000',  # Added explicit title color

    'reads': {
        'F': '#163f63',  # Forward reads
        'R': '#eb5252',  # Reverse reads
        'B': '#163f63'   # Both strands
    },
    
    # Gene structure colors and styles
    'gene': {
        'color': '#4a90e2',          # Basic gene color
        'text_color': '#333333',     # Gene label color
        'exon_color': '#2c5282',     # Exon outline color
        'exon_fill': '#2c5282',      # Exon fill color
        'exon_opacity': 1,           # Exon fill opacity
        'intron_color': '#666666',   # Intron line color
        'arrow_size': 8,             # Direction arrow size
        'arrow_spacing': 120,        # Space between arrows
    }
} 