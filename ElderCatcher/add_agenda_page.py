from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from datetime import datetime
from rounded_button import RoundedButton


class AddAgendaPage(Screen):
    """Page for adding agenda items to a specific date"""
    
    # Light yellow background color (very light yellow)
    BACKGROUND_COLOR = (1.0, 0.98, 0.85, 1.0)  # Very light yellow
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'add_agenda_page'
        self.target_date = None  # Date we're adding agenda items for
        self.schedule_data_ref = None  # Reference to schedule data from SchedulePage
        
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
        
        # Header with date display
        header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='100dp',
            spacing='5dp'
        )
        
        # Back button
        back_button = RoundedButton(
            text='← Back',
            font_size='20sp',
            size_hint_y=None,
            height='50dp',
            bg_color=(0.7, 0.7, 0.7, 1)
        )
        back_button.bind(on_press=self.go_back)
        header_layout.add_widget(back_button)
        
        # Date label
        self.date_label = Label(
            text='Select Date',
            font_size='22sp',
            size_hint_y=None,
            height='50dp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            bold=True,
            color=(0, 0, 0, 1)
        )
        header_layout.add_widget(self.date_label)
        
        main_layout.add_widget(header_layout)
        
        # Add new item section - fills remaining space
        add_section = BoxLayout(
            orientation='vertical',
            size_hint_y=1,
            spacing='8dp',  # Reduced spacing to bring time label closer to boxes
            padding='20dp'
        )
        
        add_label = Label(
            text='Add New Agenda Item:',
            font_size='20sp',
            size_hint_y=None,
            height='40dp',
            halign='left',
            valign='middle',
            text_size=(None, None),
            bold=True,
            color=(0, 0, 0, 1)
        )
        add_section.add_widget(add_label)
        
        # Title input field
        title_label = Label(
            text='Title (shown on calendar):',
            font_size='16sp',
            size_hint_y=None,
            height='30dp',
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        add_section.add_widget(title_label)
        
        self.title_input = TextInput(
            multiline=False,
            font_size='18sp',
            hint_text='Enter title (e.g., "Doctor Appointment")...',
            size_hint_y=None,
            height='55dp'
        )
        add_section.add_widget(self.title_input)
        
        # Time picker section
        time_label = Label(
            text='Time (24-hour format):',
            font_size='16sp',
            size_hint_y=None,
            height='30dp',
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        add_section.add_widget(time_label)
        
        # Time picker container (hour and minute spinners)
        time_picker_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='45dp',
            spacing='15dp'
        )
        
        # Hour spinner (0-23 for 24-hour format)
        hour_label = Label(
            text='Hour:',
            font_size='16sp',
            size_hint_x=None,
            width='60dp',
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        time_picker_layout.add_widget(hour_label)
        
        self.hour_spinner = Spinner(
            text='--',
            values=[str(i).zfill(2) for i in range(24)],  # 00-23
            size_hint_x=0.4,
            font_size='18sp'
        )
        time_picker_layout.add_widget(self.hour_spinner)
        
        # Minute spinner (00-59)
        minute_label = Label(
            text='Min:',
            font_size='16sp',
            size_hint_x=None,
            width='50dp',
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        time_picker_layout.add_widget(minute_label)
        
        self.minute_spinner = Spinner(
            text='--',
            values=[str(i).zfill(2) for i in range(60)],  # 00-59
            size_hint_x=0.4,
            font_size='18sp'
        )
        time_picker_layout.add_widget(self.minute_spinner)
        
        add_section.add_widget(time_picker_layout)
        
        # Description input field - takes remaining space
        desc_label = Label(
            text='Details (shown in agenda box):',
            font_size='16sp',
            size_hint_y=None,
            height='30dp',
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        add_section.add_widget(desc_label)
        
        self.desc_input = TextInput(
            multiline=True,
            font_size='18sp',
            hint_text='Enter details/description...',
            size_hint_y=None,
            height='120dp'  # Reduced height to prevent overlap
        )
        add_section.add_widget(self.desc_input)
        
        # Add button
        add_button = RoundedButton(
            text='Add Item',
            font_size='20sp',
            size_hint_y=None,
            height='60dp',
            bg_color=(0.2, 0.6, 0.8, 1)
        )
        add_button.bind(on_press=self.add_agenda_item)
        add_section.add_widget(add_button)
        
        main_layout.add_widget(add_section)
        
        self.add_widget(main_layout)
    
    def set_date(self, date, schedule_data_ref):
        """Set the target date and schedule data reference"""
        self.target_date = date
        self.schedule_data_ref = schedule_data_ref
        
        # Update date label
        if date == datetime.now().date():
            self.date_label.text = f"Today's Agenda\n{date.strftime('%B %d, %Y')}"
        else:
            self.date_label.text = f"Agenda for {date.strftime('%B %d, %Y')}"
    
    def add_agenda_item(self, instance):
        """Add a new agenda item with title, time, and description"""
        title = self.title_input.text.strip()
        description = self.desc_input.text.strip()
        
        # Title is required
        if not title or not self.target_date:
            return
        
        # Initialize schedule data if needed
        if self.schedule_data_ref is None:
            return
        
        # Check if target date is in the past
        today = datetime.now().date()
        if self.target_date < today:
            return
        
        # Build time string from spinners (24-hour format)
        time_str = ''
        if (self.hour_spinner.text != '--' and 
            self.minute_spinner.text != '--'):
            time_str = f"{self.hour_spinner.text}:{self.minute_spinner.text}"
            
            # Check if time has already passed for today's date
            if self.target_date == today:
                try:
                    alarm_hour = int(self.hour_spinner.text)
                    alarm_minute = int(self.minute_spinner.text)
                    alarm_time = datetime.now().replace(hour=alarm_hour, minute=alarm_minute, second=0, microsecond=0)
                    
                    if alarm_time < datetime.now():
                        return
                except (ValueError, AttributeError):
                    pass  # Invalid time format, skip validation
        
        # Create item dictionary
        item_data = {
            'title': title,
            'time': time_str,
            'description': description if description else ''
        }
        
        # Add item to schedule data
        if self.target_date not in self.schedule_data_ref:
            self.schedule_data_ref[self.target_date] = []
        
        self.schedule_data_ref[self.target_date].append(item_data)
        
        # Clear inputs
        self.title_input.text = ''
        self.hour_spinner.text = '--'
        self.minute_spinner.text = '--'
        self.desc_input.text = ''
        
        # Navigate back to schedule page and refresh it
        schedule_page = self.manager.get_screen('schedule_page')
        schedule_page.on_enter()  # Refresh the schedule page
        self.manager.current = 'schedule_page'
    
    def delete_item(self, item_data):
        """Delete an agenda item"""
        if not self.target_date or not self.schedule_data_ref:
            return
        
        if self.target_date in self.schedule_data_ref:
            items = self.schedule_data_ref[self.target_date]
            # Find and remove the matching item
            for i, item in enumerate(items):
                if isinstance(item, dict) and isinstance(item_data, dict):
                    # Match by comparing all fields
                    if (item.get('title') == item_data.get('title') and
                        item.get('time') == item_data.get('time') and
                        item.get('description') == item_data.get('description')):
                        items.pop(i)
                        break
                elif isinstance(item, str) and isinstance(item_data, str):
                    # Legacy string format
                    if item == item_data:
                        items.pop(i)
                        break
            
            # If no items left, remove the date entry
            if len(self.schedule_data_ref[self.target_date]) == 0:
                del self.schedule_data_ref[self.target_date]
            
                # Item deleted successfully
    
    def _update_rect(self, instance, value):
        """Update background rectangle size and position"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def go_back(self, instance):
        """Navigate back to schedule page and refresh it"""
        # Refresh the schedule page to show updated agenda
        schedule_page = self.manager.get_screen('schedule_page')
        schedule_page.on_enter()  # Refresh the schedule page
        self.manager.current = 'schedule_page'

