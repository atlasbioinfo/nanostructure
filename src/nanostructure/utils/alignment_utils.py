import pysam
import random
from .coordinate_utils import find_available_track_position

def collect_read_alignments(bam_path, chrom, start_pos, end_pos, image_width, max_reads=100):
    """Collect and process read alignments from BAM file with downsampling"""
    bam = pysam.AlignmentFile(bam_path, 'rb')
    forward_tracks = []
    reverse_tracks = []
    
    # First pass: count total reads in region
    total_reads = sum(1 for _ in bam.fetch(chrom, start_pos, end_pos))
    
    # Calculate sampling fraction if needed
    fraction = 1.0 if max_reads <= 0 else min(1.0, (max_reads * 2) / total_reads)
    
    # Second pass: collect reads with sampling
    for read in bam.fetch(chrom, start_pos, end_pos):
        if fraction < 1.0 and random.random() > fraction:
            continue
            
        if read.is_unmapped or read.reference_start is None:
            continue
            
        read_start = read.reference_start
        read_end = read.reference_end or (read_start + len(read.query_sequence))
        
        # Convert to image coordinates
        x_start = int((read_start - start_pos) * image_width / (end_pos - start_pos))
        x_end = int((read_end - start_pos) * image_width / (end_pos - start_pos))
        
        # Ensure coordinates are within bounds
        x_start = max(0, min(x_start, image_width))
        x_end = max(0, min(x_end, image_width))
        
        if x_end > x_start:
            if read.is_reverse:
                reverse_tracks.append((x_start, x_end, 0, read))
            else:
                forward_tracks.append((x_start, x_end, 0, read))
    
    # Sort by start position for display
    forward_tracks.sort(key=lambda x: x[0])
    reverse_tracks.sort(key=lambda x: x[0])
    
    return forward_tracks, reverse_tracks 