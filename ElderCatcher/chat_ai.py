"""
AI Chat functionality to be integrated into chat_page.py later.

This module contains the AI chat components from the original main.py:
- ChatMessage widget
- ChatScrollView widget  
- ELDERLY_PROMPT constant
- Gemini AI setup and message handling logic
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import google.generativeai as genai
import os

# System prompt for elderly-friendly conversation
ELDERLY_PROMPT = """You are a friendly and patient AI assistant talking to an elderly person. 
Please:
- Use clear, simple language
- Be patient and understanding
- Speak in a warm, caring tone
- Avoid technical jargon
- Be helpful with everyday questions and concerns
- Show empathy and respect
- Keep responses concise but complete
- If asked about technology, explain it in simple terms

Remember that the person you're talking to may have difficulty with complex instructions or modern technology."""


class ChatMessage(BoxLayout):
    """Widget to display a single chat message bubble"""
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.is_user = is_user
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50  # Will be updated by update_bubble
        self.padding = ['10dp', '8dp']
        self.spacing = '10dp'
        
        # Spacer for alignment - user messages on right, AI on left
        if is_user:
            # User messages: add spacer on left to push right
            self.add_widget(Label(size_hint_x=1))  # Flexible spacer
        else:
            # AI messages: small spacer on left
            self.add_widget(Label(size_hint_x=None, width='20dp'))
        
        # Bubble container
        bubble_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width='270dp',  # Initial width, will adjust
            size_hint_y=None,
            padding=['12dp', '10dp']
        )
        
        # Message bubble background - rounded rectangle
        with bubble_container.canvas.before:
            # Different colors for user vs AI messages
            # AI messages: light blue on left, User messages: light gray on right
            if is_user:
                Color(0.9, 0.9, 0.9, 1.0)  # Light gray for user messages (right side)
            else:
                Color(0.7, 0.85, 1.0, 1.0)  # Light blue for AI messages (left side)
            self.bubble_rect = RoundedRectangle(
                pos=bubble_container.pos,
                size=bubble_container.size,
                radius=[(18, 18)]  # Rounded corners
            )
        
        # Message label with proper text alignment and wrapping
        message_label = Label(
            text=text,
            text_size=(None, None),  # Will be set dynamically
            halign='left',
            valign='top',
            font_size='16sp',
            color=(0, 0, 0, 1) if is_user else (1, 1, 1, 1),  # Black text for user (gray bubble), white text for AI (blue bubble)
            size_hint_y=None,
            padding_x='0dp',
            padding_y='0dp',
            markup=False
        )
        
        # Update bubble size when text changes
        def update_bubble(instance, value):
            # Set text width constraint (bubble width minus padding)
            if bubble_container.width > 0:
                available_width = bubble_container.width - 24  # Account for padding (12dp each side)
                message_label.text_size = (available_width, None)
                message_label.texture_update()
                
                # Update heights based on text
                text_height = message_label.texture_size[1] if message_label.texture_size and message_label.texture_size[1] > 0 else 20
                bubble_height = max(40, text_height + 20)  # Min height 40, add padding
                bubble_container.height = bubble_height
                message_label.height = text_height
                self.height = bubble_height + 16  # Add vertical padding between messages
                
                # Update bubble rectangle
                if hasattr(self, 'bubble_rect'):
                    self.bubble_rect.size = bubble_container.size
                    self.bubble_rect.pos = bubble_container.pos
        
        # Initial update
        def initial_update(instance, value):
            if bubble_container.width > 0:
                update_bubble(instance, value)
        
        message_label.bind(texture_size=update_bubble)
        bubble_container.bind(
            size=initial_update,
            pos=lambda inst, val: setattr(self.bubble_rect, 'pos', inst.pos) if hasattr(self, 'bubble_rect') else None
        )
        
        # Schedule initial size calculation
        Clock.schedule_once(lambda dt: initial_update(bubble_container, None), 0.1)
        
        bubble_container.add_widget(message_label)
        self.add_widget(bubble_container)
        
        # Right spacer
        if is_user:
            self.add_widget(Label(size_hint_x=None, width='20dp'))  # Small right spacer
        else:
            self.add_widget(Label(size_hint_x=1))  # Flexible spacer for AI messages


class ChatScrollView(ScrollView):
    """Scrollable container for chat messages"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_layout = BoxLayout(orientation='vertical', spacing='8dp', padding=['10dp', '15dp'], size_hint_y=None)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.add_widget(self.chat_layout)
    
    def add_message(self, text, is_user=True, speak=True):
        """Add a message to the chat. speak=False skips TTS (e.g. for 'Thinking...')."""
        text = text if text is not None else ""
        message = ChatMessage(text, is_user)
        self.chat_layout.add_widget(message)
        Clock.schedule_once(self._update_chat_height, 0.05)
        Clock.schedule_once(self.scroll_to_bottom, 0.15)
        return message

    def _update_chat_height(self, dt):
        """Update chat layout height after children are laid out."""
        try:
            total = 20
            # Use list() so we don't iterate over changing list
            for c in list(self.chat_layout.children):
                try:
                    h = getattr(c, 'height', 50)
                    total += (h if isinstance(h, (int, float)) else 50)
                except Exception:
                    total += 50
            self.chat_layout.height = total
        except Exception:
            pass

    def scroll_to_bottom(self, dt):
        """Scroll to the bottom of the chat"""
        try:
            if self.chat_layout.height > self.height:
                self.scroll_y = 0
        except Exception:
            pass


def setup_gemini_model():
    """
    Initialize Gemini AI model with API key.
    Returns the model instance or None if setup fails.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Try to import from config.py
    if not api_key:
        try:
            from config import GEMINI_API_KEY
            api_key = GEMINI_API_KEY
        except ImportError:
            pass
    
    # Try to read from config.txt file
    if not api_key:
        try:
            with open('config.txt', 'r') as f:
                api_key = f.read().strip()
                # Remove quotes if present
                api_key = api_key.strip('"').strip("'")
        except FileNotFoundError:
            pass
    
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Try different model names for better compatibility
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                try:
                    model = genai.GenerativeModel('gemini-pro')
                except:
                    model = genai.GenerativeModel('gemini-1.0-pro')
        return model
    except Exception as e:
        print(f"Error initializing AI: {e}")
        return None


def generate_ai_response(model, conversation_history, user_text):
    """
    Generate AI response based on user text and conversation history.
    
    Args:
        model: Gemini model instance
        conversation_history: List of conversation history
        user_text: User's message text
    
    Returns:
        AI response text or error message
    """
    try:
        # Build conversation context
        if len(conversation_history) == 0:
            # First message - include system prompt
            prompt = f"{ELDERLY_PROMPT}\n\nUser: {user_text}"
        else:
            # Build conversation history (last 10 messages for context)
            history_text = "\n".join([f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['content']}" for h in conversation_history[-10:]])
            prompt = f"{ELDERLY_PROMPT}\n\nPrevious conversation:\n{history_text}\n\nUser: {user_text}"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error messages
        if "API_KEY" in error_msg or "api key" in error_msg.lower():
            return "API key error. Please check your GEMINI_API_KEY configuration."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "API quota exceeded. Please try again later."
        return f"Sorry, I encountered an error: {error_msg}"

