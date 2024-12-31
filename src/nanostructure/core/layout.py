class LayoutManager:
    """管理可视化组件的布局"""
    
    def __init__(self, margins, width):
        self.margins = margins
        self.width = width
        self.current_y = 0
        self.components = {}
        
    def add_component(self, component_type):
        """添加组件并计算其位置"""
        margin = self.margins[component_type]
        start_y = self.current_y + margin['top']
        
        component_layout = {
            'type': component_type,
            'y_start': start_y,
            'y_end': start_y + margin['height'],
            'x_start': margin['left'],
            'x_end': self.width - margin['right'],
            'width': self.width - margin['left'] - margin['right'],
            'height': margin['height'],
            'margins': margin
        }
        
        self.components[component_type] = component_layout
        self.current_y = component_layout['y_end'] + margin['bottom']
        
        return component_layout
    
    def get_component(self, component_type):
        """
        Get layout information for a specific component
        """
        return self.components.get(component_type) 