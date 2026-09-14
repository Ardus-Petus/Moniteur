import os
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Monitor.utils.winmgt import getChromeWindowFromPid

from typing import Callable, Any

os.environ['WDM_LOCAL'] = '0'
os.environ['WDM_SSL_VERIFY'] = '0'
from webdriver_manager.chrome import ChromeDriverManager
import urllib3

CHROMEPROFILE = 'O:\\selenium\\chromeprofile'
CHROMEEXE = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

class ChromeDriver():

    def __init__(self,url:str):
        """Classe pour ouvrir Chrome avec un Webdriver."""
        exe = CHROMEEXE
        port_num = "9222"
        port_arg = f'--remote-debugging-port={port_num}'
        userdata = f'--user-data-dir={CHROMEPROFILE}'
        self.hwnd = None
        # === pile de fenêtres ===
        self._window_stack = []

        # === 1. FORCE LA RÉINITIALISATION DU FLAG DE CRASH ===
        prefs_path = os.path.join(CHROMEPROFILE, 'Default', 'Preferences')
        if os.path.exists(prefs_path):
            def mod_profile(data: dict[str, Any]) -> None:
                data['profile']['exit_type'] = "Normal"
                data['profile']['exited_cleanly'] = True
            mod_json_file(prefs_path, mod_profile)

        # === 2. ARGUMENTS POUR DEMARRER SANS LES ANCIENS ONGLETS ===
        args = [
            exe,
            url,
            port_arg,
            userdata,
            '--disable-session-crashed-bubble',
            '--no-first-run',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-plugins-discovery',
            '--disable-translate',
            '--disable-background-networking',
            '--disable-sync',
            '--disable-default-apps',
        ]
        args = [arg for arg in args if arg]

        self.proc = subprocess.Popen(
            args,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )

        time.sleep(3)

        self.hwnd = getChromeWindowFromPid(self.proc.pid)
        urllib3.disable_warnings()
        option = Options()
        option.debugger_address = f"127.0.0.1:{port_num}"

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=option)
        except Exception as e:
            self.proc.terminate()
            raise e

    # ============================================================
    #  PRIMITIVES EXISTANTES
    # ============================================================

    def execute_script(self, script: str, *args) -> Any:
        return self.driver.execute_script(script, *args)

    def waitFor(self, url: str, delay: int) -> None:
        WebDriverWait(self.driver, delay).until(EC.url_matches(url))

    def get(self, url: str) -> None:
        self.driver.get(url)

    def findElement(self, selector:str, base=None)->WebElement:
        if base is None:
            return self.driver.find_element(By.XPATH, selector)
        else:
            return base.find_element(By.XPATH, selector)

    def findElements(self, selector:str, base=None)-> list[WebElement]:
        if base is None:
            return self.driver.find_elements(By.XPATH, selector)
        else:
            return base.find_elements(By.XPATH, selector)

    def findCells(self, row: WebElement) -> list[WebElement]:
        return row.find_elements(By.TAG_NAME, 'td')

    # ============================================================
    #  NOUVELLES PRIMITIVES FENÊTRES
    # ============================================================

    def switch_to_new_window(self):
        """Attendre et basculer vers une nouvelle fenêtre/onglet."""
        before = set(self.driver.window_handles)

        WebDriverWait(self.driver, 10).until(
            lambda d: len(d.window_handles) > len(before)
        )

        after = set(self.driver.window_handles)
        new_handle = (after - before).pop()

        self._window_stack.append(self.driver.current_window_handle)
        self.driver.switch_to.window(new_handle)

    def get_back_to_original_window(self):
        """Revenir à la fenêtre précédente."""
        if not self._window_stack:
            return

        previous = self._window_stack.pop()
        self.driver.switch_to.window(previous)

    def close_window(self):
        """Fermer la fenêtre courante et revenir à la précédente si possible."""
        self.driver.close()

        if self._window_stack:
            previous = self._window_stack.pop()
            self.driver.switch_to.window(previous)

    # ============================================================

    def terminate(self):
        self.proc.terminate()


def mod_json_file(prefs_path: str, callback: Callable[[dict[str, str]], None]) -> None:
    import json
    with open(prefs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        callback(data)
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
