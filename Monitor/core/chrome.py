import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from Monitor.utils.getChromeHwnd import get_stable_chrome_hwnd

from webdriver_manager.chrome import ChromeDriverManager
import urllib3


CHROMEPROFILE = 'O:\\selenium\\chromeprofile'
CHROMEEXE = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


class Chrome:
    def __init__(self, url: str):
        port = 9222

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
    
