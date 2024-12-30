from PIL import Image, ImageDraw
from .base_renderer import BaseRenderer

class PNGRenderer(BaseRenderer):
    """PNG format renderer implementation"""
    
    def render(self, forward_tracks, reverse_tracks, output_path, title):
        """Render tracks to PNG format"""
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
            draw.rectangle(
                [(track[0], track_data['y']),
                 (track[1], track_data['y'] + self.read_height)],
                fill=self.colors['F']
            )
        
        # 绘制反向reads
        for track_data in render_data['tracks']['reverse']:
            track = track_data['track']
            draw.rectangle(
                [(track[0], track_data['y']),
                 (track[1], track_data['y'] + self.read_height)],
                fill=self.colors['R']
            )
        
        # 保存图像
        img.save(output_path) 