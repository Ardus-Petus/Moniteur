# chrome_Playwright.py
import time
import re
import os
import asyncio
from playwright.sync_api import sync_playwright, Locator, Page
from Monitor.core.chrome import Chrome, DOWNLOAD_DIR, port_num
from typing import Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=1)


# ============================================================
# PageEx : wrapper Selenium-like
# ============================================================
class PageEx:
    def __init__(self, page: Page):
        self._page = page

    def locator(self, selector: str, **kwargs):
        return self._page.locator(selector, **kwargs)

    def __getattr__(self, name):
        return getattr(self._page, name)

# ============================================================
# ILocator Playwright — API Selenium-like + click() fiable
# ============================================================
class ILocator:
    def __init__(self, page, locator):
        self.page = page
        self.locator = locator

    # --- API Selenium-like ---
    @property
    def text(self):
        return self.locator.inner_text()

    def click(self):
        # self.locator.click()
        self.page.execute_script("(el) => el.click()", self)

    def get_attribute(self, name):
        return self.locator.get_attribute(name)

    @property
    def inner_html(self):
        return self.locator.inner_html()

    @property
    def outer_html(self):
        return self.locator.outer_html()

    # --- Recherche relative ---
    def findElement(self, selector):
        return ILocator(self.page, self.locator.locator(selector))

    def findElements(self, selector):
        loc = self.locator.locator(selector)
        return [ILocator(self.page, l) for l in loc.all()]

    # --- Indexation / itération ---
    def __getitem__(self, index):
        return ILocator(self.page, self.locator.nth(index))

    def __len__(self):
        return self.locator.count()

    def __iter__(self):
        return (ILocator(self.page, l) for l in self.locator.all())

    # --- clear / send_keys / set_value ---
    def clear(self):
        self.locator.fill("")

    def send_keys(self, text):
        self.locator.type(text)

    def set_value(self, value):
        try:
            self.locator.fill(value)
        except Exception:
            self.page.execute_script("""
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            """, val=value)

    
# ============================================================
# ChromeDriver Playwright — dérivé de Chrome
# ============================================================
class ChromeDriver(Chrome):
    def __init__(self, url: str):
        super().__init__(url)

        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port_num}")
        self.context = self.browser.contexts[0]

        pages = self.context.pages
        self.page = PageEx(pages[0]) if pages else PageEx(self.context.new_page())

        if url:
            self.page.goto(url)

        self._window_stack = []

    # ============================================================
    # findElement / findElements
    # ============================================================
    def findElement(self, selector, base=None):
        root = self.page if base is None else base.locator
        if selector.startswith("//") or selector.startswith(".//"):
            selector = f"xpath={selector}"
        loc = root.locator(selector)
        return ILocator(self, loc) if loc.count() > 0 else None

    def findElements(self, selector, base=None):
        if selector.startswith("//") or selector.startswith(".//"):
            selector = f"xpath={selector}"

        root = self.page if base is None else base.locator
        handles = root.locator(selector).element_handles()

        return [
            ILocator(self, root.locator(f"{selector} >> nth={i}"))
            for i in range(len(handles))
        ]

    def findCells(self, base=None):
        return self.findElements("td", base)

    def get(self, url: str):
        self.page.goto(url)

    @property
    def current_url(self):
        return self.page._page.evaluate("() => location.href")

    # ============================================================
    # waitFor — version Playwright officielle
    # ============================================================
    def waitFor(self, url: str, delay: int):
        pattern = re.compile(url)
        self.page.wait_for_url(pattern, timeout=delay * 1000)
        return self.page.url

    # ============================================================
    # Fenêtres / onglets — identique à Selenium
    # ============================================================
    def new_window(self, type_: str = "tab"):
        self._window_stack.append(self.page)
        new_page = self.context.new_page()
        self.page = PageEx(new_page)

    def switch_to_new_window(self):
        pages = self.context.pages
        if len(pages) > 1:
            self.page = PageEx(pages[-1])

    def get_back_to_original_window(self):
        if self._window_stack:
            self.page = self._window_stack.pop()

    def close_window(self):
        self.page._page.close()
        if self._window_stack:
            self.page = self._window_stack.pop()
            return
        pages = self.context.pages
        if pages:
            self.page = PageEx(pages[-1])

    # ============================================================
    # execute_script Selenium-like
    # ============================================================
    def execute_script(self, script: str, *args: Any)-> Any:
        """
        Exécute un script Selenium-style dans Playwright.
        - Convertit arguments[n] → argN uniquement si nécessaire
        - Ne transforme PAS les scripts déjà au format JS Playwright
        - Convertit ILocator → ElementHandle
        """

        # ============================================================
        # 1) Conversion automatique des ILocator → ElementHandle
        # ============================================================
        fixed_args = []
        for a in args:
            if hasattr(a, "locator"):  # ton wrapper ILocator
                fixed_args.append(a.locator.element_handle())
            else:
                fixed_args.append(a)

        # ============================================================
        # 2) Détection des scripts Selenium (arguments[n])
        # ============================================================
        pattern = r"arguments\[(\d+)\]"
        matches = list(re.finditer(pattern, script))

        # ------------------------------------------------------------
        # CAS 1 : script Selenium → conversion obligatoire
        # ------------------------------------------------------------
        if matches:
            max_index = max(int(m.group(1)) for m in matches)

            if max_index >= len(fixed_args):
                raise ValueError(
                    f"execute_script: script demande arguments[{max_index}] "
                    f"mais seulement {len(fixed_args)} args fournis."
                )

            # Réécriture arguments[n] → argN
            rewritten = script
            for m in matches:
                idx = int(m.group(1))
                rewritten = rewritten.replace(f"arguments[{idx}]", f"arg{idx}")

            # Multi-lignes → bloc { ... }
            multiline = "\n" in rewritten or ";" in rewritten
            params = ", ".join(f"arg{i}" for i in range(max_index + 1))

            if multiline:
                final_script = f"({params}) => {{ {rewritten} }}"
            else:
                final_script = f"({params}) => {rewritten}"

            return self.page.evaluate(final_script, *fixed_args)

        # ------------------------------------------------------------
        # CAS 2 : script déjà au format JS Playwright → PAS de conversion
        # ------------------------------------------------------------
        return self.page.evaluate(script, *fixed_args)
    # ============================================================
    # Téléchargement
    # ============================================================
    def download(self, bouton) -> None:
        for f in os.listdir(DOWNLOAD_DIR):
            os.remove(os.path.join(DOWNLOAD_DIR, f))
        # self.execute_script("arguments[0].click();", bouton)
        bouton.click()
        download = self.page.wait_for_event("download")
        download.save_as(os.path.join(DOWNLOAD_DIR, "download"))
        return os.path.join(DOWNLOAD_DIR, "download")

    def terminate(self):
        try:
            # Fermer la page active
            if hasattr(self, "page") and self.page:
                try:
                    self.page._page.close()
                except:
                    pass

            # Fermer le contexte
            if hasattr(self, "context") and self.context:
                try:
                    self.context.close()
                except:
                    pass

            # # Fermer le browser Playwright
            # if hasattr(self, "browser") and self.browser:
            #     try:
            #         self.browser.close()
            #     except:
            #         pass

            # Arrêter Playwright
            if hasattr(self, "pw") and self.pw:
                try:
                    self.pw.stop()
                except:
                    pass

        finally:
            # Tuer chrome.exe lancé par la classe Chrome
            super().__del__()
