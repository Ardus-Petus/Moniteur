# geometry.py
import Monitor.utils.winmgt as winmgt
import ctypes
from win32api import GetMonitorInfo, MonitorFromPoint

class Presentation:
    
    def __init__(self):
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # PER_MONITOR_AWARE_V2
        rect = GetMonitorInfo(MonitorFromPoint((0,0)))['Work']  # Dimension de l'écran sans compter la TaskBar
        _, _, self.screen_width, self.screen_height =  rect
        self.mid_x = self.screen_width * 1 // 2
        self.mid_w = self.screen_width - self.mid_x
        self.margin = 0
        self.bordure = 0

    def pos_right(self, hwnd: int):
        winmgt.setWindowPos(
            hwnd=hwnd,
            x=self.mid_x + self.margin - self.bordure,
            y=self.margin - self.bordure,
            w=self.mid_w - 2 * self.margin + 2 * self.bordure,
            h=self.screen_height - 2 * self.margin + 2 * self.bordure
        )

    def pos_left(self, hwnd:int):
        winmgt.setWindowPos(
            hwnd=hwnd,
            x=self.margin - self.bordure,
            y=self.margin - self.bordure,
            w=self.mid_w - 2 * self.margin + 2 * self.bordure,
            h=self.screen_height - 2 * self.margin + 2 * self.bordure
        )

    def position(self, pos:str):
        return {
            'gauche': self.pos_left,
            'droite': self.pos_right
        }[pos]

    def filter(self,msg_type, payload, pos):
        if msg_type == "html_opened":
            hwnd_html = payload
            pos(hwnd_html)
            winmgt.focus(hwnd_html)
            return True

        elif msg_type == "XL_opened":
            hwnd_excel = payload
            pos(hwnd_excel)
            return True

        return False
