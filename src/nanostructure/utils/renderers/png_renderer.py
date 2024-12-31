from PIL import Image, ImageDraw
from .base_renderer import BaseRenderer

class PNGRenderer(BaseRenderer):
    """PNG format renderer implementation"""
    
    def render(self, forward_tracks, reverse_tracks, output_path, title=None):
        """Render tracks to PNG format"""
        total_tracks = len(forward_tracks) + len(reverse_tracks)
        if total_tracks > self.max_tracks:
            self.optimize_track_layout(forward_tracks + reverse_tracks)
            
        # 获取通用渲染数据
        render_data = self._render_common(forward_tracks, reverse_tracks, title)
        
        # 创建新图像
        img = Image.new('RGB', 
                       (render_data['dimensions']['width'], 
                        render_data['dimensions']['height']), 
                       self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # 绘制坐标系
        if hasattr(self, 'coordinates'):
            coord_data = self.coordinates.get_render_data(render_data['margins']['top'] - 50)
            
            # 绘制主轴线
            draw.line(coord_data['axis']['line'], 
                     fill=coord_data['axis']['color'],
                     width=coord_data['axis']['width'])
            
            # 绘制刻度
            for tick in coord_data['ticks']:
                draw.line([tick['start'], tick['end']], 
                         fill=tick['color'],
                         width=tick['width'])
            
            # 绘制标签
            for label in coord_data['labels']:
                draw.text(label['position'], 
                         label['text'], 
                         font=label['font'],
                         fill=label['color'])
            
            # 绘制染色体标签
            if 'chrom_label' in coord_data:
                draw.text(coord_data['chrom_label']['position'],
                         coord_data['chrom_label']['text'],
                         font=coord_data['chrom_label']['font'],
                         fill=coord_data['chrom_label']['color'])
        
        # 绘制标题
        if title:
            draw.text(render_data['title']['position'], 
                     render_data['title']['text'], 
                     fill=self.colors['axis'])
        
        # 绘制正向reads
        for track_data in render_data['tracks']['forward']:
            track = track_data['track']
            self.draw_read(draw, track, track_data['y'])
        
        # 绘制反向reads
        for track_data in render_data['tracks']['reverse']:
            track = track_data['track']
            self.draw_read(draw, track, track_data['y'])
        
        # 保存图像
        img.save(output_path) 

    def draw_read(self, draw, track, y_pos):
        """Draw a single read with exons and intron lines"""
        x_start, x_end, _, read, blocks = track
        
        # Draw thin line for full read length (intron connection)
        draw.line([(x_start, y_pos), (x_end, y_pos)], 
                 fill=self.colors['background'], width=1)
        
        # Draw thicker blocks for exons
        for block_start, block_end in blocks:
            draw.line([(block_start, y_pos), (block_end, y_pos)],
                     fill=self.colors['F' if not read.is_reverse else 'R'],
                     width=self.read_height) 