from ..core.renderer import BaseRenderer
from ..config.coordinates import COORDINATES
from ..config.margins import MARGINS

class Axis:
    """坐标轴组件"""
    def __init__(self, start, end, style=None):
        self.start = start
        self.end = end
        self.style = style or {
            'color': COORDINATES['axis']['color'],
            'width': COORDINATES['axis']['line_width'],
            'tick_length': COORDINATES['axis']['major_tick_length'],
            'tick_width': COORDINATES['axis']['tick_line_width']
        }
    
    def render(self, renderer, layout):
        """Render axis component"""
        y_position = layout['y_start'] + layout['height'] / 2
        
        # Draw main axis line
        renderer.draw_line(
            start=(layout['x_start'], y_position),
            end=(layout['x_end'], y_position),
            color=self.style['color'],
            width=self.style['width']
        )
        
        # Get coordinate data from renderer
        if hasattr(renderer, 'coordinates'):
            # 确保先计算刻度
            renderer.coordinates.calculate_ticks()
            
            coord_data = renderer.coordinates.get_render_data(
                y_position,
                coord_y_offset=MARGINS['axis']['label_spacing']['axis_to_coord'],
                chrom_y_offset=MARGINS['axis']['label_spacing']['chrom_to_axis']
            )
            
            # Draw ticks
            for tick in coord_data['ticks']:
                renderer.draw_line(
                    start=tick['start'],
                    end=tick['end'],
                    color=tick['color'],
                    width=tick['width']
                )
            
            # Draw labels
            for label in coord_data['labels']:
                renderer.draw_text(
                    text=label['text'],
                    position=label['position'],
                    color=label['color']
                )
            
            # Draw chromosome label if available
            if 'chrom_label' in coord_data:
                renderer.draw_text(
                    text=coord_data['chrom_label']['text'],
                    position=coord_data['chrom_label']['position'],
                    color=coord_data['chrom_label']['color']
                ) 