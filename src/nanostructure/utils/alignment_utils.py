import pysam
import random
from .coordinate_utils import find_available_track_position
import re

def find_exon_blocks(read):
    """Find exon positions and their operation types in the read alignment
    
    Returns:
        list of tuples: (position, length, operation_type, sequence)
    """
    blocks = []
    current_pos = read.reference_start
    query_pos = 0
    
    # Get MD tag for accurate mismatch information
    mdtag = read.get_tag("MD")
    mismatch_pos = []
    
    # Parse MD tag to find mismatches
    for match in re.finditer(r'(\d+)|(\^[A-Z]+)|([A-Z])', mdtag):
        if match.group(1):  # Matched bases
            current_pos += int(match.group(1))
        elif match.group(2):  # Deletion
            continue
        elif match.group(3):  # Mismatch
            mismatch_pos.append(current_pos)
            current_pos += 1
    
    # Reset position for CIGAR parsing
    current_pos = read.reference_start
    
    for op, length in read.cigartuples:
        if op == 0:  # Match/Mismatch
            # Split the match/mismatch region based on mismatch positions
            region_start = current_pos
            for pos in range(current_pos, current_pos + length):
                if pos in mismatch_pos:
                    # Add match block before mismatch if exists
                    if pos > region_start:
                        blocks.append((region_start, pos - region_start, 'match', None))
                    # Add mismatch block
                    blocks.append((pos, 1, 'mismatch', None))
                    region_start = pos + 1
            # Add remaining match block if exists
            if region_start < current_pos + length:
                blocks.append((region_start, current_pos + length - region_start, 'match', None))
            
            current_pos += length
            query_pos += length
            
        elif op == 1:  # Insertion
            blocks.append((current_pos, length, 'insertion', None))
            query_pos += length
            
        elif op == 2:  # Deletion
            blocks.append((current_pos, length, 'deletion', None))
            current_pos += length
            
        elif op == 3:  # Skip/Intron
            blocks.append((current_pos, length, 'skip', None))
            current_pos += length
            
        elif op == 4:  # Soft clipping
            blocks.append((current_pos, length, 'soft_clip', None))
            query_pos += length
            
        elif op == 5:  # Hard clipping
            blocks.append((current_pos, length, 'hard_clip', None))
    
    return blocks

def collect_read_alignments(bam_path, chrom, start_pos, end_pos, image_width, max_reads=100, method='continuous'):
    """Collect and process read alignments from BAM file with downsampling
    
    Args:
        method (str): How to handle many reads:
            - 'continuous': Similar to IGV, pack reads continuously 
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
        for block_start, block_length, op_type, sequence in exon_blocks:
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

    
    # if method == 'downsample' and len(forward_tracks) + len(reverse_tracks) > max_reads:
    #     # Randomly sample reads
    #     all_reads = forward_tracks + reverse_tracks
    #     sampled_indices = random.sample(range(len(all_reads)), max_reads)
    #     sampled_reads = [all_reads[i] for i in sampled_indices]
    #     forward_tracks = [r for r in sampled_reads if not r[3].is_reverse]
    #     reverse_tracks = [r for r in sampled_reads if r[3].is_reverse]
        
    if method == '3_end' and len(forward_tracks) + len(reverse_tracks) > max_reads:
        # Sort by 3' end position
        forward_tracks.sort(key=lambda x: x[1], reverse=True)
        reverse_tracks.sort(key=lambda x: x[0])
        forward_ratio = len(forward_tracks) / (len(forward_tracks) + len(reverse_tracks))
        forward_max = int(max_reads * forward_ratio)
        reverse_max = max_reads - forward_max
        forward_tracks = forward_tracks[:forward_max]
        reverse_tracks = reverse_tracks[:reverse_max]
        
    elif method == '5_end' and len(forward_tracks) + len(reverse_tracks) > max_reads:
        # Sort by 5' end position
        forward_tracks.sort(key=lambda x: x[0])
        reverse_tracks.sort(key=lambda x: x[1], reverse=True)
        # calculate the ratio of forward reads
        forward_ratio = len(forward_tracks) / (len(forward_tracks) + len(reverse_tracks))
        forward_max = int(max_reads * forward_ratio)
        reverse_max = max_reads - forward_max
        forward_tracks = forward_tracks[:forward_max]
        reverse_tracks = reverse_tracks[:reverse_max]
        
    elif method == 'continuous':
        packed_forward = []
        packed_reverse = []
        
        for read in forward_tracks:
            track = find_available_track_position(read[0], read[1], packed_forward)
            packed_forward.append((read[0], read[1], track, read[3], read[4]))
            
        # Pack reverse reads
        for read in reverse_tracks:
            track = find_available_track_position(read[0], read[1], packed_reverse)
            packed_reverse.append((read[0], read[1], track, read[3], read[4]))
            
        forward_tracks = packed_forward
        reverse_tracks = packed_reverse
    
    # Only sort if not using continuous method
    if method != 'continuous':
        forward_tracks.sort(key=lambda x: x[0])
        reverse_tracks.sort(key=lambda x: x[0])
    
    return forward_tracks, reverse_tracks 