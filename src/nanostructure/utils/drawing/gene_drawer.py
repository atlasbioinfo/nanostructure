class GeneDrawer:
    """Handle drawing of gene structures"""
    
    def __init__(self, style=None):
        self.style = style or {
            'exon_fill': '#000000',
            'exon_opacity': 0.7,
            'intron_color': '#666666',
            'arrow_size': 8,
            'text_color': '#333333'
        }
        self.exon_height = 20
        self.intron_height = 2

    def draw_gene_structure(self, render_data, gene_annotation):
        """
        Calculate gene structure drawing data
        
        Args:
            render_data: Dictionary containing drawing information
            gene_annotation: List of gene feature dictionaries
        Returns:
            dict: Dictionary containing drawing information
        """
        if not gene_annotation:
            return None
            
        gene_y = render_data['axis']['y'] + render_data['margins']['gene']
        
        draw_data = {
            'gene_y': gene_y,
            'intron_line': None,
            'exons': [],
            'strand': gene_annotation[0]['strand'],
            'style': self.style
        }
        
        # Calculate intron line
        if gene_annotation:
            first_feature = min(gene_annotation, key=lambda x: x['start'])
            last_feature = max(gene_annotation, key=lambda x: x['end'])
            x1 = render_data['scale'].xmap[first_feature['start']]['spos']
            x2 = render_data['scale'].xmap[last_feature['end']]['spos']
            
            draw_data['intron_line'] = {
                'start': (x1, gene_y + self.exon_height/2),
                'end': (x2, gene_y + self.exon_height/2),
                'width': self.intron_height,
                'arrows': self._calculate_arrows(x1, x2, gene_y, draw_data['strand'])
            }
        
        # Calculate exon positions
        for feature in gene_annotation:
            if feature['type'] in ['exon', 'CDS']:
                x1 = render_data['scale'].xmap[feature['start']]['spos']
                x2 = render_data['scale'].xmap[feature['end']]['spos']
                draw_data['exons'].append({
                    'position': (x1, gene_y),
                    'size': (x2 - x1, self.exon_height)
                })
        
        return draw_data

    def _calculate_arrows(self, x1, x2, gene_y, strand):
        """Calculate arrow positions for intron line"""
        arrow_points = []
        line_length = x2 - x1
        arrow_spacing = max(120, line_length // 5)
        
        if strand in ['+', '1']:
            for x in range(x1 + arrow_spacing, x2 - arrow_spacing//2, arrow_spacing):
                arrow_points.append(self._create_arrow_points(x, gene_y, True))
        elif strand in ['-', '-1']:
            for x in range(x2 - arrow_spacing, x1 + arrow_spacing//2, -arrow_spacing):
                arrow_points.append(self._create_arrow_points(x, gene_y, False))
                
        return arrow_points

    def _create_arrow_points(self, x, gene_y, forward=True):
        """Create arrow points for given position"""
        arrow_size = self.style['arrow_size']
        y = gene_y + self.exon_height/2
        
        if forward:
            points = [
                (x - arrow_size, y - arrow_size/2),
                (x, y),
                (x - arrow_size, y + arrow_size/2)
            ]
        else:
            points = [
                (x + arrow_size, y - arrow_size/2),
                (x, y),
                (x + arrow_size, y + arrow_size/2)
            ]
            
        return {
            'x': x,
            'points': points
        } 