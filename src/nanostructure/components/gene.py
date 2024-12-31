from ..config.coordinates import COORDINATES
from ..config.colors import COLORS

class GeneComponent:
    """Gene model visualization component"""
    
    def __init__(self, gene_data, style=None):
        self.gene_data = gene_data
        self.style = style or {
            'exon_height': COORDINATES['dimensions']['exon_height'],
            'intron_height': COORDINATES['dimensions']['intron_height'],
            'exon_color': COLORS['gene']['exon'],
            'intron_color': COLORS['gene']['intron'],
            'text_color': COLORS['gene']['text']
        }
    
    def render(self, renderer, layout):
        """Render gene model"""
        gene_y = layout['y_start'] + layout['height']/2
        
        # Draw gene name and intron line if available
        if self.gene_data.get('gene_name') and self.gene_data.get('intron_line'):
            self._render_gene_name_and_intron(renderer, gene_y)
        
        # Draw exons
        self._render_exons(renderer, gene_y)
    
    def _render_gene_name_and_intron(self, renderer, gene_y):
        """Render gene name and intron line with direction arrows"""
        intron_data = self.gene_data['intron_line']
        
        # Draw gene name
        renderer.draw_text(
            text=self.gene_data['gene_name'],
            position=intron_data['label_position'],
            color=self.style['text_color']
        )
        
        # Draw intron line
        renderer.draw_line(
            start=intron_data['start'],
            end=intron_data['end'],
            color=self.style['intron_color'],
            width=self.style['intron_height']
        )
        
        # Draw direction arrows
        for arrow in intron_data['arrows']:
            renderer.draw_polyline(
                points=arrow['points'],
                color=self.style['intron_color']
            )
    
    def _render_exons(self, renderer, gene_y):
        """Render exon blocks"""
        for exon in self.gene_data['exons']:
            renderer.draw_rectangle(
                position=exon['position'],
                size=exon['size'],
                color=self.style['exon_color']
            ) 