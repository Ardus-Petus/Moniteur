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
        """Initialise le navigateur et le WebDriver"""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        exe = CHROMEEXE
        port_num = "9222"
        port_arg = f'--remote-debugging-port={port_num}'
        userdata = f'--user-data-dir={CHROMEPROFILE}'
        self.hwnd = None
        
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
            # On demande explicitement à Chrome d'ignorer la session précédente
            '--disable-extensions',
            '--disable-plugins',
            '--disable-plugins-discovery',
            '--disable-translate',
            '--disable-background-networking',
            '--disable-sync',
            '--disable-default-apps',
        ]
        # Supprime les arguments vides s'il y en a
        args = [arg for arg in args if arg]
        
        self.proc = subprocess.Popen(
            args,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # On laisse 3 secondes à Chrome
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
        
    def waitFor(self, url: str, delay: int) -> None:
        WebDriverWait(self.driver, delay).until(EC.url_matches(url))

    def get(self, url: str) -> None:
        self.driver.get(url)
        self.waitFor(url, 10)  # Attente de 10 secondes pour le chargement de la page

    def findElement(self, value:str):
        return self.driver.find_element(By.XPATH, value)

    def findElements(self, value:str)-> list[WebElement]:
        return self.driver.find_elements(By.XPATH, value)

    def findCells(self, row: WebElement) -> list[WebElement]:
        return row.find_elements(By.TAG_NAME, 'td')

    def terminate(self):
        self.proc.terminate()

def mod_json_file(prefs_path: str, callback: Callable[[dict[str, str]], None]) -> None:
    import json
    with open(prefs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        callback(data)
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)

if __name__ == "__main__":
    url = "https://www.google.com"
    chrome_driver: ChromeDriver = ChromeDriver(url)
    chrome_driver.waitFor(url, 10)
    print("Page loaded successfully.")