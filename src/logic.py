from PySide6.QtCore import QObject, Signal
import time
from typing import Optional
import ctypes
import json

class Session:
    def __init__(self, subject: str, duration: float) -> None:
        if type(subject) != str:
            raise TypeError("invalid subject")
        self.subject = subject

        if type(duration) != float:
            raise TypeError("invalid duration")
        else:
            if duration <= 0.0:
                raise ValueError("invalid duration")
        self.duration = duration

    def timer(self):
        pass

    def end_session(self):
        pass


class SessionTracker:
    def __init__(self) -> None:
        self.session_list = []

    def log_session(self,session: object) -> None:
        self.session_list.append(session)

    def remove_session(self, session: object) -> None:
        #UI will pass exact session as arg
        if session not in self.session_list:
            raise IndexError("session not found")
        self.session_list.remove(session)


    def total_study_time(self):
        #counts all time, not yet accounting for daily / weekly, will implement in the future
        total = 0
        for session in self.session_list:
            total += session.duration
        return total


class StorageHandler:
    def __init__(self) -> None:
        pass



class FocusMonitor(QObject):

    warning_signalled = Signal()

    def __init__(self):
        super().__init__()
        self.warn_toggle = False
        self.unfocus_duration = 0
        self.unfocus_start = None
        self.blacklist = []
        self.user32 = ctypes.windll.user32

    def current_window(self) -> Optional[str]:
        hwnd = self.user32.GetForegroundWindow()
        if not hwnd:
            return None

        h_len = self.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(h_len+1)
        self.user32.GetWindowTextW(hwnd,buf,h_len+1)

        #getwintextw returns an int (len), actual window title stored in buf.value (blame C++)

        return buf.value

    def unfocus_timer(self):
        time_now = time.perf_counter()
        cur_win = self.current_window()
        if cur_win in self.blacklist:  #returns False if None, intentional
            if self.unfocus_start is None:
                self.unfocus_start = time_now

            if time_now - self.unfocus_start >= 5.0:
                if not self.warn_toggle:
                    self.warning_signalled.emit()
                    self.warn_toggle = True

        else:
            self.warn_toggle = False
            self.unfocus_start = None

    #checks current active window
    #has a list of blacklisted/whitelisted tab names
    #sends signal to UI to display reminder if duration > limit
    #has a timer state for distracted duration
    #should be called by QTimer. How? Ill figure it out later


