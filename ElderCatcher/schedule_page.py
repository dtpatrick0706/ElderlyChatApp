from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, Line, Ellipse
from datetime import datetime, timedelta
from rounded_button import RoundedButton


class CircularButton(ButtonBehavior, Label):
    """Circular button widget"""
    def __init__(self, **kwargs):
        # Extract bg_color if provided
        bg_color = kwargs.pop('bg_color', (0.2, 0.6, 0.8, 1))
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 60)  # Circular button size
        self.bg_color = bg_color
        self.color = (1, 1, 1, 1)  # White text by default
        self.halign = 'center'
        self.valign = 'middle'
        self._ellipse = None
        self.bind(pos=self._update_circle, size=self._update_circle)
        self._update_circle()
    
    def _update_circle(self, *args):
        """Update circular background"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            # Draw circular background - Ellipse positioned at widget's pos
            # Use minimum of width/height to ensure perfect circle
            size = min(self.width, self.height) if self.width > 0 and self.height > 0 else 60
            x_offset = (self.width - size) / 2 if self.width > 0 else 0
            y_offset = (self.height - size) / 2 if self.height > 0 else 0
            self._ellipse = Ellipse(
                pos=(self.x + x_offset, self.y + y_offset),
                size=(size, size)
            )


class ClickableDateCell(BoxLayout):
    """Clickable date cell for calendar"""
    def __init__(self, date_value, on_date_clicked, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.date_value = date_value
        self.on_date_clicked = on_date_clicked
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_date_clicked(self.date_value)
            return True
        return super().on_touch_down(touch)


class SchedulePage(Screen):
    """Schedule page with calendar and day's agenda"""
    
    # Light yellow background color (very light yellow)
    BACKGROUND_COLOR = (1.0, 0.98, 0.85, 1.0)  # Very light yellow
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'schedule_page'
        
        # Schedule data (empty for now)
        self.schedule_data = {}
        
        # Selected date (None means today is selected)
        self.selected_date = None
        
        # Store date cells for highlighting
        self.date_cells = {}
        
        # Create main layout with FloatLayout overlay for circular button
        main_layout = FloatLayout()
        
        # Content layout (vertical box layout) - fills entire FloatLayout
        content_layout = BoxLayout(
            orientation='vertical',
            padding='8dp',
            spacing='8dp',
            size_hint=(1, 1)  # Fill entire parent FloatLayout
        )
        
        # Set background color
        with content_layout.canvas.before:
            Color(*self.BACKGROUND_COLOR)
            self.rect = Rectangle(size=content_layout.size, pos=content_layout.pos)
        
        # Bind to update background when size changes
        content_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Back button with rounded corners - optimized for phone
        back_button = RoundedButton(
            text='← Back',
            font_size='20sp',
            size_hint_y=0.08,
            bg_color=(0.7, 0.7, 0.7, 1)
        )
        back_button.bind(on_press=self.go_back)
        content_layout.add_widget(back_button)
        
        # Calendar section (top part) - adjusted for phone
        calendar_section = BoxLayout(
            orientation='vertical',
            size_hint_y=0.60,
            padding='8dp',
            spacing='8dp'
        )
        
        # Calendar header (month, date, day) - shows current date with background
        today = datetime.now()
        calendar_header_wrapper = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='60dp',
            padding='5dp'
        )
        
        # Add background to header
        with calendar_header_wrapper.canvas.before:
            Color(1, 1, 1, 1)  # White background
            calendar_header_wrapper.bg_rect = Rectangle(
                pos=calendar_header_wrapper.pos,
                size=calendar_header_wrapper.size
            )
            # Border
            Color(0.4, 0.4, 0.4, 1)
            calendar_header_wrapper.border_line = Line(
                width=1,
                rectangle=(calendar_header_wrapper.x, calendar_header_wrapper.y,
                          calendar_header_wrapper.width, calendar_header_wrapper.height)
            )
        
        calendar_header_wrapper.bind(size=self._update_header_bg, pos=self._update_header_bg)
        
        calendar_header = Label(
            text=f'{today.strftime("%B")} {today.day}, {today.year}\n{today.strftime("%A")}',
            font_size='20sp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            bold=True,
            color=(0, 0, 0, 1)  # Black text for contrast
        )
        self.calendar_header = calendar_header  # Store reference for updates
        calendar_header_wrapper.add_widget(calendar_header)
        calendar_section.add_widget(calendar_header_wrapper)
        
        # Calendar grid - days of week headers
        weekdays_layout = GridLayout(cols=7, size_hint_y=None, height='30dp', spacing='2dp')
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for day in weekdays:
            day_wrapper = BoxLayout()
            # Add background to weekday header
            with day_wrapper.canvas.before:
                Color(0.95, 0.95, 0.95, 1)  # Light gray background
                day_wrapper.bg_rect = Rectangle(
                    pos=day_wrapper.pos,
                    size=day_wrapper.size
                )
            day_wrapper.bind(size=self._update_day_header_bg, pos=self._update_day_header_bg)
            
            day_label = Label(
                text=day,
                font_size='14sp',
                halign='center',
                valign='middle',
                text_size=(None, None),
                color=(0, 0, 0, 1),  # Black text
                bold=True
            )
            day_wrapper.add_widget(day_label)
            weekdays_layout.add_widget(day_wrapper)
        calendar_section.add_widget(weekdays_layout)
        
        # Calendar grid - dates
        calendar_grid = GridLayout(cols=7, spacing='2dp', size_hint_y=1, padding='2dp')
        self.calendar_grid = calendar_grid
        
        # Populate calendar with dates
        self._populate_calendar()
        calendar_section.add_widget(calendar_grid)
        
        content_layout.add_widget(calendar_section)
        
        # Day's agenda section (bottom part - small box) - adjusted for phone
        agenda_wrapper = BoxLayout(
            orientation='vertical',
            size_hint_y=0.32,
            padding='6dp'
        )
        
        # Add border to agenda section
        with agenda_wrapper.canvas.after:
            Color(0.4, 0.4, 0.4, 1)  # Dark gray border color
            agenda_wrapper.border_line = Line(
                width=2,
                rectangle=(agenda_wrapper.x, agenda_wrapper.y, 
                          agenda_wrapper.width, agenda_wrapper.height)
            )
        
        # Bind to update border when size/position changes
        agenda_wrapper.bind(size=self._update_agenda_border, pos=self._update_agenda_border)
        self.agenda_wrapper = agenda_wrapper
        
        # Agenda title with background
        agenda_title_wrapper = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='35dp',
            padding='5dp'
        )
        
        # Add background to agenda title
        with agenda_title_wrapper.canvas.before:
            Color(1, 1, 1, 1)  # White background
            agenda_title_wrapper.bg_rect = Rectangle(
                pos=agenda_title_wrapper.pos,
                size=agenda_title_wrapper.size
            )
            # Border
            Color(0.4, 0.4, 0.4, 1)
            agenda_title_wrapper.border_line = Line(
                width=1,
                rectangle=(agenda_title_wrapper.x, agenda_title_wrapper.y,
                          agenda_title_wrapper.width, agenda_title_wrapper.height)
            )
        
        agenda_title_wrapper.bind(size=self._update_agenda_title_bg, pos=self._update_agenda_title_bg)
        
        agenda_title = Label(
            text="Today's Agenda",
            font_size='18sp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            bold=True,
            color=(0, 0, 0, 1)  # Black text for contrast
        )
        self.agenda_title = agenda_title  # Store reference for updates
        agenda_title_wrapper.add_widget(agenda_title)
        agenda_wrapper.add_widget(agenda_title_wrapper)
        
        # Scrollable agenda list
        agenda_scroll = ScrollView()
        agenda_layout = BoxLayout(
            orientation='vertical',
            spacing='5dp',
            padding='5dp',
            size_hint_y=None
        )
        agenda_layout.bind(minimum_height=agenda_layout.setter('height'))
        self.agenda_layout = agenda_layout
        
        # Populate today's agenda
        self._populate_agenda_for_date(datetime.now().date())
        
        agenda_scroll.add_widget(agenda_layout)
        agenda_wrapper.add_widget(agenda_scroll)
        
        content_layout.add_widget(agenda_wrapper)
        
        # Add content layout to main FloatLayout
        main_layout.add_widget(content_layout)
        
        # Create circular button in bottom right corner - floating style
        self.circular_button = CircularButton(
            text='+',
            font_size='32sp',
            bg_color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        # Position in bottom right with more padding to create floating effect
        # Using 'bottom' with higher value (0.20 = 20% from bottom) for floating look
        self.circular_button.pos_hint = {'right': 0.93, 'bottom': 0.20}
        # Bind button press to function
        self.circular_button.bind(on_press=self.on_circular_button_pressed)
        
        # Add circular button to main layout (FloatLayout) - floats on top
        main_layout.add_widget(self.circular_button)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Called when the screen is displayed - update date to current"""
        self._update_date_display()
        # Refresh calendar to update today's highlighting (keep current selection)
        self.calendar_grid.clear_widgets()
        self.date_cells = {}  # Clear stored cells
        self._populate_calendar()
        # Update highlighting for selected date
        if self.selected_date:
            self._update_date_highlighting()
        # Update agenda for currently selected date (or today if none selected)
        self._update_agenda()
    
    def _update_date_display(self):
        """Update the calendar header with current date"""
        today = datetime.now()
        self.calendar_header.text = f'{today.strftime("%B")} {today.day}, {today.year}\n{today.strftime("%A")}'
    
    def _update_agenda(self):
        """Update agenda display for selected date (or today if none selected)"""
        # Clear existing agenda items
        self.agenda_layout.clear_widgets()
        # Use selected date or today
        display_date = self.selected_date if self.selected_date else datetime.now().date()
        self._populate_agenda_for_date(display_date)
    
    def _populate_calendar(self):
        """Populate calendar grid with dates - only current month"""
        today = datetime.now()
        first_day = today.replace(day=1)
        # Get the last day of the current month
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Find the first Monday of the month (or before if month doesn't start on Monday)
        days_before = first_day.weekday()  # 0=Monday, 6=Sunday
        start_date = first_day - timedelta(days=days_before)
        
        # Calculate total days in month
        days_in_month = last_day.day
        
        # Find the starting position (first day of month in the week)
        start_pos = first_day.weekday()
        
        # Add empty cells for days before the first day of the month
        for i in range(start_pos):
            empty_cell = BoxLayout(orientation='vertical')
            with empty_cell.canvas.before:
                Color(0.95, 0.95, 0.95, 1)  # Very light gray for empty cells
                empty_cell.bg_rect = Rectangle(
                    pos=empty_cell.pos,
                    size=empty_cell.size
                )
            with empty_cell.canvas.after:
                Color(0.6, 0.6, 0.6, 1)  # Gray border
                empty_cell.border_line = Line(
                    width=1,
                    rectangle=(empty_cell.x, empty_cell.y,
                              empty_cell.width, empty_cell.height)
                )
            empty_cell.bind(size=self._update_date_cell, pos=self._update_date_cell)
            self.calendar_grid.add_widget(empty_cell)
        
        # Generate dates for the current month only
        for day in range(1, days_in_month + 1):
            current_date_obj = today.replace(day=day)
            current_date = current_date_obj.date()
            is_today = (current_date == today.date())
            is_selected = (self.selected_date == current_date) if self.selected_date else False
            
            # Create clickable date cell
            date_cell = ClickableDateCell(
                date_value=current_date,
                on_date_clicked=self._select_date
            )
            
            # Add background and border using Rectangle and Line
            with date_cell.canvas.before:
                # Background color - different for selected, today, or normal
                if is_selected:
                    Color(0.5, 0.8, 0.5, 1)  # Light green background for selected
                elif is_today:
                    Color(0.7, 0.85, 1.0, 1)  # Light blue background for today
                else:
                    Color(1, 1, 1, 1)  # White background for other dates
                date_cell.bg_rect = Rectangle(
                    pos=date_cell.pos,
                    size=date_cell.size
                )
            
            with date_cell.canvas.after:
                # Border - thicker for selected date
                if is_selected:
                    Color(0.2, 0.6, 0.2, 1)  # Darker green border for selected
                    border_width = 2
                else:
                    Color(0.6, 0.6, 0.6, 1)  # Gray border
                    border_width = 1
                date_cell.border_line = Line(
                    width=border_width,
                    rectangle=(date_cell.x, date_cell.y, 
                              date_cell.width, date_cell.height)
                )
            
            # Store cell reference for later highlighting updates
            date_cell.is_today = is_today
            
            # Bind to update background and border when positioned
            date_cell.bind(size=self._update_date_cell, pos=self._update_date_cell)
            
            # Date number label - always black, centered
            date_label = Label(
                text=str(day),
                font_size='16sp',
                size_hint_y=None,
                height='30dp',
                halign='center',
                valign='middle',
                text_size=(None, None),
                color=(0, 0, 0, 1),  # Always black for better visibility
                bold=(is_today or is_selected)
            )
            date_cell.add_widget(date_label)
            
            # Show agenda title(s) on calendar if date has agenda items
            if current_date in self.schedule_data and len(self.schedule_data[current_date]) > 0:
                agenda_items = self.schedule_data[current_date]
                # Extract titles from items (handle both dict and string formats for backwards compatibility)
                titles_to_show = []
                for item in agenda_items[:1]:  # Show only first title due to space
                    if isinstance(item, dict):
                        title = item.get('title', '')
                    else:
                        title = str(item)
                    if title:
                        titles_to_show.append(title)
                
                if titles_to_show:
                    indicator_text = titles_to_show[0]
                    
                    # Truncate if too long to fit in calendar cell
                    if len(indicator_text) > 10:
                        indicator_text = indicator_text[:8] + '...'
                    
                    indicator_label = Label(
                        text=indicator_text,
                        font_size='9sp',
                        size_hint_y=None,
                        height='16dp',
                        halign='center',
                        valign='middle',
                        text_size=(None, None),
                        color=(0.6, 0.3, 0.1, 1)  # Brownish color for indicators
                    )
                    date_cell.add_widget(indicator_label)
            
            # Store cell for highlighting updates
            self.date_cells[current_date] = date_cell
            
            self.calendar_grid.add_widget(date_cell)
        
        # Fill remaining cells to complete the grid (if month doesn't end on Sunday)
        # Calculate remaining cells needed to complete the last week
        total_cells_so_far = start_pos + days_in_month
        remaining_cells = (7 - (total_cells_so_far % 7)) % 7
        
        # Add empty cells for remaining days in the week
        for i in range(remaining_cells):
            empty_cell = BoxLayout(orientation='vertical')
            with empty_cell.canvas.before:
                Color(0.95, 0.95, 0.95, 1)  # Very light gray for empty cells
                empty_cell.bg_rect = Rectangle(
                    pos=empty_cell.pos,
                    size=empty_cell.size
                )
            with empty_cell.canvas.after:
                Color(0.6, 0.6, 0.6, 1)  # Gray border
                empty_cell.border_line = Line(
                    width=1,
                    rectangle=(empty_cell.x, empty_cell.y,
                              empty_cell.width, empty_cell.height)
                )
            empty_cell.bind(size=self._update_date_cell, pos=self._update_date_cell)
            self.calendar_grid.add_widget(empty_cell)
    
    def _select_date(self, date):
        """Select a date and update highlighting and agenda"""
        self.selected_date = date
        self._update_date_highlighting()
        self._update_agenda_title()
        self._update_agenda()
    
    def _update_agenda_title(self):
        """Update agenda title to show selected date"""
        today = datetime.now().date()
        if self.selected_date:
            if self.selected_date == today:
                self.agenda_title.text = "Today's Agenda"
            else:
                date_str = self.selected_date.strftime("%B %d, %Y")
                self.agenda_title.text = f"Agenda for {date_str}"
        else:
            self.agenda_title.text = "Today's Agenda"
    
    def _update_date_highlighting(self):
        """Update highlighting for all date cells based on selection"""
        today = datetime.now().date()
        
        for date_value, cell in self.date_cells.items():
            is_today = (date_value == today)
            is_selected = (self.selected_date == date_value) if self.selected_date else False
            
            # Clear old canvas
            cell.canvas.before.clear()
            cell.canvas.after.clear()
            
            # Redraw background
            with cell.canvas.before:
                if is_selected:
                    Color(0.5, 0.8, 0.5, 1)  # Light green for selected
                elif is_today:
                    Color(0.7, 0.85, 1.0, 1)  # Light blue for today
                else:
                    Color(1, 1, 1, 1)  # White for others
                cell.bg_rect = Rectangle(
                    pos=cell.pos,
                    size=cell.size
                )
            
            # Redraw border
            with cell.canvas.after:
                if is_selected:
                    Color(0.2, 0.6, 0.2, 1)  # Darker green border for selected
                    border_width = 2
                else:
                    Color(0.6, 0.6, 0.6, 1)  # Gray border
                    border_width = 1
                cell.border_line = Line(
                    width=border_width,
                    rectangle=(cell.x, cell.y, cell.width, cell.height)
                )
            
            # Rebind size/pos updates after clearing canvas
            cell.bind(size=self._update_date_cell, pos=self._update_date_cell)
            
            # Update label boldness
            if len(cell.children) > 0:
                label = cell.children[0]
                if isinstance(label, Label):
                    label.bold = (is_today or is_selected)
    
    def _populate_agenda_for_date(self, date):
        """Populate agenda for a specific date - displays title, time, and description"""
        # Update agenda title to show selected date
        if date in self.schedule_data:
            agenda_items = self.schedule_data[date]
            # Sort items by time if available (for dict format)
            sorted_items = sorted(agenda_items, key=lambda x: x.get('time', '') if isinstance(x, dict) else '')
            
            for item in sorted_items:
                # Handle both dict format and string format (for backwards compatibility)
                if isinstance(item, dict):
                    # Outer container with delete button
                    item_container = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height='80dp',
                        spacing='5dp',
                        padding='5dp'
                    )
                    
                    # Create a vertical layout for each agenda item
                    item_wrapper = BoxLayout(
                        orientation='vertical',
                        size_hint_x=0.9,
                        spacing='3dp',
                        padding='8dp'
                    )
                    
                    # Title (bold)
                    title_label = Label(
                        text=f'• {item.get("title", "Untitled")}',
                        font_size='16sp',
                        size_hint_y=None,
                        height='25dp',
                        halign='left',
                        valign='middle',
                        text_size=(None, None),
                        bold=True,
                        color=(0, 0, 0, 1)
                    )
                    item_wrapper.add_widget(title_label)
                    
                    # Time (if available)
                    if item.get('time'):
                        time_label = Label(
                            text=f'Time: {item["time"]}',
                            font_size='14sp',
                            size_hint_y=None,
                            height='20dp',
                            halign='left',
                            valign='middle',
                            text_size=(None, None),
                            color=(0.4, 0.4, 0.4, 1)
                        )
                        item_wrapper.add_widget(time_label)
                    
                    # Description (if available)
                    if item.get('description'):
                        desc_label = Label(
                            text=item['description'],
                            font_size='14sp',
                            size_hint_y=1,
                            halign='left',
                            valign='top',
                            text_size=(None, None),
                            color=(0.2, 0.2, 0.2, 1)
                        )
                        item_wrapper.add_widget(desc_label)
                    
                    item_container.add_widget(item_wrapper)
                    
                    # Delete button
                    delete_button = RoundedButton(
                        text='✕',
                        font_size='16sp',
                        size_hint_x=0.1,
                        size_hint_y=1,
                        bg_color=(1, 0.3, 0.3, 1)  # Red
                    )
                    delete_button.bind(on_press=lambda instance, item_data=item: self.delete_agenda_item(date, item_data))
                    item_container.add_widget(delete_button)
                    
                    self.agenda_layout.add_widget(item_container)
                else:
                    # Legacy format - just a string
                    # Create container with delete button
                    item_container = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height='40dp',
                        spacing='5dp',
                        padding='5dp'
                    )
                    
                    agenda_item = Label(
                        text=f'• {item}',
                        font_size='16sp',
                        size_hint_x=0.9,
                        halign='left',
                        valign='middle',
                        text_size=(None, None),
                        padding_x='10dp'
                    )
                    item_container.add_widget(agenda_item)
                    
                    # Delete button for legacy format
                    delete_button = RoundedButton(
                        text='✕',
                        font_size='16sp',
                        size_hint_x=0.1,
                        size_hint_y=1,
                        bg_color=(1, 0.3, 0.3, 1)  # Red
                    )
                    delete_button.bind(on_press=lambda instance, item_data=item: self.delete_agenda_item(date, item_data))
                    item_container.add_widget(delete_button)
                    
                    self.agenda_layout.add_widget(item_container)
        else:
            date_str = date.strftime("%B %d, %Y")
            if date == datetime.now().date():
                no_agenda_text = 'No agenda items for today'
            else:
                no_agenda_text = f'No agenda items for {date_str}'
            
            no_agenda = Label(
                text=no_agenda_text,
                font_size='16sp',
                size_hint_y=None,
                height='40dp',
                halign='center',
                valign='middle',
                text_size=(None, None),
                color=(0.6, 0.6, 0.6, 1)
            )
            self.agenda_layout.add_widget(no_agenda)
    
    def _update_date_cell(self, instance, value):
        """Update date cell background and border when size/position changes"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        if hasattr(instance, 'border_line'):
            instance.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def _update_header_bg(self, instance, value):
        """Update calendar header background and border"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        if hasattr(instance, 'border_line'):
            instance.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def _update_day_header_bg(self, instance, value):
        """Update weekday header background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_agenda_title_bg(self, instance, value):
        """Update agenda title background and border"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        if hasattr(instance, 'border_line'):
            instance.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def _update_agenda_border(self, instance, value):
        """Update agenda border when size/position changes"""
        if hasattr(instance, 'border_line'):
            instance.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def _update_rect(self, instance, value):
        """Update background rectangle size and position"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def delete_agenda_item(self, date, item_data):
        """Delete an agenda item from a specific date"""
        if date in self.schedule_data:
            items = self.schedule_data[date]
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
            if len(self.schedule_data[date]) == 0:
                del self.schedule_data[date]
            
            # Refresh the agenda display
            self.agenda_layout.clear_widgets()
            self._populate_agenda_for_date(date)
            
            # Refresh calendar to update indicators
            self.calendar_grid.clear_widgets()
            self.date_cells = {}
            self._populate_calendar()
            if self.selected_date:
                self._update_date_highlighting()
    
    def on_circular_button_pressed(self, instance):
        """Handle circular button press - navigate to add agenda page"""
        # Determine target date: use selected date or today if none selected
        target_date = self.selected_date if self.selected_date else datetime.now().date()
        
        # Navigate to add agenda page
        add_agenda_page = self.manager.get_screen('add_agenda_page')
        add_agenda_page.set_date(target_date, self.schedule_data)
        self.manager.current = 'add_agenda_page'
    
    def go_back(self, instance):
        """Navigate back to front page"""
        self.manager.current = 'front_page'
