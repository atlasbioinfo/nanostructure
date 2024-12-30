import svgwrite
import cairosvg
from pathlib import Path
from .base_renderer import BaseRenderer

class VectorRenderer(BaseRenderer):
    """Vector format (SVG/PDF) renderer implementation"""
    
    def render(self, forward_tracks, reverse_tracks, output_path, title):
        """Render tracks to SVG/PDF format"""
        # 获取通用渲染数据
        render_data = self._render_common(forward_tracks, reverse_tracks, title)
        
        # 创建SVG绘图对象
        dwg = svgwrite.Drawing(output_path, size=(render_data['dimensions']['width'],
                                                 render_data['dimensions']['height']))
        
        # 添加背景
        dwg.add(dwg.rect(insert=(0, 0),
                        size=(render_data['dimensions']['width'],
                              render_data['dimensions']['height']),
                        fill=self.colors['background']))
        
        # 绘制坐标系
        if hasattr(self, 'coordinates'):
            coord = self.coordinates
            
            # 确保坐标轴数据已计算
            if coord.font is None:
                coord.set_font()
            coord.resize_height()
            coord.calculate_ticks()
            
            # 获取渲染数据
            coord_data = coord.get_render_data(65)
            
            # Add chromosome label
            if 'chrom_label' in coord_data:
                dwg.add(dwg.text(coord_data['chrom_label']['text'],
                                insert=coord_data['chrom_label']['position'],
                                font_family='Arial',
                                font_size=f"{coord.font_size}px",
                                fill=coord_data['chrom_label']['color']))
            
            # Draw main axis line
            dwg.add(dwg.line(start=coord_data['axis']['line'][0],
                            end=coord_data['axis']['line'][1],
                            stroke=coord_data['axis']['color'],
                            stroke_width=coord_data['axis']['width']))
            
            # Draw ticks and labels
            for tick in coord_data['ticks']:
                dwg.add(dwg.line(start=tick['start'],
                                end=tick['end'],
                                stroke=tick['color'],
                                stroke_width=tick['width']))
            
            for label in coord_data['labels']:
                dwg.add(dwg.text(label['text'],
                                insert=label['position'],
                                text_anchor='middle',
                                font_family='Arial',
                                font_size=f"{coord.font_size}px",
                                fill=label['color']))
            
            # Draw gene structure if available
            gene_data = coord.draw_gene_structure(coord_data['axis']['y'])
            if gene_data:
                # Draw gene name
                if gene_data['gene_name'] and gene_data['intron_line']:
                    dwg.add(dwg.text(gene_data['gene_name'],
                                   insert=gene_data['intron_line']['label_position'],
                                   font_family='Arial',
                                   font_size='12px',
                                   fill=gene_data['style']['text_color']))
                
                # Draw intron line
                if gene_data['intron_line']:
                    dwg.add(dwg.line(start=gene_data['intron_line']['start'],
                                   end=gene_data['intron_line']['end'],
                                   stroke=gene_data['style']['intron_color'],
                                   stroke_width=gene_data['intron_line']['width']))
                    
                    # Draw direction arrows
                    for arrow in gene_data['intron_line']['arrows']:
                        points = arrow['points']
                        dwg.add(dwg.polyline(points=points,
                                           stroke=gene_data['style']['intron_color'],
                                           fill='none',
                                           stroke_width=1))
                
                # Draw exons
                for exon in gene_data['exons']:
                    dwg.add(dwg.rect(insert=exon['position'],
                                   size=exon['size'],
                                   fill=gene_data['style']['exon_fill'],
                                   fill_opacity=gene_data['style']['exon_opacity']))
        
        # 绘制标题
        if title:
            dwg.add(dwg.text(render_data['title']['text'],
                           insert=render_data['title']['position'],
                           font_family='Arial',
                           font_size='14px',
                           font_weight='bold',
                           fill=self.colors['axis']))
        
        # 绘制正向和反向reads
        track_start_y = 120
        for track_data in render_data['tracks']['forward']:
            track = track_data['track']
            dwg.add(dwg.rect(
                insert=(track[0], track_data['y'] + track_start_y),
                size=(track[1] - track[0], self.read_height),
                fill=self.colors['F']
            ))
        
        for track_data in render_data['tracks']['reverse']:
            track = track_data['track']
            dwg.add(dwg.rect(
                insert=(track[0], track_data['y'] + track_start_y),
                size=(track[1] - track[0], self.read_height),
                fill=self.colors['R']
            ))
        
        # 保存文件
        if output_path.endswith('.pdf'):
            temp_svg = output_path.replace('.pdf', '.svg')
            dwg.saveas(temp_svg)
            try:
                cairosvg.svg2pdf(url=temp_svg, write_to=output_path)
                Path(temp_svg).unlink()
            except Exception as e:
                print(f"Error converting to PDF: {e}")
                print(f"SVG file saved as: {temp_svg}")
        else:
            dwg.save() 