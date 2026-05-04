from PySide6.QtCore import QObject, Signal
import time
from typing import Optional
import ctypes
import json


#REMINDER: CONTROLLER CONTROLS TIMING, NONE OF THE BELOW SHOULD

class Subject:
    def __init__(self, subject: str, desc: Optional[str], tags: Optional[list[str]]) -> None:
        if type(subject) != str:
            raise TypeError("invalid subject")

        self.subject = subject
        self.description = desc
        self.tags = tags

    def jsonify(self):
        converted = {
            "subject": self.subject,
            "description": self.description,
            "tags": self.tags
        }
        return converted

    def un_jsonify(self):

class SubjectManager: #container for subject objects
    def __init__(self):
        self.subject_list = []

    def add_subject(self, subject: object):
        self.subject_list.append(subject)

    def remove_subject(self,subject:object):
        if subject not in self.subject_list:
            raise IndexError("subject not found")
        self.subject_list.remove(subject)

    def convert_to_json(self) -> list[dict[str,str]]:


#Session & SessionTracker below serve only to contain current / past sessions
class Session:
    def __init__(self, subject: str)-> None:
        if type(subject) != str:
            raise TypeError("invalid subject")

        self.subject = subject
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.is_active = False

    def start_sesh(self,start_time: float=None):
        self.is_active = True
        self.start_time = start_time

    def end_sesh(self,time_now: float=None) -> None:
        #time_now passed from controller
        if not self.is_active:
            pass
        else:
            if time_now is None:
                time_now = time.time()

            self.duration = time_now - self.start_time
            self.end_time = time_now
            self.is_active = False

    def jsonify(self):
        converted = {
            "subject": self.subject,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration
        }
        return converted

class SessionTracker:
    def __init__(self) -> None:
        self.active_session = None
        self.session_list = []

    def start_session(self,subject: str):
        self.active_session = Session(subject)
        self.active_session.start_sesh(time.time())

    def end_session(self):
        self.active_session.end_sesh(time.time())
        self.log_session(self.active_session)
        self.active_session = None

    def log_session(self,session: object) -> None:
        self.session_list.append(session)

    def remove_session(self, session: object) -> None:
        if session not in self.session_list:
            raise IndexError("session not found")
        self.session_list.remove(session)


    def total_study_time(self) -> None:
        #counts all time, not yet accounting for daily / weekly, will implement in the future
        total = 0
        for session in self.session_list:
            total += session.duration
        return total


#FIX this
class StorageHandler:
    def __init__(self) -> None:
        self.file_path = None

    def set_file_path(self,path):
        if type(path) != str:
            raise TypeError("Invalid path")
        self.file_path = path

    def read_json(self):
        pass

    def write_json(self):
        pass



class FocusMonitor(QObject):

    warning_signalled = Signal()
    #will link to controller

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


