"""Configuration for coordinate system"""
from .colors import COLORS

COORDINATES = {
    'dimensions': {
        'exon_height': 15,        # 外显子高度
        'intron_height': 2,       # 内含子线条高度
        'min_bar_size': 5,        # 最小条形图大小
        'min_axis_label_width': 50,  # 坐标轴标签最小宽度
        'gap_label_and_bar': 15,   # 增加标签和刻度线之间的间距
    },
    'margins': {
        'top': 50,    # 顶部边距，为标题和坐标轴预留空间
        'bottom': 50,  # 底部边距
        'left': 100,    # 左边距
        'right': 50    # 右边距
    },
    'axis': {
        'color': 'black',           # 坐标轴颜色
        'major_tick_length': 8,     # 主刻度线长度
        'minor_tick_length': 4,     # 次刻度线长度
        'line_width': 2,           # 坐标轴线宽
        'tick_line_width': 1,      # 刻度线宽度
    },
    'spacing': {
        'axis_top_margin': 30,        # 坐标轴顶部边距
        'label_height': 15,           # 标签高度
        'gene_structure_margin': 40,  # 基因结构与其他元素的间距
    },
    'styles': {
        'gene': COLORS['gene']
    },
    'colors': {
        'background': COLORS['background'],
        'label': COLORS['label'],
        'reads': COLORS['reads']
    }
} 