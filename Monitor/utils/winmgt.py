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
def getChromeWindowFromPid(pid: int) -> int:
    result = []

    def callback(hwnd: int, _)-> bool:
        cls = win32gui.GetClassName(hwnd)
        if cls == "Chrome_WidgetWin_1":
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            title = win32gui.GetWindowText(hwnd)
            if title:
                result.append((hwnd, pid, title))
        return True

     # Chrome peut mettre longtemps à afficher sa fenêtre
    for _ in range(60):  # 6 secondes
        win32gui.EnumWindows(callback, None) #type: ignore
        if result:
            break
        time.sleep(0.1)

    
    for _hwnd, _pid, _ in result:
        if _pid == pid: return _hwnd
    with open('hwnds',"w") as dump:
        dump.write(f'pid demandé: {pid}\n')
        for _hwnd, _pid, _title in result:
            dump.write(f'hwnd:{_hwnd}, pid:{_pid}, title:{_title}\n')

                   
    raise ValueError(f"Aucune fenêtre Chrome trouvée pour le PID {pid}.")

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
