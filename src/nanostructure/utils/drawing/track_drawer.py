class TrackDrawer:
    """Handle drawing of read tracks"""
    
    def __init__(self, colors):
        self.colors = colors

    def draw_tracks(self, render_data, tracks, y_offset, is_reverse=False):
        """
        Draw read tracks with proper positioning and coloring
        
        Args:
            render_data: Dictionary containing drawing information
            tracks: List of track tuples (x_start, x_end, track_position, read)
            y_offset: Vertical offset for track placement
            is_reverse: Boolean indicating if these are reverse strand reads
        """
        track_data = []
        
        for i, (x_start, x_end, _, _) in enumerate(tracks):
            y = y_offset + (i * (render_data['read_height'] + render_data['track_spacing']))
            track_data.append({
                'position': (x_start, y),
                'size': (x_end - x_start, render_data['read_height']),
                'color': self.colors['R'] if is_reverse else self.colors['F']
            })
            
        return track_data 