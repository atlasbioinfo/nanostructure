from PIL import Image, ImageDraw

class ImageRenderer:
    """Handle image rendering for coordinates and gene structures"""
    
    def __init__(self, width, height, bgcolor='#ffffff'):
        """Initialize renderer
        
        Args:
            width (int): Image width
            height (int): Image height
            bgcolor (str): Background color in hex format
        """
        self.width = width
        self.height = height
        self.bgcolor = bgcolor
        self.image = None
        self.draw = None
        
    def create_image(self):
        """Create new image with specified dimensions"""
        self.image = Image.new('RGBA', (self.width, self.height), self.bgcolor)
        self.draw = ImageDraw.Draw(self.image)
        
    def render_coordinates(self, coord_data):
        """Render coordinate axis and labels
        
        Args:
            coord_data (dict): Coordinate rendering data from BaseCoordinates
        """
        if self.draw is None:
            self.create_image()
            
        # Draw main axis line
        self.draw.line(
            coord_data['axis']['line'],
            fill=coord_data['axis']['color'],
            width=coord_data['axis']['width']
        )
        
        # Draw ticks
        for tick in coord_data['ticks']:
            self.draw.line(
                [tick['start'], tick['end']],
                fill=tick['color'],
                width=tick['width']
            )
            
        # Draw labels
        for label in coord_data['labels']:
            self.draw.text(
                label['position'],
                label['text'],
                fill=label['color'],
                font=label['font'],
                anchor="mt"  # Middle top alignment
            )
            
        # Draw chromosome label if present
        if 'chrom_label' in coord_data:
            self.draw.text(
                coord_data['chrom_label']['position'],
                coord_data['chrom_label']['text'],
                fill=coord_data['chrom_label']['color'],
                font=coord_data['chrom_label']['font']
            )
            
    def render_gene_structure(self, gene_data):
        """Render gene structure
        
        Args:
            gene_data (dict): Gene structure rendering data from DrawingCoordinates
        """
        if self.draw is None:
            self.create_image()
            
        if not gene_data:
            return
            
        # Draw intron line
        if gene_data['intron_line']:
            self.draw.line(
                [gene_data['intron_line']['start'], gene_data['intron_line']['end']],
                fill=gene_data['style']['intron_color'],
                width=gene_data['intron_line']['width']
            )
            
            # Draw direction arrows
            for arrow in gene_data['intron_line']['arrows']:
                self.draw.polygon(
                    arrow['points'],
                    fill=gene_data['style']['intron_color']
                )
            
        # Draw exons
        for exon in gene_data['exons']:
            self.draw.rectangle(
                [
                    exon['position'],
                    (
                        exon['position'][0] + exon['size'][0],
                        exon['position'][1] + exon['size'][1]
                    )
                ],
                fill=gene_data['style']['exon_fill'],
                outline=gene_data['style']['exon_fill']
            )
            
        # Draw gene name
        if gene_data['gene_name']:
            self.draw.text(
                gene_data['intron_line']['label_position'],
                gene_data['gene_name'],
                fill=gene_data['style']['text_color'],
                anchor="lb"  # Left bottom alignment
            )
            
    def save(self, filepath):
        """Save rendered image
        
        Args:
            filepath (str): Path where to save the image
        """
        if self.image:
            self.image.save(filepath) 