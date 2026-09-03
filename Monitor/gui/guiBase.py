import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
import queue
import ctypes
from typing import Callable, Any

PINK = "#FFAED0"
GREY = "#B5B5B5"

# ============================================================
# GUI
# ============================================================

class guiBase:
    def __init__(self, context) -> None:
        self.context = context
        root=context['gui_root']
        self.root = root
        self.gui_queue, self.metier_queue = context["queues"]
        self.premier_appel = True           # Flag pour gui_updater
        self.responseform=None
        root.title(__file__)
        icon_path = os.path.join(os.path.dirname(__file__), '_gui_.ico')
        root.iconbitmap(icon_path) #type: ignore
        W = root.winfo_screenwidth()
        H = root.winfo_screenheight()
        self.ratio = W/1920
        self.style = ttk.Style()
        self.erreur = None
        self.scaling = float(root.tk.call('tk', 'scaling'))

    def close(self) -> None:
        self.root.destroy()

    # ============================================================
    # GUI update loop
    # ============================================================
    def update(self)->None:

        if self.premier_appel:
            setpos = self.context.get('position')
            if setpos:
                #self.root.propagate(False)  # On empêche le redimensionnement automatique de la fenêtre
                setpos(ctypes.windll.user32.GetParent(self.root.winfo_id()))
                simulate_manual_resize(self.root)
        self.premier_appel = False
    
        try:
            while True:
                msg_type, payload = self.gui_queue.get_nowait()
                if msg_type[0] == '!':
                    self.traiter_champ(msg_type[1:], payload)
                else:
                    proc = getattr(self, f'traiter_{msg_type}')
                    proc(msg_type, payload)

        except queue.Empty:
            pass

        self.root.after(100, self.update)

    def traiter_champ(self, msg_type, payload):
        entry = getattr(self,f'Entry_{msg_type.replace(' ', '_')}')
        entry.delete(0, 'end')
        entry.insert(0, payload)
        if msg_type == "Erreur":
            entry.configure(background=PINK)



#-----------------------
# Procedures utilitaires
#-----------------------
def simulate_manual_resize(root)->None:
    w = root.winfo_width()
    h = root.winfo_height()

    for delta in (1, -1):
        root.geometry(f"{w+delta}x{h}")
        root.update_idletasks()

def font_bold() ->tkfont.Font:
    font = tkfont.nametofont("TkDefaultFont").copy()
    font.configure(weight="bold")
    return font

if __name__ == "__main__":
    context = {}
    root = tk.Tk()
    gui_queue = queue.Queue()
    context['queues'] = gui_queue, None
    context['gui_root'] = root
    mygui = guiBase(context)
    root.after(100, mygui.update)
    root.mainloop()
    