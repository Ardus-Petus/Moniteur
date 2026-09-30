# chrome_Selenium.py
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Monitor.core.chrome import Chrome, port_num, DOWNLOAD_DIR

class ILocator:
    def __init__(self, driver, element):
        self.driver = driver
        self._el = element

    def click(self):
        self.driver.execute_script("arguments[0].click();", self._el)
        return self.driver.current_url

    @property
    def text(self):
        return self._el.text

    def get_attribute(self, name):
        return self._el.get_attribute(name)

    @property
    def inner_html(self):
        return self._el.get_attribute("innerHTML")

    @property
    def outer_html(self):
        return self._el.get_attribute("outerHTML")

class ChromeDriver(Chrome):
    def __init__(self, url: str):
        super().__init__(url)

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port_num}")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)

    def findElement(self, selector, base=None):
        root = self.driver if base is None else base._el
        try:
            if selector.startswith("//") or selector.startswith(".//"):
                el = root.find_element(By.XPATH, selector)
            else:
                el = root.find_element(By.CSS_SELECTOR, selector)
            return ILocator(self, el)
        except:
            return None

    def findElements(self, selector, base=None):
        root = self.driver if base is None else base._el
        try:
            if selector.startswith("//") or selector.startswith(".//"):
                els = root.find_elements(By.XPATH, selector)
            else:
                els = root.find_elements(By.CSS_SELECTOR, selector)
            return [ILocator(self, el) for el in els]
        except:
            return []

    def findCells(self, base=None):
        return self.findElements("td", base)

    def get(self, url: str):
        self.driver.get(url)

    @property
    def current_url(self):
        return self.driver.current_url

    def waitFor(self, url: str, delay: int):
        pattern = re.compile(url)
        WebDriverWait(self.driver, delay).until(EC.url_matches(pattern))
        return self.driver.current_url

    def new_window(self, type_: str = "tab"):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_to_new_window(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def get_back_to_original_window(self):
        self.driver.switch_to.window(self.driver.window_handles[0])

    def close_window(self):
        self.driver.close()
        if self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[-1])

    def execute_script(self, script, *args):
        script = script.strip()
        if script.startswith("(") and "=>" in script:
            m = re.match(r"\((.*?)\)\s*=>\s*(.*)", script)
            if m:
                params = [p.strip() for p in m.group(1).split(",")]
                body = m.group(2).strip()
                for i, p in enumerate(params):
                    body = body.replace(p, f"arguments[{i}]")
                if body.startswith("{") and body.endswith("}"):
                    body = body[1:-1].strip()
                return self.driver.execute_script(body, *args)
        return self.driver.execute_script(script, *args)

    def download(self, bouton):
        import os, time

        # Nettoyer le dossier
        for f in os.listdir(DOWNLOAD_DIR):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, f))
            except:
                pass

        # Clic via ILocator.click()
        bouton.click()

        # Attendre le fichier
        timeout = 30
        end = time.time() + timeout

        while time.time() < end:
            files = os.listdir(DOWNLOAD_DIR)
            done = [f for f in files if not f.endswith(".crdownload")]
            if done:
                return os.path.join(DOWNLOAD_DIR, done[0])
            time.sleep(0.1)

        raise TimeoutError("Aucun fichier téléchargé dans le délai")


    def terminate(self):
        self.driver.quit()
