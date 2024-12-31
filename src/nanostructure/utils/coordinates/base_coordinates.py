from PIL import ImageFont
from pathlib import Path
import math
from ...config.colors import colors

class BaseCoordinates:
    """Base class for coordinate handling"""
    
    # 基础尺寸常量
    MIN_BAR_SIZE = colors['dimensions']['min_bar_size']
    MIN_AXIS_LABEL_WIDTH = colors['dimensions']['min_axis_label_width']
    GAP_LABEL_AND_BAR = colors['dimensions']['gap_label_and_bar']
    
    # 样式常量
    MAJOR_TICK_LENGTH = colors['axis']['major_tick_length']
    MINOR_TICK_LENGTH = colors['axis']['minor_tick_length']
    AXIS_LINE_WIDTH = colors['axis']['line_width']
    TICK_LINE_WIDTH = colors['axis']['tick_line_width']
    
    # 高度相关常量
    AXIS_TOP_MARGIN = colors['spacing']['axis_top_margin']
    LABEL_HEIGHT = colors['spacing']['label_height']
    GENE_STRUCTURE_MARGIN = colors['spacing']['gene_structure_margin']

    def __init__(self, chrom=None, start_pos=None, end_pos=None, xscale=None, width=1000, height=50):
        self.chrom = chrom
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.xscale = xscale
        self.width = width
        self.height = height
        
        # 字体相关
        self.font = None
        self.font_size = 12
        
        # 样式设置
        self.bgcolor = colors['background']
        self.axiscolor = colors['axis']
        self.labelcolor = colors['label']
        
        # 计算相关
        self.axis_pos_list = []
        self.axis_x_list = []
        self.bar_size = None
        self.single_font_size = None

    def set_font(self, font_size=12):
        """Set font for coordinate labels"""
        self.font_size = font_size
        font_path = Path(__file__).parent.parent / 'fonts' / 'VeraMono.ttf'
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

    def get_render_data(self, y_position):
        """Get coordinate rendering data"""
        render_data = {
            'axis': {
                'line': [(self.margin['left'], y_position),
                        (self.width - self.margin['right'], y_position)],
                'y': y_position,
                'color': colors['axis']['color'],
                'width': colors['axis']['line_width']
            },
            'ticks': [],
            'labels': [],
            'scale': self.xscale
        }
        
        # Add ticks and labels
        for pos, x in zip(self.axis_pos_list, self.axis_x_list):
            # Tick data
            render_data['ticks'].append({
                'start': (x, y_position),
                'end': (x, y_position + self.MAJOR_TICK_LENGTH),
                'color': colors['axis']['color'],
                'width': colors['axis']['tick_line_width']
            })
            
            # Label data
            label = format(int(pos), ',d')
            render_data['labels'].append({
                'text': label,
                'position': (x, y_position + self.MAJOR_TICK_LENGTH + self.GAP_LABEL_AND_BAR),
                'color': colors['label'],
                'font': self.font
            })
        
        # Add chromosome label if available
        if self.chrom:
            render_data['chrom_label'] = {
                'text': f"Chromosome {self.chrom}",
                'position': (5, y_position - self.LABEL_HEIGHT),
                'color': colors['label'],
                'font': self.font
            }
            
        return render_data

    def resize_height(self):
        """Calculate appropriate height based on content"""
        if self.font is None:
            self.set_font()
            
        min_height = (self.AXIS_TOP_MARGIN + 
                     self.LABEL_HEIGHT + 
                     self.MAJOR_TICK_LENGTH + 
                     self.GAP_LABEL_AND_BAR + 
                     self.font_size)
        
        self.height = max(self.height, min_height)
        self.bar_size = self.height - self.single_font_size[1] - self.GAP_LABEL_AND_BAR 