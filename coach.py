import queue
import threading
import time
import winsound
import pythoncom
import win32com.client


class Coach:
    """Speaks and beeps on a background thread so the video never freezes."""

    def __init__(self, min_gap=2.0):
        self.jobs = queue.Queue()
        self.min_gap = min_gap
        self._last = {}
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        pythoncom.CoInitialize()     # COM must be initialised per thread
        voice = win32com.client.Dispatch("SAPI.SpVoice")
        voice.Rate = 1               # -10 slowest .. 10 fastest
        while True:
            kind, value = self.jobs.get()
            if kind == "beep":
                winsound.Beep(value[0], value[1])
            else:
                voice.Speak(value)

    def _too_soon(self, key):
        now = time.time()
        if now - self._last.get(key, 0) < self.min_gap:
            return True
        self._last[key] = now
        return False

    def say(self, text, key=None):
        if not self._too_soon(key or text):
            self.jobs.put(("say", text))

    def beep(self, freq=880, ms=150, key="beep"):
        if not self._too_soon(key):
            self.jobs.put(("beep", (freq, ms)))