import json
from pathlib import Path
from .utils.drawing_utils import render_genomic_coordinates
from .utils.alignment_utils import collect_read_alignments
# from .utils.renderers.png_renderer import PNGRenderer
from .utils.renderers.vector_renderer import VectorRenderer
from .utils.coordinates.gene_coordinates import GeneCoordinates
from .utils.coordinates.drawing_coordinates import DrawingCoordinates
from .utils.coordinates.scale import XScale
from .config import COLORS

def parse_position(position_str):
    
    try:
        chrom, pos_range = position_str.split(':')
        start, end = map(int, pos_range.split('-'))
        return {'chrom': chrom, 'start': start, 'end': end}
    except:
        raise ValueError("Position must be in format 'chr1:1000-2000'")

def render_alignment_snapshot(bam_path, position=None, transcript=None, output_path=None, 
                            title=None, strand_direction="B", format="svg",
                            image_width=1000, read_height=None, track_spacing=None,
                            gtf_file=None, max_reads=100, flanking=100,
                            read_display_method='continuous'):
    """Generate alignment visualization snapshot for specified genomic region or transcript
    
    Args:
        ...
        read_display_method (str): How to handle many reads:
            - 'continuous': Similar to IGV, pack reads continuously (default)
            - 'downsample': Randomly sample max_reads number of reads
            - '3_end': Sort by 3' end and take top max_reads
            - '5_end': Sort by 5' end and take top max_reads
    """
    
    coord = DrawingCoordinates(
        width=image_width,
        height=50 
    )
    
    if transcript and gtf_file:
        coords = coord.get_transcript_coordinates(gtf_file, transcript)
        coords['start'] -= flanking
        coords['end'] += flanking
        coord.set_gene_annotation(gtf_file)
    elif position:
        coords = parse_position(position)
    else:
        raise ValueError("Either position or both transcript and gtf_file must be provided")
    
    if coords['start'] > coords['end']:
        coords['start'], coords['end'] = coords['end'], coords['start']
    
    # 更新坐标对象的属性
    coord.chrom = coords['chrom']
    coord.start_pos = coords['start']
    coord.end_pos = coords['end']
    
    # 创建并设置比例尺
    xscale = XScale(coords['start'], coords['end'], image_width)
    coord.xscale = xscale
    
    # 收集读取比对
    forward_tracks, reverse_tracks = collect_read_alignments(
        bam_path, coords['chrom'], coords['start'], coords['end'], 
        image_width, max_reads=max_reads, method=read_display_method
    )
    
    # 根据strand_direction过滤tracks
    if strand_direction == "F":
        reverse_tracks = []
    elif strand_direction == "R":
        forward_tracks = []
    elif strand_direction != "B":
        raise ValueError('strand_direction must be one of: "F", "R", "B"')
    
    # 排序reads
    forward_tracks.sort(key=lambda x: (x[0], (x[1] - x[0])))
    reverse_tracks.sort(key=lambda x: (x[0], (x[1] - x[0])))
    
    
    # if format.lower() == "png":
    #     renderer = PNGRenderer(colors, image_width, read_height, track_spacing)
    # else:
    renderer = VectorRenderer(COLORS, image_width, read_height, track_spacing)
    
    renderer.coordinates = coord
    coord.renderer = renderer
    
    renderer.render(forward_tracks, reverse_tracks, output_path, title)

