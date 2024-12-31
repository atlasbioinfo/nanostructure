class Title:
    """Title component"""
    def __init__(self, text, style=None):
        self.text = text
        self.style = style or {}
    
    def render(self, renderer, layout):
        """Render title"""
        # Calculate title position using layout margins
        x = layout['x_start']
        y = layout['y_start']
        
        renderer.draw_text(
            text=self.text,
            position=(x, y),
            color=renderer.colors['title_color'],
            font_size='14px'
        ) 