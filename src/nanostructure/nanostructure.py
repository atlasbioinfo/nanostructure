import click
from .visualizer import render_alignment_snapshot

@click.command()
@click.option('--bam', '-b', type=click.Path(exists=True), required=True, help='BAM file path')
@click.option('--position', '-p', type=str, help='Genomic position (e.g., "chr1:1000-2000")')
@click.option('--gene', '-n', type=str, help='Gene name')
@click.option('--output', '-o', default='output.png', help='Output image path')
@click.option('--title', '-t', help='Title for the visualization')
@click.option('--gtf', '-g', type=click.Path(exists=True), help='Gene annotation GTF file')
def main(bam, position, gene, output, title, gtf):
    """Create BAM alignment visualization at specified genomic position or gene."""
    if not position and not gene:
        raise click.UsageError("Either --position or --gene must be specified")
    if position and gene:
        raise click.UsageError("Cannot specify both --position and --gene")
    
    if gene and not gtf:
        raise click.UsageError("GTF file is required when specifying a gene name")

    render_alignment_snapshot(
        bam_path=bam,
        position=position,
        gene_name=gene,
        output_path=output,
        title=title,
        gtf_file=gtf
    )

if __name__ == "__main__":
    main() 