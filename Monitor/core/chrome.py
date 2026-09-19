import subprocess
import time
from Monitor.utils.getChromeHwnd import get_stable_chrome_hwnd
import os
from typing import Any, Callable


CHROMEPROFILE = 'O:\\selenium\\chromeprofile'
CHROMEEXE = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


class Chrome:
    def __init__(self, url: str):
        port = 9222

       # === 1. FORCE LA RÉINITIALISATION DU FLAG DE CRASH ===
        prefs_path = os.path.join(CHROMEPROFILE, 'Default', 'Preferences')
        if os.path.exists(prefs_path):
            def mod_profile(data: dict[str, Any]) -> None:
                data['profile']['exit_type'] = "Normal"
                data['profile']['exited_cleanly'] = True
            mod_json_file(prefs_path, mod_profile)       

         # 1. Lancer Chrome manuellement avec profil + remote debugging
        args = [
            CHROMEEXE,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={CHROMEPROFILE}",
            "--disable-session-crashed-bubble",
            "--no-first-run",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-plugins-discovery",
            "--disable-translate",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            url,
        ]

        self.proc = subprocess.Popen(args)

        # 2. Attendre que Chrome ouvre le port CDP
        #    (sinon EPIPE garanti)
        for _ in range(50):
            try:
                import socket
                s = socket.socket()
                s.settimeout(0.1)
                s.connect(("127.0.0.1", port))
                s.close()
                break
            except:
                time.sleep(0.1)
        else:
            raise RuntimeError("Chrome n'a pas ouvert le port CDP")
        self.hwnd = get_stable_chrome_hwnd(self.proc.pid)

def __del__(self):
        if hasattr(self, 'proc'):
            subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"])

def mod_json_file(prefs_path: str, callback: Callable[[dict[str, str]], None]) -> None:
    import json
    with open(prefs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        callback(data)
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)


