from src.nanostructure.visualizer import render_alignment_snapshot

def main():
    render_alignment_snapshot(
        bam_path="./test/SQK-NBD114-24_barcode09_tagged_elongating.bam",
        transcript="ENST00000229239",
        output_path="./test/test_by_gene.svg",
        title="ATLAS test - By Gene Name",
        format="svg",
        gtf_file="./test/test.gff3"
    )

if __name__ == "__main__":
    main() 