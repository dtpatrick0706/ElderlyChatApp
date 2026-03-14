from kivy.clock import Clock
from datetime import datetime


class AlarmManager:
    """Manages alarm checking and notifications for agenda items"""
    
    def __init__(self, schedule_data_ref=None, schedule_page_ref=None):
        self.schedule_data_ref = schedule_data_ref
        self.schedule_page_ref = schedule_page_ref  # Reference to schedule page for refreshing
        self.triggered_alarms = set()  # Track alarms that have already fired today
        self.current_date = datetime.now().date()
        self.alarm_event = None
        self.is_running = False
    
    def start(self):
        """Start the alarm checking service"""
        if not self.is_running:
            # Check time every 30 seconds
            self.alarm_event = Clock.schedule_interval(self.check_alarms, 30)
            self.is_running = True
    
    def stop(self):
        """Stop the alarm checking service"""
        if self.alarm_event:
            Clock.unschedule(self.alarm_event)
            self.alarm_event = None
            self.is_running = False
    
    def check_alarms(self, dt=None):
        """Check if any agenda items' times have arrived"""
        if not self.schedule_data_ref:
            return
        
        now = datetime.now()
        today = now.date()
        
        # Reset triggered alarms if it's a new day
        if today != self.current_date:
            self.triggered_alarms.clear()
            self.current_date = today
        
        # Check today's agenda items
        if today in self.schedule_data_ref:
            agenda_items = self.schedule_data_ref[today]
            
            for item in agenda_items:
                if isinstance(item, dict) and item.get('time'):
                    time_str = item.get('time', '')
                    title = item.get('title', 'Untitled')
                    
                    if not time_str:
                        continue
                    
                    # Create unique alarm ID (date + time + title)
                    alarm_id = f"{today}_{time_str}_{title}"
                    
                    # Skip if already triggered
                    if alarm_id in self.triggered_alarms:
                        continue
                    
                    # Parse time (format: "HH:MM")
                    try:
                        alarm_hour, alarm_minute = map(int, time_str.split(':'))
                        alarm_time = now.replace(hour=alarm_hour, minute=alarm_minute, second=0, microsecond=0)
                        
                        # Check if current time matches alarm time (within 30 seconds window)
                        time_diff = abs((now - alarm_time).total_seconds())
                        
                        if time_diff <= 30:  # Trigger within 30 seconds of alarm time
                            self.trigger_alarm(item)
                            self.triggered_alarms.add(alarm_id)
                    except (ValueError, AttributeError):
                        # Invalid time format, skip
                        continue
    
    def trigger_alarm(self, item):
        """Trigger an alarm notification for an agenda item"""
        # Remove the agenda item after alarm triggers
        self.remove_agenda_item(item)
    
    def remove_agenda_item(self, item):
        """Remove the agenda item from schedule data after alarm triggers"""
        if not self.schedule_data_ref:
            return
        
        today = datetime.now().date()
        if today in self.schedule_data_ref:
            items = self.schedule_data_ref[today]
            # Find and remove the matching item
            item_removed = False
            for i, agenda_item in enumerate(items):
                if isinstance(agenda_item, dict) and isinstance(item, dict):
                    # Match by comparing all fields
                    if (agenda_item.get('title') == item.get('title') and
                        agenda_item.get('time') == item.get('time') and
                        agenda_item.get('description') == item.get('description')):
                        items.pop(i)
                        item_removed = True
                        break
            
            # If no items left, remove the date entry
            if len(self.schedule_data_ref[today]) == 0:
                del self.schedule_data_ref[today]
            
            # Refresh schedule page if available
            if item_removed and self.schedule_page_ref:
                # Schedule refresh on next frame to avoid threading issues
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self._refresh_schedule_page(), 0.1)
    
    def _refresh_schedule_page(self):
        """Refresh the schedule page to reflect removed agenda item"""
        if self.schedule_page_ref:
            try:
                # Refresh the calendar and agenda display
                self.schedule_page_ref.on_enter()
            except:
                pass  # Ignore errors if page is not accessible
    
    def update_schedule_data(self, schedule_data_ref):
        """Update the reference to schedule data"""
        self.schedule_data_ref = schedule_data_ref
