import time
import win32gui
import win32con
import win32api
import win32process 
import ctypes
import pyautogui

# Récupération de la résolution de l'écran
# ---------------------------------------------------------
def get_screen_size() -> tuple[int, int]:
    w = win32api.GetSystemMetrics(0)
    h = win32api.GetSystemMetrics(1)
    return w, h

# Récupération du HWND de la fenêtre active et renommage
# ---------------------------------------------------------
def getCurrentHwnd() -> int:
    hwnd_potentiel = win32gui.GetForegroundWindow()
    jeton_unique = f"New_Window_{time.time()}"
    win32gui.SetWindowText(hwnd_potentiel, jeton_unique) #type: ignore
    time.sleep(0.02)
    hwnd_console = win32gui.FindWindow(None, jeton_unique)
    return hwnd_console

# Positionnement et redimensionnement de la fenêtre
# ---------------------------------------------------------
def setWindowPos(hwnd: int, x: int, y: int, w: int, h: int) -> None:
    restore(hwnd)
    win32gui.SetWindowPos(
        hwnd, win32con.HWND_TOP, 
        x, y, w, h, 
        win32con.SWP_SHOWWINDOW
    )
    pass

# Fermeture forcée de la fenêtre via Windows
# ---------------------------------------------------------
def close_window(hwnd: int) -> None:
    #Envoie un message WM_CLOSE à la fenêtre spécifiée pour la fermer.
    # WM_CLOSE (0x0010) force la fenêtre Windows à se détruire immédiatement
    # ce qui ferme le prompt système.
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
 
# Récupérer le HWND d’un processus *
# ---------------------------------------------------------

# Réduire la fenêtre
# ---------------------------------------------------------
def minimize(hwnd: int)-> None:
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

# Restaurer la fenêtre
# --------------------------------------------------------- 
def restore(hwnd: int)-> None:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) 

# Maximiser la fenêtre
# ---------------------------------------------------------     
def maximize(hwnd: int)-> None: 
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def focus(hwnd: int) -> None:
    # Force la fenêtre à passer au premier plan
    # Source - https://stackoverflow.com/a/76386100
    # Posted by crxyz
    # Retrieved 2026-06-05, License - CC BY-SA 4.0

    pyautogui.press("alt")

    win32gui.SetForegroundWindow(hwnd)
    win32gui.BringWindowToTop(hwnd)

def getParentHwnd(hwndTk: int) -> int:
    # Récupération du a HWND parent
    return ctypes.windll.user32.GetParent(hwndTk)
