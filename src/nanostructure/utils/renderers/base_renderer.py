class BaseRenderer:
    """Base renderer with common functionality"""
    def __init__(self, colors, image_width, read_height=None, track_spacing=None):
        self.colors = colors
        self.image_width = image_width
        self.read_height = read_height or 8  # 默认read高度
        self.track_spacing = track_spacing or 2  # 默认track间距
        self.max_tracks = 100  # 添加最大track数限制
        
        
        self.min_total_height = 400
        self.max_total_height = 500
        
        
        self.margin = {
            'top': 10,      
            'bottom': 100,   
            'left': 150,     
            'right': 100     
        }
        
        self.target_aspect_ratio = 16/9

    def calculate_dimensions(self, forward_tracks, reverse_tracks):
        """Calculate optimal dimensions for visualization"""
        total_tracks = len(forward_tracks) + len(reverse_tracks)
        
        # 计算初始总高度
        potential_height = (self.margin['top'] + 
                          (total_tracks * (self.read_height + self.track_spacing)) +
                          self.margin['bottom'])
        
        # 如果潜在高度超过最大值，进行压缩
        if potential_height > self.max_total_height:
            # 计算可用高度(不包括边距)
            available_height = self.max_total_height - self.margin['top'] - self.margin['bottom']
            
            # 最小高度配置
            min_read_height = 0.5  # 最小read高度
            min_track_spacing = 0.25  # 最小间距
            
            # 计算使用最小配置时的高度
            min_total_height = (self.margin['top'] + 
                              (total_tracks * (min_read_height + min_track_spacing)) +
                              self.margin['bottom'])
            
            # 在最小配置和原始配置之间进行等比例压缩
            ratio = available_height / (total_tracks * (self.read_height + self.track_spacing))
            
            self.read_height = max(min_read_height, self.read_height * ratio)
            self.track_spacing = max(min_track_spacing, self.track_spacing * ratio)
            
            # 如果压缩后的高度超过max_total_height，更新max_total_height为最小值
            if min_total_height > self.max_total_height:
                self.max_total_height = min_total_height
                return min_total_height
            
            return self.max_total_height
            
        # 如果不需要压缩，返回原始高度
        return potential_height

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