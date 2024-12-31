from pathlib import Path
from PIL import ImageFont
import math

class XScale:
    """Handle x-axis scaling calculations"""
    
    def __init__(self, start, end, width):
        self.xmap = {}
        scale = width / (end - start)
        for pos in range(start, end + 1):
            cpos = int((pos - start) * scale)
            self.xmap[pos] = {
                'cpos': cpos,
                'spos': max(0, cpos - 1),
                'epos': min(width, cpos + 1)
            }

class BaseCoordinates:
    """Base class for coordinate system handling"""
    
    def __init__(self):
        self.start_pos = None
        self.end_pos = None
        self.chrom = None
        self.width = None
        self.xscale = None
        self.font = None
        self.font_size = None
        self.MIN_AXIS_LABEL_WIDTH = 50
        
    def set_font(self, font_size=12):
        """Set font for coordinate labels"""
        self.font_size = font_size
        font_path = Path(__file__).parent.parent / 'utils' / 'fonts' / 'VeraMono.ttf'
        self.font = ImageFont.truetype(str(font_path), font_size)
        self.single_font_size = self.font.getsize('C')

    def calculate_ticks(self):
        """Calculate axis ticks and labels with improved spacing"""
        if not all([self.start_pos, self.end_pos]):
            return
            
        genome_length = self.end_pos - self.start_pos
        
        # 计算合适的刻度间隔
        ideal_tick_count = max(4, min(10, self.width // self.MIN_AXIS_LABEL_WIDTH))
        base_unit = 10 ** (len(str(genome_length)) - 1)
        
        possible_intervals = [
            base_unit/10, base_unit/5, base_unit/2,
            base_unit, base_unit*2, base_unit*5
        ]
        
        # 选择最接近理想刻度数量的间隔
        interval = min(possible_intervals,
                      key=lambda x: abs(genome_length/x - ideal_tick_count))
        
        # 计算起始位置（对齐到间隔）
        start = math.ceil(self.start_pos / interval) * interval
        
        # 生成主刻度位置
        self.axis_pos_list = []
        self.axis_x_list = []
        
        current_pos = start
        while current_pos < self.end_pos:
            if current_pos >= self.start_pos:
                self.axis_pos_list.append(current_pos)
                self.axis_x_list.append(self.xscale.xmap[int(current_pos)]['cpos'])
            current_pos += interval

class GeneCoordinates(BaseCoordinates):
    """Coordinate system for gene visualization"""
    
    def __init__(self):
        super().__init__()
        self.exon_height = None
        self.intron_height = None
        self.renderer = None
    
    def set_dimensions(self, exon_height=15, intron_height=2):
        """Set dimensions for gene visualization"""
        self.exon_height = exon_height
        self.intron_height = intron_height
    
    def calculate_track_start_y(self, gene_y):
        """Calculate the starting y position for read tracks"""
        if hasattr(self, 'renderer') and self.renderer:
            spacing = self.renderer.track_spacing
        else:
            spacing = 2  # 默认值
        return gene_y + self.exon_height + spacing

class DrawingCoordinates(GeneCoordinates):
    """Enhanced coordinate system with drawing capabilities"""
    
    def __init__(self):
        super().__init__()
        self.renderer = None
    
    def get_render_data(self, y_position):
        """Get rendering data for coordinates"""
        if not self.font:
            self.set_font()
        
        self.calculate_ticks()
        
        return {
            'axis': {
                'line': [(0, y_position), (self.width, y_position)],
                'color': 'black',
                'width': 1
            },
            'ticks': [
                {
                    'start': (x, y_position),
                    'end': (x, y_position + 5),
                    'color': 'black',
                    'width': 1
                }
                for x in self.axis_x_list
            ],
            'labels': [
                {
                    'text': str(pos),
                    'position': (x, y_position + 7),
                    'color': 'black'
                }
                for pos, x in zip(self.axis_pos_list, self.axis_x_list)
            ],
            'chrom_label': {
                'text': self.chrom,
                'position': (10, y_position - 5),
                'color': 'black'
            } if self.chrom else None
        } 