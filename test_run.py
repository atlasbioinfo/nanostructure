from src.nanostructure.visualizer import render_alignment_snapshot

def main():
    # # Example 1: Using genomic position
    # render_alignment_snapshot(
    #     bam_path="./test/SQK-NBD114-24_barcode09_tagged_elongating.bam",
    #     position="12:6534016-6538871",
    #     output_path="test_by_position.png",
    #     title="ATLAS test - By Position",
    #     format="png",
    #     gtf_file="./test/Homo_sapiens.GRCh38.106.main.gff3"
    # )

    # # Example 2: Using gene name
    render_alignment_snapshot(
        bam_path="./test/SQK-NBD114-24_barcode09_tagged_elongating.bam",
        transcript="ENST00000229239",
        output_path="./test/test_by_gene.pdf",
        title="ATLAS test - By Gene Name",
        format="pdf",
        gtf_file="./test/Homo_sapiens.GRCh38.106.main.gff3"
    )

if __name__ == "__main__":
    main() 