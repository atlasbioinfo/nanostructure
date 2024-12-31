class ReadsComponent:
    """Reads visualization component"""
    
    def __init__(self, forward_tracks, reverse_tracks, style=None):
        self.forward_tracks = forward_tracks
        self.reverse_tracks = reverse_tracks
        self.style = style or {}
        self.occupied_positions = []
    
    @staticmethod
    def find_available_track_position(read_start, read_end, occupied_positions):
        """Find first available vertical track position for read placement"""
        track_pos = 0
        while True:
            can_place = True
            for existing_read in occupied_positions:
                if (read_start <= existing_read[1] and 
                    read_end >= existing_read[0] and 
                    track_pos == existing_read[2]):
                    can_place = False
                    break
            if can_place:
                return track_pos
            track_pos += 1
    
    def render(self, renderer, layout):
        """Render reads tracks"""
        current_y = layout['y_start']
        
        # Render forward tracks
        for track in self.forward_tracks:
            x_start, x_end = track[0], track[1]
            track_pos = self.find_available_track_position(
                x_start, x_end, self.occupied_positions)
            self.occupied_positions.append((x_start, x_end, track_pos))
            
            y_pos = current_y + (track_pos * (renderer.read_height + renderer.track_spacing))
            self._render_single_track(renderer, track, y_pos, 'forward')
        
        # Reset occupied positions for reverse tracks
        self.occupied_positions = []
        current_y += renderer.track_spacing * 2
        
        # Render reverse tracks
        for track in self.reverse_tracks:
            x_start, x_end = track[0], track[1]
            track_pos = self.find_available_track_position(
                x_start, x_end, self.occupied_positions)
            self.occupied_positions.append((x_start, x_end, track_pos))
            
            y_pos = current_y + (track_pos * (renderer.read_height + renderer.track_spacing))
            self._render_single_track(renderer, track, y_pos, 'reverse')
    
    def _render_single_track(self, renderer, track, y_pos, strand):
        """Render a single read track"""
        x_start, x_end, _, read, blocks = track
        
        # Draw intron line
        renderer.draw_line(
            start=(x_start, y_pos + renderer.read_height/2),
            end=(x_end, y_pos + renderer.read_height/2),
            color='#A6A6A6',
            width=1
        )
        
        # Draw exon blocks
        color = renderer.colors['reads']['F' if strand == 'forward' else 'R']
        for block_start, block_end in blocks:
            renderer.draw_rectangle(
                position=(block_start, y_pos),
                size=(block_end - block_start, renderer.read_height),
                color=color
            ) 