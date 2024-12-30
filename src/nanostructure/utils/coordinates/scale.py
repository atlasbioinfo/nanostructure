class XScale:
    """Handle x-axis scaling calculations"""
    
    def __init__(self, start, end, width):
        self.xmap = {}
        scale = width / (end - start)
        for pos in range(start, end + 1):
            cpos = int((pos - start) * scale)
            self.xmap[pos] = {
                'cpos': cpos,
                'spos': max(0, cpos - 1),
                'epos': min(width, cpos + 1)
            } 