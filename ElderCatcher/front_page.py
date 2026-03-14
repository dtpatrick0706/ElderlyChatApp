from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from rounded_button import RoundedButton


class FrontPage(Screen):
    """Front/Main page with navigation buttons"""
    
    # Light yellow background color (very light yellow)
    BACKGROUND_COLOR = (1.0, 0.98, 0.85, 1.0)  # Very light yellow
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'front_page'
        
        # Create main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding='20dp',
            spacing='20dp'
        )
        
        # Set background color
        with main_layout.canvas.before:
            Color(*self.BACKGROUND_COLOR)
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        # Bind to update background when size changes
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Create button layout (middle of screen) - optimized for phone
        button_layout = BoxLayout(
            orientation='vertical',
            spacing='15dp',
            size_hint=(0.85, 0.7),  # Use relative sizing for phone
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Create buttons with rounded corners - optimized for phone
        chat_button = RoundedButton(
            text='Chat',
            font_size='28sp',  # Slightly smaller for phone
            size_hint_y=0.2,  # Use relative sizing
            bg_color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        chat_button.bind(on_press=self.go_to_chat)
        
        schedule_button = RoundedButton(
            text='Schedule',
            font_size='28sp',
            size_hint_y=0.2,
            bg_color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        schedule_button.bind(on_press=self.go_to_schedule)
        
        practice_button = RoundedButton(
            text='Practice',
            font_size='28sp',
            size_hint_y=0.2,
            bg_color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        practice_button.bind(on_press=self.go_to_practice)
        
        help_button = RoundedButton(
            text='Help',
            font_size='28sp',
            size_hint_y=0.2,
            bg_color=(1, 0, 0, 1)  # Red background
        )
        # Help button is placeholder for now
        
        # Add buttons to layout
        button_layout.add_widget(chat_button)
        button_layout.add_widget(schedule_button)
        button_layout.add_widget(practice_button)
        button_layout.add_widget(help_button)
        
        # Add button layout to main layout (centered)
        main_layout.add_widget(BoxLayout(size_hint_y=0.15))  # Spacer top
        main_layout.add_widget(button_layout)
        main_layout.add_widget(BoxLayout(size_hint_y=0.15))  # Spacer bottom
        
        self.add_widget(main_layout)
    
    def _update_rect(self, instance, value):
        """Update background rectangle size and position"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def go_to_chat(self, instance):
        """Navigate to chat page"""
        self.manager.current = 'chat_page'
    
    def go_to_schedule(self, instance):
        """Navigate to schedule page"""
        self.manager.current = 'schedule_page'
    
    def go_to_practice(self, instance):
        """Navigate to practice page"""
        self.manager.current = 'practice_page'

