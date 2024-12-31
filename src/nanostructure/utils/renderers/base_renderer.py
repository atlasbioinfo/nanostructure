class BaseRenderer:
    """Base renderer with common functionality"""
    def __init__(self, colors, image_width, read_height=None, track_spacing=None):
        self.colors = colors
        self.image_width = image_width
        self.read_height = read_height or 8  # 默认read高度
        self.track_spacing = track_spacing or 2  # 默认track间距
        self.max_tracks = 100  # 添加最大track数限制
        
        
        self.min_total_height = 400
        self.max_total_height = 1000
        
        
        self.margin = {
            'top': 10,      # 改为更小的值
            'bottom': 200,   
            'left': 150,     
            'right': 100     
        }
        
        self.target_aspect_ratio = 16/9

    def calculate_dimensions(self, forward_tracks, reverse_tracks):
        """Calculate optimal dimensions for visualization"""
        total_tracks = len(forward_tracks) + len(reverse_tracks)
        
        # 计算理想高度（考虑边距）
        available_width = self.image_width - self.margin['left'] - self.margin['right']
        ideal_height = min(self.max_total_height, 
                          max(self.min_total_height, 
                              available_width / self.target_aspect_ratio))
        
        # 计算可用高度（减去边距）
        available_height = ideal_height - self.margin['top'] - self.margin['bottom']
        
        # 计算单个track的理想高度
        single_track_height = available_height / max(1, total_tracks)
        base_read_height = max(2, int(single_track_height * 0.6))
        base_track_spacing = max(1, int(single_track_height * 0.4))
        
        # 如果没有指定高度和间距，计算最优值
        if self.read_height is None or self.track_spacing is None:
            scale_factor = min(1.0, available_height / 
                             (total_tracks * (base_read_height + base_track_spacing)))
            
            self.read_height = max(2, int(base_read_height * scale_factor))
            self.track_spacing = max(1, int(base_track_spacing * scale_factor))
        
        total_height = self.margin['top'] + (total_tracks * (self.read_height + self.track_spacing))
        
        # 如果高度超过最大值，重新调整read高度和间距
        if total_height > self.max_total_height:
            available_height = self.max_total_height - self.margin['top'] - self.margin['bottom']
            height_per_track = available_height / total_tracks
            self.read_height = max(2, int(height_per_track * 0.7))
            self.track_spacing = max(1, int(height_per_track * 0.3))
            total_height = self.max_total_height
            
        return total_height

    def _render_common(self, forward_tracks, reverse_tracks, title):
        """Common rendering logic for both PNG and Vector outputs"""
        # 计算总高度
        image_height = self.calculate_dimensions(forward_tracks, reverse_tracks)
        
        # 准备渲染数据
        render_data = {
            'dimensions': {
                'width': self.image_width,
                'height': image_height
            },
            'margins': self.margin,
            'read_height': self.read_height,
            'track_spacing': self.track_spacing,
            'colors': self.colors,
            'tracks': {
                'forward': [],
                'reverse': []
            }
        }
        
        # 计算起始位置
        current_y = self.margin['top']
        
        # Forward reads
        for i, track in enumerate(forward_tracks):
            y = current_y + (i * (self.read_height + self.track_spacing))
            render_data['tracks']['forward'].append({
                'track': track,
                'y': y
            })
        
        # Add spacing between forward and reverse tracks
        current_y += (len(forward_tracks) * (self.read_height + self.track_spacing)) + 20
        
        # Reverse reads
        for i, track in enumerate(reverse_tracks):
            y = current_y + (i * (self.read_height + self.track_spacing))
            render_data['tracks']['reverse'].append({
                'track': track,
                'y': y
            })
            
        return render_data

    def render(self, forward_tracks, reverse_tracks, output_path, title):
        """
        Abstract method to be implemented by specific renderers
        """
        raise NotImplementedError("Render method must be implemented by specific renderer") 

    def optimize_track_layout(self, tracks):
        """优化track布局"""
        total_tracks = len(tracks)
        if total_tracks > self.max_tracks:
            # 计算压缩比
            compression_ratio = self.max_tracks / total_tracks
            self.read_height = max(1, int(self.read_height * compression_ratio))
            self.track_spacing = max(0, int(self.track_spacing * compression_ratio)) 