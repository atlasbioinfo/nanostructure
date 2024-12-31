"""Configuration for colors and styles"""

colors = {
    # Basic colors
    'background': 'white',
    'axis_color': 'black',
    'label': '#000000',
    'title_color': '#000000',  # Added explicit title color
    
    # Read colors
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
    },
    
    # Dimensions
    'dimensions': {
        'exon_height': 20,
        'intron_height': 2,
        'min_bar_size': 5,
        'min_axis_label_width': 100,
        'gap_label_and_bar': 4,
        'track_margin': 20,
    },
    
    # Margins
    'margins': {
        'top': 150,     # Space for title and axis
        'bottom': 50,   # Bottom margin
        'left': 50,     # Left margin
        'right': 50     # Right margin
    },
    
    # Axis style
    'axis': {
        'color': 'black',            # Color for axis lines
        'major_tick_length': 8,
        'minor_tick_length': 4,
        'line_width': 2,
        'tick_line_width': 1,
    },
    
    # Spacing
    'spacing': {
        'axis_top_margin': 30,         # Top padding
        'label_height': 25,            # Label height
        'gene_structure_margin': 20,   # Space between gene structure and axis
    }
} 