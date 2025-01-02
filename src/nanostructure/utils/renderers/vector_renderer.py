import svgwrite
import cairosvg
from pathlib import Path
from .base_renderer import BaseRenderer
from ...config import TITLE

class VectorRenderer(BaseRenderer):
    """Vector format (SVG/PDF) renderer implementation"""
    
    def render(self, forward_tracks, reverse_tracks, output_path, title=None):
        """Render tracks to SVG/PDF format"""
        title_data = {
            'text': title,
            'position': (TITLE['left'], TITLE['top']),
            'color': TITLE['color'],
            'font_size': TITLE['font_size']
        }
        
        title_height = title_data['font_size'] * 1.5 if title else 0
        
        render_data = self._render_common(forward_tracks, reverse_tracks, None)
        
        # Add bottom margin (e.g., 20 pixels)
        render_data['dimensions']['height'] += 100
        
        if title:
            render_data['dimensions']['height'] += title_height
            
        dwg = self._create_drawing(output_path, render_data)
        
        if title:
            self._draw_title(dwg, title_data)
        
        title_offset = title_height if title else 0
        
        if hasattr(self, 'coordinates'):
            gene_y = self._draw_coordinates(dwg, title_offset)
        
        # Pass gene_y to _draw_tracks
        self._draw_tracks(dwg, render_data['tracks'], gene_y)
        
        self._save_drawing(dwg, output_path)
    
    def _create_drawing(self, output_path, render_data):
        """Create and initialize the SVG drawing"""
        dwg = svgwrite.Drawing(output_path, size=(render_data['dimensions']['width'],
                                                render_data['dimensions']['height']))
        
        # Add metadata using text elements in a hidden group
        metadata = dwg.g(style="display:none")
        metadata.add(dwg.text("Created by NanoStructure (Haopeng Yu)", id="creator"))
        metadata.add(dwg.text("Generated using NanoStructure", id="software"))
        metadata.add(dwg.text("https://github.com/atlasbioinfo/nanostructure", id="github"))
        dwg.add(metadata)
        
        # Add background rectangle
        dwg.add(dwg.rect(insert=(0, 0),
                        size=(render_data['dimensions']['width'],
                              render_data['dimensions']['height']),
                        fill=self.colors['background']))
        return dwg
    
    def _draw_coordinates(self, dwg, title_offset):
        """Draw coordinate system including axis, ticks, and labels"""
        coord = self.coordinates
        if coord.font is None:
            coord.set_font()
        coord.resize_height()
        coord.calculate_ticks()
        
        coord_data = coord.get_render_data(30+title_offset)
        
        # Draw chromosome label with offset
        if 'chrom_label' in coord_data:
            self._draw_chrom_label(dwg, coord_data['chrom_label'], coord.font_size)
        
        # Draw axis and ticks
        self._draw_axis_and_ticks(dwg, coord_data, coord)
        
        # Draw gene structure and return gene_y_end
        gene_y_end = self._draw_gene_structure(dwg, coord, coord_data['axis']['y'])
        return gene_y_end
    
    def _draw_chrom_label(self, dwg, label_data, font_size):
        """Draw chromosome label"""
        dwg.add(dwg.text(label_data['text'],
                        insert=label_data['position'],
                        font_family='Arial',
                        font_size=f"{font_size}px",
                        font_weight="bold",
                        text_anchor="middle",
                        fill=label_data['color']))
    
    def _draw_axis_and_ticks(self, dwg, coord_data, coord):
        """Draw main axis line, ticks and labels"""
        # Draw main axis
        dwg.add(dwg.line(
            start=coord_data['axis']['line'][0],
            end=coord_data['axis']['line'][1],
            stroke=coord_data['axis']['color'],
            stroke_width=coord_data['axis']['width']
        ))
        
        # Draw ticks and labels
        for tick in coord_data['ticks']:
            dwg.add(dwg.line(
                start=tick['start'],
                end=tick['end'],
                stroke=tick['color'],
                stroke_width=tick['width']
            ))
        
        for label in coord_data['labels']:
            dwg.add(dwg.text(
                label['text'],
                insert=label['position'],
                text_anchor='middle',
                font_family='Arial',
                font_size=f"{coord.font_size}px",
                fill=label['color']
            ))
    
    def _draw_gene_structure(self, dwg, coord, axis_y):
        """Draw gene structure including introns and exons"""
        gene_data, gene_y_end = coord.draw_gene_structure(axis_y)
        if not gene_data:
            return None
            
        # Draw gene components
        if gene_data['gene_name'] and gene_data['intron_line']:
            self._draw_gene_name_and_intron(dwg, gene_data)
        self._draw_exons(dwg, gene_data)
        
        return gene_y_end
    
    def _draw_gene_name_and_intron(self, dwg, gene_data):
        """Draw gene name and intron line with arrows"""
        # Draw gene name
        dwg.add(dwg.text(gene_data['gene_name'],
                        insert=gene_data['intron_line']['label_position'],
                        font_family='Arial',
                        font_size='12px',
                        fill=gene_data['style']['text_color']))
        
        # Draw intron line
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
    
    def _draw_exons(self, dwg, gene_data):
        """Draw exon blocks"""
        for exon in gene_data['exons']:
            dwg.add(dwg.rect(
                insert=exon['position'],
                size=exon['size'],
                fill=gene_data['style']['exon_color'],
                fill_opacity=gene_data['style'].get('exon_opacity', 1)
            ))
    
    def _draw_tracks(self, dwg, tracks_data, gene_y):
        """Draw forward and reverse tracks"""
        # 添加总计数器
        total_counts = {
            'match': 0,
            'mismatch': 0,
            'insertion': 0,
            'deletion': 0,
            'soft_clip': 0,
            'hard_clip': 0,
            'skip': 0
        }
        
        track_start_y = gene_y
        
        for direction in ['forward', 'reverse']:
            color_key = 'F' if direction == 'forward' else 'R'
            for track_data in tracks_data[direction]:
                # 统计每个block的操作类型
                for _, _, op_type in track_data['track'][4]:  # blocks在track[4]
                    total_counts[op_type] += 1
                self._draw_single_track(dwg, track_data, track_start_y, self.colors['reads'][color_key])
        
        # 只打印总计
        print("\n=== Operation Statistics ===")
        for op_type, count in total_counts.items():
            print(f"{op_type}: {count}")
    
    def _draw_single_track(self, dwg, track_data, track_start_y, base_color):
        """Draw a single track including intron lines and exon blocks"""
        track = track_data['track']
        x_start, x_end, _, read, blocks = track
        y = track_data['y'] + track_start_y
        
        # Draw intron line first (as background)
        dwg.add(dwg.line(
            start=(x_start, y + self.read_height/2),
            end=(x_end, y + self.read_height/2),
            stroke='#A6A6A6',
            stroke_width=1
        ))
        
        # Draw blocks with appropriate colors
        for block_start, block_end, op_type in blocks:
            if op_type == 'skip':
                continue  # Skip already drawn as intron line
            
            color = {
                'match': base_color,
                'mismatch': '#FF0000',  # Red
                'insertion': '#304FFE',  # Blue
                'deletion': '#7DFF6F',   # Green
            }.get(op_type, base_color)
            
            dwg.add(dwg.rect(
                insert=(block_start, y),
                size=(block_end - block_start, self.read_height),
                fill=color
            ))
    
    def _save_drawing(self, dwg, output_path):
        """Save drawing as SVG or convert to PDF"""
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
    
    def _draw_title(self, dwg, title_data):
        """Draw title text"""
        if title_data['text']:
            dwg.add(dwg.text(
                title_data['text'],
                insert=title_data['position'],
                font_family='Arial',
                font_size=f"{title_data['font_size']}px",
                fill=title_data['color']
            )) 