def calculate_tick_interval(range_size):
    """Calculate appropriate tick interval based on genomic range size"""
    if range_size <= 1000:
        return 100
    elif range_size <= 5000:
        return 500
    return 1000

def find_available_track_position(read_start, read_end, occupied_positions):
    """Find first available vertical track position for read placement"""
    track_pos = 0
    while True:
        can_place = True
        for existing_read in occupied_positions:
            if (read_start <= existing_read[1] and 
                read_end >= existing_read[0] and 
                track_pos == existing_read[2]):
                can_place = False
                break
        if can_place:
            return track_pos
        track_pos += 1 