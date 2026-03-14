"""
Text-to-Speech manager for ElderCatcher chat.
Uses pyttsx3 in a dedicated worker thread to avoid blocking Kivy's main loop
and prevent crashes that occur when TTS runs on the main thread.
"""

import threading
import queue


class TTSManager:
    """
    Thread-safe TTS manager. All speech runs in a single background thread
    to avoid pyttsx3's "run loop already started" and main-thread crash issues.
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._running = True
        self._thread = None
        self._started = False

    def _get_natural_english_voice(self, engine):
        """Select the most natural-sounding English voice available on the system."""
        voices = engine.getProperty('voices')
        # Prefer Natural/Neural voices (Windows 10/11) - they sound more human
        natural_keywords = ('natural', 'neural', 'aria', 'jenny', 'guy', 'sara', 'online')
        english_voice = None
        natural_voice = None
        for v in voices:
            langs = getattr(v, 'languages', []) or []
            name = (getattr(v, 'name', '') or '').lower()
            is_english = any(lang and ('en' in str(lang).lower()) for lang in langs)
            if is_english:
                if not english_voice:
                    english_voice = v.id
                if any(kw in name for kw in natural_keywords):
                    natural_voice = v.id
                    break
        return natural_voice or english_voice or (voices[0].id if voices else None)

    def _worker(self):
        """Worker runs in its own thread - engine must be created and used here only."""
        while self._running:
            try:
                text = self._queue.get(timeout=0.3)
                if text is None:
                    break
                if not text:
                    continue
                # One message at a time; wrap everything so one failure never kills the worker
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    try:
                        voice_id = self._get_natural_english_voice(engine)
                        if voice_id:
                            engine.setProperty('voice', voice_id)
                        rate = engine.getProperty('rate')
                        engine.setProperty('rate', min(rate, 150))
                        engine.say(text)
                        engine.runAndWait()
                    finally:
                        try:
                            del engine
                        except Exception:
                            pass
                        # Brief pause so OS releases audio before next message (reduces 2nd-use crash)
                        try:
                            import time
                            time.sleep(0.2)
                        except Exception:
                            pass
                except Exception as e:
                    print("TTS error:", e)
            except queue.Empty:
                continue
            except Exception as e:
                print("TTS worker:", e)
                continue

    def _ensure_started(self):
        """Start worker thread on first use (lazy init)."""
        if not self._started:
            self._started = True
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()

    def speak(self, text):
        """Queue text for speech. Safe to call from any thread (e.g. Kivy main thread)."""
        if not text or not isinstance(text, str):
            return
        text = text.strip()
        if not text:
            return
        self._ensure_started()
        try:
            self._queue.put_nowait(text)
        except queue.Full:
            pass  # Skip if queue is full to avoid blocking

    def stop(self):
        """Stop the TTS worker. Call when app is closing."""
        self._running = False
        if self._started:
            try:
                self._queue.put(None)
            except Exception:
                pass
