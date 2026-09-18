# chrome_Selenium.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Monitor.core.chrome import Chrome
from webdriver_manager.chrome import ChromeDriverManager

CHROMEPROFILE = 'O:\\selenium\\chromeprofile'
CHROMEEXE = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

port_num = 9222

class ChromeDriver(Chrome):
    def __init__(self, url: str):
        super().__init__(url)
        try:
            service = Service(ChromeDriverManager().install())
            option = Options()
            option.debugger_address = f"127.0.0.1:{port_num}"
            
            self.driver = webdriver.Chrome(service=service, options=option)
        except Exception as e:
            self.proc.terminate()
            raise e
        self._window_stack = []


    # --- API exposée à tes applis ---
    def findElement(self, selector, base=None):
        by = By.XPATH if selector.startswith("//") or selector.startswith(".//") else By.CSS_SELECTOR
        b = self.driver if base is None else base
        try:
            return b.find_element(by, selector)
        except Exception as e:
            return None

    def findElements(self, selector, base=None):
        by = By.XPATH if selector.startswith("//") or selector.startswith(".//") else By.CSS_SELECTOR
        b = self.driver if base is None else base
        try:
            return b.find_elements(by, selector)
        except Exception as e:
            return []

    def findCells(self, row):
        return row.find_elements(By.TAG_NAME, "td")

    def execute_script(self, script: str, *args):
        return self.driver.execute_script(script, *args)

    def get(self, url: str):
        self.driver.get(url)

    def getCurrentUrl(self) -> str:
        return self.driver.current_url

    def waitFor(self, url: str, delay: int):
        WebDriverWait(self.driver, delay).until(EC.url_matches(url))

    def terminate(self):
        self.proc.terminate()

    def new_window(self, type_: str = "tab"):
        self._window_stack.append(self.driver.current_window_handle)
        self.driver.switch_to.new_window(type_)

    def switch_to_new_window(self):
        handles = self.driver.window_handles
        if len(handles) > 1:
            self.driver.switch_to.window(handles[-1])


    def get_back_to_original_window(self):
        if self._window_stack:
            previous = self._window_stack.pop()
            self.driver.switch_to.window(previous)


    def close_window(self):
        self.driver.close()
        if self._window_stack:
            previous = self._window_stack.pop()
            self.driver.switch_to.window(previous)
