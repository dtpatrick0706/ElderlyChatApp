import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config

# Import all page modules
from front_page import FrontPage
from chat_page import ChatPage
from schedule_page import SchedulePage
from practice_page import PracticePage
from add_agenda_page import AddAgendaPage
from alarm_manager import AlarmManager
from sudoku_game import SudokuGamePage
from memory_game import MemoryGamePage

# Set window size to phone dimensions (typical Android phone size)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')  # Prevent resizing to maintain phone aspect ratio
Config.set('graphics', 'borderless', '0')  # Keep window borders


class ElderCatcherApp(App):
    """Main Kivy Application with ScreenManager"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alarm_manager = None
    
    def build(self):
        # Create screen manager
        sm = ScreenManager()
        
        # Add all screens
        sm.add_widget(FrontPage(name='front_page'))
        sm.add_widget(ChatPage(name='chat_page'))
        schedule_page = SchedulePage(name='schedule_page')
        sm.add_widget(schedule_page)
        sm.add_widget(PracticePage(name='practice_page'))
        sm.add_widget(AddAgendaPage(name='add_agenda_page'))
        sm.add_widget(SudokuGamePage(name='sudoku_game'))
        sm.add_widget(MemoryGamePage(name='memory_game'))
        
        # Set starting screen
        sm.current = 'front_page'
        
        # Initialize alarm manager with reference to schedule data and schedule page
        self.alarm_manager = AlarmManager(
            schedule_data_ref=schedule_page.schedule_data,
            schedule_page_ref=schedule_page
        )
        
        # Start alarm checking (checks time every 30 seconds)
        self.alarm_manager.start()
        
        return sm
    
    def on_stop(self):
        """Called when the app is stopped - stop alarm manager"""
        if self.alarm_manager:
            self.alarm_manager.stop()


if __name__ == '__main__':
    ElderCatcherApp().run()
