from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from rounded_button import RoundedButton
import random


class MemoryGamePage(Screen):
    """Card Memory Game - Match pairs of cards"""
    
    BACKGROUND_COLOR = (1.0, 0.98, 0.85, 1.0)  # Very light yellow
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'memory_game'
        
        # Game state
        self.cards = []
        self.flipped_cards = []
        self.matched_pairs = 0
        self.total_pairs = 12  # 24 cards total, 12 pairs
        self.wrong_matches = 0  # Track wrong matches
        
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
        
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Back button
        back_button = RoundedButton(
            text='← Back',
            font_size='20sp',
            size_hint_y=None,
            height='50dp',
            bg_color=(0.7, 0.7, 0.7, 1)
        )
        back_button.bind(on_press=self.go_back)
        main_layout.add_widget(back_button)
        
        # Title
        title_label = Label(
            text='Card Memory Game',
            font_size='24sp',
            size_hint_y=None,
            height='50dp',
            halign='center',
            bold=True,
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(title_label)
        
        # Score/Status
        self.status_label = Label(
            text='Match the pairs!',
            font_size='18sp',
            size_hint_y=None,
            height='40dp',
            halign='center',
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Wrong matches counter
        self.counter_label = Label(
            text='Wrong matches: 0',
            font_size='16sp',
            size_hint_y=None,
            height='35dp',
            halign='center',
            color=(0.8, 0.2, 0.2, 1)
        )
        main_layout.add_widget(self.counter_label)
        
        # Cards grid (4 columns for 24 cards = 6 rows)
        self.cards_grid = GridLayout(
            cols=4,
            spacing='5dp',
            padding='10dp',
            size_hint_y=1
        )
        main_layout.add_widget(self.cards_grid)
        
        # Reset button
        reset_button = RoundedButton(
            text='New Game',
            font_size='18sp',
            size_hint_y=None,
            height='50dp',
            bg_color=(0.6, 0.8, 0.4, 1)
        )
        reset_button.bind(on_press=self.reset_game)
        main_layout.add_widget(reset_button)
        
        self.add_widget(main_layout)
        self.reset_game()
    
    def _update_rect(self, instance, value):
        """Update background rectangle"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def reset_game(self, instance=None):
        """Start a new game"""
        self.cards_grid.clear_widgets()
        self.flipped_cards = []
        self.matched_pairs = 0
        self.wrong_matches = 0
        
        # Create pairs: numbers 1-12, each appears twice (24 cards total)
        card_values = list(range(1, self.total_pairs + 1)) * 2
        random.shuffle(card_values)
        
        self.cards = []
        for i, value in enumerate(card_values):
            card = {
                'value': value,
                'index': i,
                'flipped': False,
                'matched': False
            }
            self.cards.append(card)
        
            # Create card buttons
        for card in self.cards:
            btn = Button(
                text='?',
                font_size='20sp',  # Smaller font for more cards
                bold=True
            )
            btn.card_data = card
            btn.bind(on_press=self.flip_card)
            self.cards_grid.add_widget(btn)
        
        self.status_label.text = 'Match the pairs!'
        self.counter_label.text = 'Wrong matches: 0'
    
    def flip_card(self, button):
        """Handle card flip"""
        card = button.card_data
        
        # Ignore if already flipped or matched
        if card['flipped'] or card['matched'] or len(self.flipped_cards) >= 2:
            return
        
        # Flip card
        card['flipped'] = True
        button.text = str(card['value'])
        button.background_color = (0.9, 0.9, 0.9, 1)
        self.flipped_cards.append((button, card))
        
        # Check for match if two cards are flipped
        if len(self.flipped_cards) == 2:
            self.check_match()
    
    def check_match(self):
        """Check if flipped cards match"""
        (btn1, card1), (btn2, card2) = self.flipped_cards
        
        if card1['value'] == card2['value']:
            # Match!
            card1['matched'] = True
            card2['matched'] = True
            btn1.background_color = (0.6, 0.8, 0.4, 1)
            btn2.background_color = (0.6, 0.8, 0.4, 1)
            self.matched_pairs += 1
            
            if self.matched_pairs == self.total_pairs:
                self.status_label.text = 'You won! 🎉'
            else:
                self.status_label.text = f'Match! {self.matched_pairs}/{self.total_pairs} pairs'
            
            self.flipped_cards = []
        else:
            # No match - increment wrong matches counter
            self.wrong_matches += 1
            self.counter_label.text = f'Wrong matches: {self.wrong_matches}'
            self.status_label.text = 'No match. Try again!'
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.flip_cards_back(), 1.0)
    
    def flip_cards_back(self):
        """Flip unmatched cards back"""
        for button, card in self.flipped_cards:
            card['flipped'] = False
            button.text = '?'
            button.background_color = (1, 1, 1, 1)
        self.flipped_cards = []
        self.status_label.text = 'Match the pairs!'
    
    def go_back(self, instance):
        """Navigate back to practice page"""
        self.manager.current = 'practice_page'
