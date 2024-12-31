from .visualizer import render_alignment_snapshot
import click

@click.command()
@click.option('--bam', '-b', type=click.Path(exists=True), required=True, help='BAM file path')
@click.option('--position', '-p', type=str, help='Genomic position (e.g., "chr1:1000-2000")')
@click.option('--transcript', '-t', type=str, help='Transcript name')
@click.option('--output', '-o', default='output.png', help='Output image path')
@click.option('--title', help='Title for the visualization', default='NanoStructure')
@click.option('--gtf', '-g', type=click.Path(exists=True), help='Gene annotation GTF file')
@click.option('--strand-direction', '-s', type=click.Choice(['F', 'R', 'B']), default='B',
              help='Strand direction to display (F=Forward, R=Reverse, B=Both)')
@click.option('--image-width', '-w', type=int, default=1000, help='Width of the output image')
@click.option('--read-height', '-h', type=int, help='Height of each read track')
@click.option('--track-spacing', '-s', type=int, help='Spacing between tracks')
@click.option('--max-reads', '-m', type=int, default=100, help='Maximum number of reads to display')
@click.option('--flanking', type=int, default=100, help='Flanking region size around gene')
def main(bam, position, transcript, output, title, gtf, strand_direction, 
         image_width, read_height, track_spacing, max_reads, flanking):
    """Create BAM alignment visualization at specified genomic position or gene."""
    render_alignment_snapshot(
        bam_path=bam,
        position=position,
        transcript=transcript,
        output_path=output,
        title=title,
        gtf_file=gtf,
        strand_direction=strand_direction,
        image_width=image_width,
        read_height=read_height,
        track_spacing=track_spacing,
        max_reads=max_reads,
        flanking=flanking
    ) 