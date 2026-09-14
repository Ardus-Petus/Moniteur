import time
import win32gui
import win32process
import win32con

def get_stable_chrome_hwnd(pid: int) -> int | None:
    hwnds = []

    def callback(hwnd, _):
        # Vérifie le PID
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid != pid:
            return True

        # Fenêtre visible
        if not win32gui.IsWindowVisible(hwnd):
            return True

        # Fenêtre principale = pas de parent
        if win32gui.GetParent(hwnd) != 0:
            return True

        # Titre non vide
        title = win32gui.GetWindowText(hwnd)
        if not title.strip():
            return True

        # Style de fenêtre normale
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        if not (style & win32con.WS_OVERLAPPEDWINDOW):
            return True

        hwnds.append(hwnd)
        return True

    # Attente intelligente : Chrome crée la vraie fenêtre un peu plus tard
    for _ in range(30):  # 3 secondes max
        win32gui.EnumWindows(callback, None)
        if hwnds:
            break
        time.sleep(0.1)

    return hwnds[0] if hwnds else None

def getChromeWindowFromPid(pid: int) -> int:
    def callback(hwnd: int, _)-> bool:
        cls = win32gui.GetClassName(hwnd)
        if cls == "Chrome_WidgetWin_1":
        # if cls.startswith("Chrome"):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            title = win32gui.GetWindowText(hwnd)
            result.append((hwnd, pid, cls, title))
        return True

     # Chrome peut mettre longtemps à afficher sa fenêtre
    for _ in range(60):  # 6 secondes
        result = []
        win32gui.EnumWindows(callback, None) #type: ignore
        if result:
            break
        time.sleep(0.1)

    
    with open('O:\\hwnds.txt',"w") as dump:
        dump.write(f'pid demandé: {pid}\n')
        for _hwnd, _pid, _cls,_title in result:
            dump.write(f'hwnd:{_hwnd}, pid:{_pid}, cls:{_cls} title:{_title}\n')

    for _hwnd, _pid, _cls, _title in result:
        if _pid == pid: return _hwnd
    
                   
    raise ValueError(f"Aucune fenêtre Chrome trouvée pour le PID {pid}.")
