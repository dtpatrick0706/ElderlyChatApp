from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from rounded_button import RoundedButton


class PracticePage(Screen):
    """Practice page with games for cognitive health"""
    
    # Light yellow background color (very light yellow)
    BACKGROUND_COLOR = (1.0, 0.98, 0.85, 1.0)  # Very light yellow
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'practice_page'
        
        # Create main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding='10dp',
            spacing='10dp'
        )
        
        # Set background color
        with main_layout.canvas.before:
            Color(*self.BACKGROUND_COLOR)
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        # Bind to update background when size changes
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Back button with rounded corners - optimized for phone
        back_button = RoundedButton(
            text='← Back',
            font_size='20sp',  # Smaller for phone
            size_hint_y=None,
            height='50dp',  # Fixed height
            bg_color=(0.7, 0.7, 0.7, 1)
        )
        back_button.bind(on_press=self.go_back)
        main_layout.add_widget(back_button)
        
        # Title - optimized for phone
        title_label = Label(
            text='Practice Games',
            font_size='26sp',  # Smaller for phone
            size_hint_y=None,
            height='50dp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            bold=True,
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(title_label)
        
        # Subtitle
        subtitle_label = Label(
            text='Games for Entertainment and Cognitive Health',
            font_size='16sp',
            size_hint_y=None,
            height='40dp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            color=(0.3, 0.3, 0.3, 1)
        )
        main_layout.add_widget(subtitle_label)
        
        # Scrollable games section
        scroll_view = ScrollView(
            size_hint_y=1,  # Take remaining space
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        # Games container
        games_container = BoxLayout(
            orientation='vertical',
            spacing='12dp',
            padding='15dp',
            size_hint_y=None
        )
        games_container.bind(minimum_height=games_container.setter('height'))
        
        # List of games from outline
        games = [
            {'name': 'Sudoku', 'color': (0.8, 0.5, 0.2, 1), 'description': 'Number puzzle for logical thinking'},
            {'name': 'Card Memory Game', 'color': (0.6, 0.8, 0.4, 1), 'description': 'Match pairs to improve memory'},
        ]
        
        # Create game buttons
        for game in games:
            game_button = RoundedButton(
                text=game['name'],
                font_size='22sp',
                size_hint_y=None,
                height='80dp',
                bg_color=game['color']
            )
            game_button.bind(on_press=lambda instance, g=game: self.start_game(g))
            games_container.add_widget(game_button)
            
            # Game description
            desc_label = Label(
                text=game['description'],
                font_size='14sp',
                size_hint_y=None,
                height='35dp',
                halign='center',
                valign='middle',
                text_size=(None, None),
                color=(0.4, 0.4, 0.4, 1)
            )
            games_container.add_widget(desc_label)
        
        scroll_view.add_widget(games_container)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)
    
    def _update_rect(self, instance, value):
        """Update background rectangle size and position"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def start_game(self, game):
        """Handle game button press"""
        game_name = game['name']
        if game_name == 'Sudoku':
            self.manager.current = 'sudoku_game'
        elif game_name == 'Card Memory Game':
            self.manager.current = 'memory_game'
    
    def go_back(self, instance):
        """Navigate back to front page"""
        self.manager.current = 'front_page'

