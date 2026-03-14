import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from rounded_button import RoundedButton
from chat_ai import ChatScrollView, setup_gemini_model, generate_ai_response, ELDERLY_PROMPT
from tts_manager import TTSManager
from voice_input import VoiceInputManager


class ChatPage(Screen):
    """Chat page with virtual face area and chatting box"""

    # Light yellow background color (very light yellow)
    BACKGROUND_COLOR = (1.0, 0.98, 0.85, 1.0)  # Very light yellow

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'chat_page'

        # Initialize AI model and conversation history
        self.model = None
        self.conversation_history = []
        self.tts = TTSManager()
        self.voice_input = VoiceInputManager()

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
            size_hint_y=0.08,  # Relative sizing
            bg_color=(0.7, 0.7, 0.7, 1)
        )
        back_button.bind(on_press=self.go_back)
        main_layout.add_widget(back_button)

        # Virtual Face area (empty for now, but space reserved)
        # Covers a bit more than half of the screen - adjusted for phone
        self.virtual_face_area = BoxLayout(
            orientation='vertical',
            size_hint_y=0.52  # Adjusted for phone screen
        )

        # Empty space for virtual face (will be implemented later)
        virtual_face_label = Label(
            text='Virtual Face Area\n(Reserved for future implementation)',
            font_size='18sp',  # Smaller for phone
            color=(0.5, 0.5, 0.5, 1),
            halign='center',
            valign='middle',
            text_size=(None, None)
        )
        self.virtual_face_area.add_widget(virtual_face_label)

        main_layout.add_widget(self.virtual_face_area)

        # Chatting Box area (remaining space) - bottom section with border
        # Adjusted for phone screen
        chatting_box_wrapper = BoxLayout(
            orientation='vertical',
            size_hint_y=0.40,  # Adjusted to fit with back button
            padding='5dp'  # Padding inside the border
        )

        # Add border to the wrapper using Line
        with chatting_box_wrapper.canvas.after:
            Color(0.4, 0.4, 0.4, 1)  # Dark gray border color
            chatting_box_wrapper.border_line = Line(
                width=2,
                rectangle=(chatting_box_wrapper.x, chatting_box_wrapper.y,
                          chatting_box_wrapper.width, chatting_box_wrapper.height)
            )

        # Bind to update border when size/position changes
        chatting_box_wrapper.bind(size=self._update_chat_border, pos=self._update_chat_border)
        self.chat_box_wrapper = chatting_box_wrapper

        chatting_box_container = BoxLayout(
            orientation='vertical',
            spacing='5dp'
        )

        # Chat scroll view for messages
        self.chat_view = ChatScrollView()
        chatting_box_container.add_widget(self.chat_view)

        # Input area at bottom - optimized for phone
        input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',  # Smaller height for phone
            spacing='8dp'
        )

        self.text_input = TextInput(
            multiline=False,
            font_size='16sp',  # Smaller font for phone
            hint_text='Type your message here...',
            size_hint_x=0.55
        )
        self.text_input.bind(on_text_validate=self.send_message)

        self.mic_button = RoundedButton(
            text='🎤',
            font_size='20sp',
            size_hint_x=0.15,
            bg_color=(0.5, 0.5, 0.6, 1)
        )
        self.mic_button.bind(on_press=self._voice_input_tap)

        self.send_button = RoundedButton(
            text='Send',
            font_size='16sp',  # Smaller font for phone
            size_hint_x=0.30,
            bg_color=(0.2, 0.6, 0.8, 1)
        )
        self.send_button.bind(on_press=self.send_message)

        input_layout.add_widget(self.text_input)
        input_layout.add_widget(self.mic_button)
        input_layout.add_widget(self.send_button)
        chatting_box_container.add_widget(input_layout)

        chatting_box_wrapper.add_widget(chatting_box_container)
        main_layout.add_widget(chatting_box_wrapper)

        self.add_widget(main_layout)

        # Setup Gemini AI
        self.setup_gemini()

        # Track if welcome message has been shown
        self.welcome_shown = False

    def _update_rect(self, instance, value):
        """Update background rectangle size and position"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_chat_border(self, instance, value):
        """Update chat box border when size/position changes"""
        if hasattr(instance, 'border_line'):
            instance.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def setup_gemini(self):
        """Initialize Gemini AI with API key"""
        try:
            self.model = setup_gemini_model()
            if not self.model:
                error_msg = "Error: Please set your GEMINI_API_KEY in config.py or config.txt"
                self.chat_view.add_message(error_msg, is_user=False)
                if self.tts:
                    self.tts.speak(error_msg)
        except Exception:
            pass

    def _voice_input_tap(self, instance):
        """Tap mic: listen until you stop speaking, then send."""
        try:
            if self.voice_input.is_recording:
                return
            # Allow voice even without model (text will go to input; user can send after setting API key)
            listening_msg = self.chat_view.add_message("Listening... (speak now)", is_user=False, speak=False)

            def on_voice_result(text, error):
                try:
                    if self.chat_view.chat_layout and listening_msg.parent == self.chat_view.chat_layout:
                        self.chat_view.chat_layout.remove_widget(listening_msg)
                    if error:
                        self.chat_view.add_message(error, is_user=False)
                    elif text:
                        self.text_input.text = text
                        if self.model:
                            self.send_message(self.send_button)
                        # else text is in the box for user to send after setting API key
                except Exception as e:
                    self.chat_view.add_message("Voice result error: " + str(e), is_user=False)

            self.voice_input.listen_async_fallback(on_voice_result)
        except Exception as e:
            self.chat_view.add_message("Voice not available: " + str(e), is_user=False)

    def send_message(self, instance):
        """Send user message and get AI response"""
        user_text = self.text_input.text.strip()
        if not user_text or not self.model:
            return

        # Add user message to chat and clear the input
        self.chat_view.add_message(user_text, is_user=True)
        self.text_input.text = ''

        # Show thinking indicator
        thinking_msg = self.chat_view.add_message("Thinking...", is_user=False, speak=False)

        # Run AI call in a background thread so main thread never blocks (avoids crash while answering)
        def get_response_thread():
            try:
                ai_response = generate_ai_response(self.model, self.conversation_history, user_text)
                Clock.schedule_once(
                    lambda dt: self._apply_ai_response(thinking_msg, user_text, ai_response, None),
                    0
                )
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self._apply_ai_response(thinking_msg, user_text, None, str(e)),
                    0
                )

        threading.Thread(target=get_response_thread, daemon=True).start()

    def _apply_ai_response(self, thinking_msg, user_text, ai_response, error_msg):
        """Update UI with AI response (must run on main thread)."""
        try:
            # Remove thinking indicator only if it's still in the layout (avoids crash on 2nd use)
            try:
                layout = getattr(self, 'chat_view', None) and getattr(self.chat_view, 'chat_layout', None)
                if layout and thinking_msg and getattr(thinking_msg, 'parent', None) == layout:
                    layout.remove_widget(thinking_msg)
            except Exception:
                pass
            if error_msg:
                self.chat_view.add_message("Sorry, I encountered an error: " + error_msg, is_user=False)
                if self.tts:
                    self.tts.speak("Sorry, I encountered an error.")
            elif ai_response:
                self.conversation_history.append({'role': 'user', 'content': user_text})
                self.conversation_history.append({'role': 'assistant', 'content': ai_response})
                self.chat_view.add_message(ai_response, is_user=False)
                if self.tts:
                    self.tts.speak(ai_response)
        except Exception as e:
            try:
                self.chat_view.add_message("Error showing response: " + str(e), is_user=False)
            except Exception:
                pass

    def on_enter(self):
        """Called when this screen is entered/displayed"""
        try:
            if not self.welcome_shown:
                self.welcome_shown = True
                welcome_msg = "Hello! I'm your friendly AI assistant. How can I help you today?"
                self.chat_view.add_message(welcome_msg, is_user=False)
                Clock.schedule_once(lambda dt: self._speak_welcome(welcome_msg), 0.6)
        except Exception:
            pass

    def _speak_welcome(self, text):
        """Speak welcome message (called after delay to prevent crash on first TTS)."""
        if text and self.tts:
            self.tts.speak(text)

    def go_back(self, instance):
        """Navigate back to front page"""
        self.manager.current = 'front_page'
