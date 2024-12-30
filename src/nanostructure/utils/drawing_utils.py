def render_genomic_coordinates(draw, y_position, start_pos, end_pos, image_width, font, axis_color='black'):
    """Render genomic coordinate axis with tick marks and labels"""
    # Draw main axis line
    draw.line([(0, y_position), (image_width, y_position)], fill=axis_color)
    
    # Calculate and draw ticks
    from .coordinate_utils import calculate_tick_interval
    tick_interval = calculate_tick_interval(end_pos - start_pos)
    first_tick = ((start_pos // tick_interval) + 1) * tick_interval
    
    for pos in range(first_tick, end_pos, tick_interval):
        x = int((pos - start_pos) * image_width / (end_pos - start_pos))
        
        # Draw tick mark
        tick_height = 5
        draw.line([(x, y_position), (x, y_position + tick_height)], fill=axis_color)
        
        # Draw label
        label = str(pos)
        try:
            text_width = draw.textlength(label, font=font)
        except AttributeError:
            text_width = draw.textsize(label, font=font)[0]
        draw.text((x - text_width/2, y_position + tick_height + 2), 
                 label, fill=axis_color, font=font) 