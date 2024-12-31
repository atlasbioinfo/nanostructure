from ...config.colors import colors
from .gene_coordinates import GeneCoordinates
from .image_renderer import ImageRenderer

class DrawingCoordinates(GeneCoordinates):
    """Handle coordinate drawing and rendering"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = None
        self.axisloc = "top"
        self.exon_height = colors['dimensions']['exon_height']
        self.intron_height = colors['dimensions']['intron_height']
        self.TRACK_MARGIN = colors['dimensions']['track_margin']
        self.margin = colors['margins']
        
    def initialize_renderer(self):
        """Initialize the image renderer"""
        self.renderer = ImageRenderer(
            width=self.width,
            height=self.height,
            bgcolor=self.bgcolor
        )
        
    def render(self, output_path, y_position):
        """Render coordinates and gene structure
        
        Args:
            output_path (str): Path where to save the rendered image
            y_position (int): Vertical position for coordinate axis
        """
        if not self.renderer:
            self.initialize_renderer()
            
        # Get coordinate rendering data
        coord_data = self.get_render_data(y_position)
        
        # Get gene structure rendering data
        gene_data = self.draw_gene_structure(y_position)
        
        # Render everything
        self.renderer.create_image()
        self.renderer.render_coordinates(coord_data)
        self.renderer.render_gene_structure(gene_data)
        
        # Save the result
        self.renderer.save(output_path)
        
    def draw_gene_structure(self, yi):
        """Calculate gene structure drawing data
        
        Args:
            yi: y-position of the coordinate axis
            
        Returns:
            dict: Dictionary containing drawing information
        """
        if not self.gene_annotation:
            return None
            
        gene_y = yi + self.LABEL_HEIGHT + self.GENE_STRUCTURE_MARGIN
        
        draw_data = {
            'gene_y': gene_y,
            'intron_line': None,
            'exons': [],
            'strand': None,
            'gene_name': self.transcript_id,
            'style': colors['gene']
        }
        
        if self.gene_annotation:
            draw_data['strand'] = self.gene_annotation[0]['strand']
        
        if len(self.gene_annotation) > 0:
            first_feature = min(self.gene_annotation, key=lambda x: x['start'])
            last_feature = max(self.gene_annotation, key=lambda x: x['end'])
            x1 = self.xscale.xmap[max(first_feature['start'], self.start_pos)]['spos']
            x2 = self.xscale.xmap[min(last_feature['end'], self.end_pos)]['spos']
            
            arrow_points = []
            line_length = x2 - x1
            arrow_spacing = max(120, line_length // 5)
            
            if draw_data['strand'] in ['+', '1']:
                for x in range(x1 + arrow_spacing, x2 - arrow_spacing//2, arrow_spacing):
                    arrow_points.append({
                        'x': x,
                        'points': [
                            (x - draw_data['style']['arrow_size'], gene_y + self.exon_height/2 - draw_data['style']['arrow_size']/2),
                            (x, gene_y + self.exon_height/2),
                            (x - draw_data['style']['arrow_size'], gene_y + self.exon_height/2 + draw_data['style']['arrow_size']/2)
                        ]
                    })
            elif draw_data['strand'] in ['-', '-1']:
                for x in range(x2 - arrow_spacing, x1 + arrow_spacing//2, -arrow_spacing):
                    arrow_points.append({
                        'x': x,
                        'points': [
                            (x + draw_data['style']['arrow_size'], gene_y + self.exon_height/2 - draw_data['style']['arrow_size']/2),
                            (x, gene_y + self.exon_height/2),
                            (x + draw_data['style']['arrow_size'], gene_y + self.exon_height/2 + draw_data['style']['arrow_size']/2)
                        ]
                    })
            
            draw_data['intron_line'] = {
                'start': (x1, gene_y + self.exon_height/2),
                'end': (x2, gene_y + self.exon_height/2),
                'width': self.intron_height,
                'arrows': arrow_points,
                'label_position': (x1, gene_y - 5)
            }
        
        for feature in self.gene_annotation:
            if feature['start'] > self.end_pos or feature['end'] < self.start_pos:
                continue
            
            start = max(feature['start'], self.start_pos)
            end = min(feature['end'], self.end_pos)
            
            if feature['type'] in ['exon']:
                x1 = self.xscale.xmap[start]['spos']
                x2 = self.xscale.xmap[end]['spos']
                draw_data['exons'].append({
                    'position': (x1, gene_y),
                    'size': (x2 - x1, self.exon_height)
                })
        
        return draw_data
        
    def calculate_track_start_y(self, gene_y):
        """Calculate the starting y position for read tracks"""
        return gene_y + self.exon_height + self.TRACK_MARGIN