import pysam
import random
from .coordinate_utils import find_available_track_position

def find_exon_blocks(read):
    """Find exon positions and their operation types in the read alignment"""
    blocks = []
    read_pos = read.reference_start
    
    for op, length in read.cigartuples:
        # Match (0) or Mismatch (8)
        if op in [0, 8]:
            blocks.append((read_pos, length, 'match' if op == 0 else 'mismatch'))
            read_pos += length
        # Deletion (2)
        elif op == 2:
            blocks.append((read_pos, length, 'deletion'))
            read_pos += length
        # Insertion (1)
        elif op == 1:
            blocks.append((read_pos, length, 'insertion'))
        # Skip/Intron (3)
        elif op == 3:
            read_pos += length
    return blocks

def collect_read_alignments(bam_path, chrom, start_pos, end_pos, image_width, max_reads=100, method='continuous'):
    """Collect and process read alignments from BAM file with downsampling
    
    Args:
        method (str): How to handle many reads:
            - 'continuous': Similar to IGV, pack reads continuously 
            - 'downsample': Randomly sample max_reads number of reads
            - '3_end': Sort by 3' end and take top max_reads
            - '5_end': Sort by 5' end and take top max_reads
    """
    bam = pysam.AlignmentFile(bam_path, 'rb')
    forward_tracks = []
    reverse_tracks = []
    
    # Collect all reads first
    for read in bam.fetch(chrom, start_pos, end_pos):
        if read.is_unmapped or read.reference_start is None or not read.cigartuples:
            continue
            
        read_start = read.reference_start
        read_end = read.reference_end or (read_start + len(read.query_sequence))
        
        # Get exon blocks
        exon_blocks = find_exon_blocks(read)
        
        # Convert coordinates
        x_start = int((read_start - start_pos) * image_width / (end_pos - start_pos))
        x_end = int((read_end - start_pos) * image_width / (end_pos - start_pos))
        
        # Convert exon blocks
        image_blocks = []
        for block_start, block_length, op_type in exon_blocks:
            block_x_start = int((block_start - start_pos) * image_width / (end_pos - start_pos))
            block_x_end = int((block_start + block_length - start_pos) * image_width / (end_pos - start_pos))
            image_blocks.append((block_x_start, block_x_end, op_type))
        
        x_start = max(0, min(x_start, image_width))
        x_end = max(0, min(x_end, image_width))
        
        if x_end > x_start:
            if read.is_reverse:
                reverse_tracks.append((x_start, x_end, 0, read, image_blocks))
            else:
                forward_tracks.append((x_start, x_end, 0, read, image_blocks))

    # Handle large number of reads based on method
    if method == 'downsample' and len(forward_tracks) + len(reverse_tracks) > max_reads:
        # Randomly sample reads
        all_reads = forward_tracks + reverse_tracks
        sampled_indices = random.sample(range(len(all_reads)), max_reads)
        sampled_reads = [all_reads[i] for i in sampled_indices]
        forward_tracks = [r for r in sampled_reads if not r[3].is_reverse]
        reverse_tracks = [r for r in sampled_reads if r[3].is_reverse]
        
    elif method == '3_end' and len(forward_tracks) + len(reverse_tracks) > max_reads:
        # Sort by 3' end position
        forward_tracks.sort(key=lambda x: x[1], reverse=True)
        reverse_tracks.sort(key=lambda x: x[0])
        forward_tracks = forward_tracks[:max_reads//2]
        reverse_tracks = reverse_tracks[:max_reads//2]
        
    elif method == '5_end' and len(forward_tracks) + len(reverse_tracks) > max_reads:
        # Sort by 5' end position
        forward_tracks.sort(key=lambda x: x[0])
        reverse_tracks.sort(key=lambda x: x[1], reverse=True)
        forward_tracks = forward_tracks[:max_reads//2]
        reverse_tracks = reverse_tracks[:max_reads//2]
    
    # For 'continuous' method, keep all reads and let display handle packing
    forward_tracks.sort(key=lambda x: x[0])
    reverse_tracks.sort(key=lambda x: x[0])
    
    return forward_tracks, reverse_tracks 