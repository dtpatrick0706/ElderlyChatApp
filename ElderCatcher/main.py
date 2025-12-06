import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import google.generativeai as genai
import os
from kivy.config import Config

# Set window size for better visibility
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

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
    """Widget to display a single chat message"""
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.is_user = is_user
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = ['10dp', '5dp']
        self.spacing = '10dp'
        
        # Create label for message
        message_label = Label(
            text=text,
            text_size=(None, None),
            halign='left' if is_user else 'right',
            valign='middle',
            size_hint_x=0.8 if is_user else 1.0,
            font_size='18sp',
            color=(0, 0, 0, 1) if is_user else (0, 0.3, 0.6, 1)
        )
        message_label.bind(texture_size=lambda instance, value: setattr(instance.parent, 'height', max(48, value[1] + 10)))
        
        # Add label to layout
        if is_user:
            self.add_widget(message_label)
            self.add_widget(Label(size_hint_x=0.2))  # Spacer
        else:
            self.add_widget(Label(size_hint_x=0.2))  # Spacer
            self.add_widget(message_label)

class ChatScrollView(ScrollView):
    """Scrollable container for chat messages"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_layout = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp', size_hint_y=None)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.add_widget(self.chat_layout)
    
    def add_message(self, text, is_user=True):
        """Add a message to the chat"""
        message = ChatMessage(text, is_user)
        self.chat_layout.add_widget(message)
        # Update layout height
        total_height = sum(child.height for child in self.chat_layout.children) + 20
        self.chat_layout.height = max(self.height, total_height)
        # Scroll to bottom
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
        return message
    
    def scroll_to_bottom(self, dt):
        """Scroll to the bottom of the chat"""
        if self.chat_layout.height > self.height:
            self.scroll_y = 0

class ElderlyChatApp(BoxLayout):
    """Main application layout"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '10dp'
        self.spacing = '10dp'
        
        # Title
        title = Label(
            text='Elderly Chat Assistant',
            size_hint_y=0.1,
            font_size='28sp',
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        self.add_widget(title)
        
        # Chat area
        self.chat_view = ChatScrollView()
        self.add_widget(self.chat_view)
        
        # Input area
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing='10dp')
        
        self.text_input = TextInput(
            multiline=False,
            font_size='20sp',
            hint_text='Type your message here...',
            size_hint_x=0.75
        )
        self.text_input.bind(on_text_validate=self.send_message)
        
        self.send_button = Button(
            text='Send',
            font_size='20sp',
            size_hint_x=0.25,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.send_button.bind(on_press=self.send_message)
        
        input_layout.add_widget(self.text_input)
        input_layout.add_widget(self.send_button)
        self.add_widget(input_layout)
        
        # Initialize Gemini AI
        self.model = None
        self.conversation_history = []  # Conversation history for context
        self.setup_gemini()
        
        # Add welcome message
        self.chat_view.add_message("Hello! I'm your friendly AI assistant. How can I help you today?", is_user=False)
    
    def setup_gemini(self):
        """Initialize Gemini AI with API key"""
        api_key = os.getenv('GEMINI_API_KEY')
        
        # Try to import from config.py (like entertainment_companion)
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
            self.chat_view.add_message(
                "Error: Please set your GEMINI_API_KEY environment variable, create a config.py file with GEMINI_API_KEY, or create a config.txt file with your API key.",
                is_user=False
            )
            return
        
        try:
            genai.configure(api_key=api_key)
            # Try different model names for better compatibility
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except:
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                except:
                    try:
                        self.model = genai.GenerativeModel('gemini-pro')
                    except:
                        self.model = genai.GenerativeModel('gemini-1.0-pro')
        except Exception as e:
            error_msg = str(e)
            # Provide more specific error information
            if "API_KEY" in error_msg or "api key" in error_msg.lower() or "invalid" in error_msg.lower():
                self.chat_view.add_message(
                    f"Error: Invalid API key. Please check your GEMINI_API_KEY. Error details: {error_msg}",
                    is_user=False
                )
            else:
                self.chat_view.add_message(
                    f"Error initializing AI: {error_msg}",
                    is_user=False
                )
    
    def send_message(self, instance):
        """Send user message and get AI response"""
        user_text = self.text_input.text.strip()
        if not user_text or not self.model:
            return
        
        # Add user message to chat
        self.chat_view.add_message(user_text, is_user=True)
        self.text_input.text = ''
        
        # Show thinking indicator
        thinking_msg = self.chat_view.add_message("Thinking...", is_user=False)
        
        # Get AI response
        try:
            # Use generate_content with conversation history (like entertainment_companion)
            # Build conversation context
            if len(self.conversation_history) == 0:
                # First message - include system prompt
                prompt = f"{ELDERLY_PROMPT}\n\nUser: {user_text}"
            else:
                # Build conversation history (last 10 messages for context)
                history_text = "\n".join([f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['content']}" for h in self.conversation_history[-10:]])
                prompt = f"{ELDERLY_PROMPT}\n\nPrevious conversation:\n{history_text}\n\nUser: {user_text}"
            
            response = self.model.generate_content(prompt)
            ai_response = response.text
            
            # Update conversation history
            self.conversation_history.append({'role': 'user', 'content': user_text})
            self.conversation_history.append({'role': 'assistant', 'content': ai_response})
            
            # Remove thinking message and add actual response
            self.chat_view.chat_layout.remove_widget(thinking_msg)
            self.chat_view.add_message(ai_response, is_user=False)
            
        except Exception as e:
            # Remove thinking message and show error
            self.chat_view.chat_layout.remove_widget(thinking_msg)
            error_msg = str(e)
            # Provide more helpful error messages
            if "API_KEY" in error_msg or "api key" in error_msg.lower():
                error_msg = "API key error. Please check your GEMINI_API_KEY configuration."
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_msg = "API quota exceeded. Please try again later."
            self.chat_view.add_message(
                f"Sorry, I encountered an error: {error_msg}",
                is_user=False
            )

class ElderlyChatApplication(App):
    """Main Kivy Application"""
    def build(self):
        return ElderlyChatApp()

if __name__ == '__main__':
    ElderlyChatApplication().run()
