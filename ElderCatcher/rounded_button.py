from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty, NumericProperty


class RoundedButton(Button):
    """Custom button with rounded corners"""
    
    # Custom property for background color
    bg_color = ListProperty([0.7, 0.7, 0.7, 1])
    corner_radius = NumericProperty(20)
    
    def __init__(self, **kwargs):
        # Extract bg_color if provided, otherwise use background_color if set
        bg_color_arg = None
        if 'bg_color' in kwargs:
            bg_color_arg = kwargs.pop('bg_color')
        elif 'background_color' in kwargs:
            bg = kwargs['background_color']
            if bg != (0, 0, 0, 0) and bg != [0, 0, 0, 0]:
                bg_color_arg = bg
                kwargs.pop('background_color')
        
        # Set default background to transparent so we can use our custom rounded rectangle
        if 'background_color' not in kwargs:
            kwargs['background_color'] = (0, 0, 0, 0)
        
        super().__init__(**kwargs)
        
        # Set bg_color after initialization
        if bg_color_arg:
            self.bg_color = bg_color_arg
        
        self._rect = None
        self.bind(pos=self._update_rect, size=self._update_rect, bg_color=self._update_rect)
        self._update_rect()
    
    def _update_rect(self, *args):
        """Update the rounded rectangle background"""
        # Clear canvas.before and recreate (simpler approach)
        self.canvas.before.clear()
        
        # Create rounded rectangle
        with self.canvas.before:
            Color(*self.bg_color)
            radius = [self.corner_radius]
            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=radius
            )
