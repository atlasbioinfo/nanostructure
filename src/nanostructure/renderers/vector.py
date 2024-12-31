import svgwrite
import cairosvg
from pathlib import Path
from ..core.renderer import BaseRenderer
from ..components.axis import Axis
from ..components.gene import GeneComponent
from ..components.reads import ReadsComponent
from ..components.title import Title
from ..core.layout import LayoutManager
from ..config.margins import MARGINS

class VectorRenderer(BaseRenderer):
    """Vector format (SVG/PDF) renderer implementation"""
    
    def render(self, forward_tracks, reverse_tracks, output_path, title=None):
        """Render tracks to SVG/PDF format"""
        # Store tracks data for later use
        self.forward_tracks = forward_tracks
        self.reverse_tracks = reverse_tracks
        
        # Initialize layout manager
        layout_manager = LayoutManager(MARGINS, self.image_width)
        
        # Ensure coordinates are calculated
        if hasattr(self, 'coordinates'):
            self.coordinates.set_font()  # Set default font
            self.coordinates.calculate_ticks()  # Calculate tick positions
        
        # Create components
        components = []
        
        # Add title component (if provided)
        if title:
            title_layout = layout_manager.add_component('title')
            components.append((Title(title), title_layout))
        
        # Add axis component
        axis_layout = layout_manager.add_component('axis')
        components.append((
            Axis(self.coordinates.start_pos, self.coordinates.end_pos),
            axis_layout
        ))
        
        # Add gene model component
        gene_layout = layout_manager.add_component('gene_model')
        if hasattr(self.coordinates, 'gene_data'):
            components.append((
                GeneComponent(self.coordinates.gene_data),
                gene_layout
            ))
        
        # Add reads component
        reads_layout = layout_manager.add_component('reads')
        components.append((
            ReadsComponent(forward_tracks, reverse_tracks),
            reads_layout
        ))
        
        # Create SVG canvas and store it as instance attribute
        self.dwg = self._create_drawing(output_path, layout_manager.current_y)
        
        # Render background
        self._render_background(self.dwg)
        
        # Render all components
        for component, layout in components:
            component.render(self, layout)
        
        self._save_drawing(self.dwg, output_path)
        
    def _create_drawing(self, output_path, height):
        """Create and initialize SVG drawing"""
        dwg = svgwrite.Drawing(
            output_path,
            size=(self.image_width, height)
        )
        
        # Add metadata
        metadata = dwg.g(style="display:none")
        metadata.add(dwg.text("Created by NanoStructure (Haopeng Yu)", id="creator"))
        metadata.add(dwg.text("Generated using NanoStructure", id="software"))
        metadata.add(dwg.text("https://github.com/atlasbioinfo/nanostructure", id="github"))
        dwg.add(metadata)
        
        return dwg
    
    def _render_background(self, dwg):
        """Render background rectangle"""
        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(self.image_width, dwg.attribs['height']),
            fill=self.colors['background']
        ))
    
    # 渲染器接口方法
    def draw_text(self, text, position, color, font_family=None, font_size=None):
        """Draw text element"""
        # Use font settings from coordinates if available
        if hasattr(self, 'coordinates') and hasattr(self.coordinates, 'font'):
            font_family = font_family or self.coordinates.font['family']
            font_size = font_size or f"{self.coordinates.font['size']}px"
        else:
            font_family = font_family or 'Arial'
            font_size = font_size or '12px'
        
        self.dwg.add(self.dwg.text(
            text,
            insert=position,
            fill=color,
            font_family=font_family,
            font_size=font_size
        ))
    
    def draw_line(self, start, end, color, width=1):
        """Draw line element"""
        self.dwg.add(self.dwg.line(
            start=start,
            end=end,
            stroke=color,
            stroke_width=width
        ))
    
    def draw_rectangle(self, position, size, color, opacity=1):
        """Draw rectangle element"""
        self.dwg.add(self.dwg.rect(
            insert=position,
            size=size,
            fill=color,
            fill_opacity=opacity
        ))
    
    def draw_polyline(self, points, color, width=1):
        """Draw polyline element"""
        self.dwg.add(self.dwg.polyline(
            points=points,
            stroke=color,
            fill='none',
            stroke_width=width
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
