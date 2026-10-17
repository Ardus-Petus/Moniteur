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
        self.element = element

    # --- API Selenium-like ---
    @property
    def text(self):
        return self.element.text

    def click(self):
        self.element.click()

    def get_attribute(self, name):
        return self.element.get_attribute(name)

    @property
    def inner_html(self):
        return self.element.get_attribute("innerHTML")

    @property
    def outer_html(self):
        return self.element.get_attribute("outerHTML")

    # --- Recherche relative ---
    def findElement(self, selector):
        return ILocator(self.driver, self.element.find_element(By.CSS_SELECTOR, selector))

    def findElements(self, selector):
        return [ILocator(self.driver, e) for e in self.element.find_elements(By.CSS_SELECTOR, selector)]

    # --- Indexation / itération ---
    def __getitem__(self, index):
        return ILocator(self.driver, self.element.find_elements(By.XPATH, "*")[index])

    def __len__(self):
        return len(self.element.find_elements(By.XPATH, "*"))

    def __iter__(self):
        return (ILocator(self.driver, e) for e in self.element.find_elements(By.XPATH, "*"))

    # --- clear / send_keys / set_value ---
    def clear(self):
        # Tentative standard
        try:
            self.element.clear()
            return
        except Exception:
            pass

        # Fallback JS universel
        self.driver.execute_script("""
            arguments[0].value = '';
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, self.element)

    def send_keys(self, text):
        # Tentative standard
        try:
            self.element.send_keys(text)
            return
        except Exception:
            pass

        # Fallback JS universel
        self.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, self.element, text)

    def set_value(self, text):
        self.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, self.element, text)    # --- execute_script (Selenium) ---
        
    def execute_script(self, script: str, *args):
        # 1) Convertit les ILocator → WebElement
        fixed_args = []
        for a in args:
            if isinstance(a, ILocator):
                fixed_args.append(a.element)
            else:
                fixed_args.append(a)

        # 2) Réécrit le script : "el" → "arguments[i]"
        # Exemple : el.setAttribute(...)  → arguments[0].setAttribute(...)
        for i in range(len(fixed_args)):
            script = script.replace(f"el", f"arguments[{i}]")

        # 3) Exécute le script Selenium
        return self.driver.execute_script(script, *fixed_args)

class ChromeDriver(Chrome):
    def __init__(self, url: str):
        super().__init__(url)

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port_num}")

        self.driver = webdriver.Chrome(options=chrome_options)
        # self.wait = WebDriverWait(self.driver, 30)

    def findElement(self, selector, base=None):
        root = self.driver if base is None else base._el
        if selector.startswith("//") or selector.startswith(".//"):
            el = root.find_element(By.XPATH, selector)
        else:
            el = root.find_element(By.CSS_SELECTOR, selector)
        return ILocator(self, el)

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
        WebDriverWait(self.driver, delay).until(EC.url_matches(url))
        return self.driver.current_url

    def new_window(self, type_: str = "tab"):
        self.driver.switch_to.new_window(type_)

    def switch_to_new_window(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def get_back_to_original_window(self):
        self.driver.switch_to.window(self.driver.window_handles[0])

    def close_window(self):
        self.driver.close()
        # if self.driver.window_handles:
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def execute_script(self, script: str, *args):
        fixed_args = []

        # Convertit ILocator → WebElement
        for a in args:
            if isinstance(a, ILocator):
                fixed_args.append(a.element)
            else:
                fixed_args.append(a)

        # Réécriture automatique du script :
        # "el" → "arguments[i]"
        for i in range(len(fixed_args)):
            script = script.replace("el", f"arguments[{i}]")

        return self.driver.execute_script(script, *fixed_args)

    def download(self, bouton):
        import os, time

        # Nettoyer le dossier
        for f in os.listdir(DOWNLOAD_DIR):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, f))
            except:
                pass

        # Clic via ILocator.click()
        time.sleep(0.5)  # Attendre un court instant avant de cliquer
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
