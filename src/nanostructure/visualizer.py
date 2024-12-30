from pathlib import Path
from .utils.drawing_utils import render_genomic_coordinates
from .utils.alignment_utils import collect_read_alignments
from .utils.renderers.png_renderer import PNGRenderer
from .utils.renderers.vector_renderer import VectorRenderer
from .utils.coordinates.drawing_coordinates import DrawingCoordinates
from .utils.coordinates.scale import XScale

def parse_position(position_str):
    """Parse position string in format 'chr1:1000-2000'"""
    try:
        chrom, pos_range = position_str.split(':')
        start, end = map(int, pos_range.split('-'))
        return {'chrom': chrom, 'start': start, 'end': end}
    except:
        raise ValueError("Position must be in format 'chr1:1000-2000'")

def render_alignment_snapshot(bam_path, position=None, transcript=None, output_path=None, 
                            title=None, strand_direction="B", format="pdf",
                            image_width=1000, read_height=None, track_spacing=None,
                            gtf_file=None, max_reads=100, flanking=100):
    """Generate alignment visualization snapshot for specified genomic region or transcript"""
    
    # 创建坐标对象
    coord = DrawingCoordinates(
        width=image_width,
        height=50  # 初始高度，后续会根据内容调整
    )
    
    # 获取基因组坐标和转录本信息
    if transcript and gtf_file:
        # 获取转录本坐标
        coords = coord.get_transcript_coordinates(gtf_file, transcript)
        # 添加侧翼区域
        coords['start'] -= flanking
        coords['end'] += flanking
        # 设置基因注释
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

    colors = {
        'F': '#163f63',
        'R': '#eb5252',
        'B': '#163f63',
        'background': 'white',
        'axis': 'black'
    }
    
    # 收集读取比对
    forward_tracks, reverse_tracks = collect_read_alignments(
        bam_path, coords['chrom'], coords['start'], coords['end'], 
        image_width, max_reads=max_reads
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
    
    # 创建渲染器
    if format.lower() == "png":
        renderer = PNGRenderer(colors, image_width, read_height, track_spacing)
    else:
        renderer = VectorRenderer(colors, image_width, read_height, track_spacing)
    
    # 设置渲染器的坐标对象
    renderer.coordinates = coord
    
    # 渲染图像
    renderer.render(forward_tracks, reverse_tracks, output_path, title)

