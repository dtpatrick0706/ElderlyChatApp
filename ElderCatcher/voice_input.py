"""
Voice/Speech input module for ElderCatcher chat.
Tap mic to listen until you stop speaking, then send.
Uses a thread only (no subprocess) so no second window opens on Windows.
"""

import threading


class VoiceInputManager:
    """
    Manages voice input. Listens in a background thread.
    """

    def __init__(self):
        self._recording = False

    def listen_async_fallback(self, on_result):
        """
        Tap once to start: listens until silence, then calls on_result(text, error).
        """
        if self._recording:
            return
        self._recording = True

        def listen_thread():
            result_text = None
            error_msg = None
            try:
                import speech_recognition as sr

                r = sr.Recognizer()
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.3)
                    audio = r.listen(source, timeout=8, phrase_time_limit=12)
                result_text = r.recognize_google(audio, language="en-US")
                if result_text:
                    result_text = result_text.strip()
            except ImportError:
                error_msg = "Install: pip install SpeechRecognition pyaudio"
            except Exception as e:
                err = str(e).lower()
                if "timed out" in err or "timeout" in err:
                    error_msg = "No speech detected. Try again."
                elif "not recognized" in err or "no results" in err:
                    error_msg = "Could not understand. Try again."
                else:
                    error_msg = "Voice error: " + str(e)
            finally:
                self._recording = False
                try:
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: on_result(result_text, error_msg), 0)
                except Exception:
                    try:
                        on_result(result_text, error_msg)
                    except Exception:
                        pass

        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()

    @property
    def is_recording(self):
        return self._recording
