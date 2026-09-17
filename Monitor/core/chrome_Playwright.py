# chrome_Playwright.py
from gettext import find
import time
import re
from playwright.sync_api import sync_playwright, Locator, Page
#from Monitor.core.Playwright_classes import PageEx
from Monitor.core.chrome import Chrome  
from typing import Any

# ============================================================
# PageEx : wrapper autour de Page Playwright pour API Selenium-like
# ============================================================
class PageEx:
    def __init__(self, page: Page):
        self._page = page

    def locator(self, selector: str, **kwargs) -> ILocator:
        loc = self._page.locator(selector, **kwargs)
        return loc

    def __getattr__(self, name):
        return getattr(self._page, name)

# ============================================================
# ILocator : version stable, CDP-safe, API Selenium-like
# ============================================================
class ILocator:
    def __init__(self, locator: Locator):
        self._loc = locator
   
    # --- API Selenium-like ---
    @property
    def text(self):
        return self._loc.inner_text()

    def click(self):
        self._loc.click()

    def get_attribute(self, name):
        return self._loc.get_attribute(name)

    @property
    def inner_html(self):
        return self._loc.inner_html()

    @property
    def outer_html(self):
        return self._loc.outer_html()

    # --- Indexation / itération ---
    def __getitem__(self, index):
        if isinstance(index, slice):
            all_locators = self._loc.all()
            sliced = all_locators[index]
            return ILocatorList(sliced)
        return ILocator(self._loc.nth(index))

    def __len__(self):
        return self._loc.count()

    def __iter__(self):
        yield from (ILocator(l) for l in self._loc.all())

    def __getattr__(self, name):
        return getattr(self._loc, name)
    
# ============================================================
# ILocatorList : liste d’ILocator
# ====================================================
class ILocatorList:
    def __init__(self, locators):
        self._locs = [ILocator(l) for l in locators]

    def __getitem__(self, index):
        if isinstance(index, slice):
            return ILocatorList(self._locs[index])
        return self._locs[index]

    def __len__(self):
        return len(self._locs)

    def __iter__(self):
        return iter(self._locs)

    def __repr__(self):
        return f"ILocatorList({self._locs})"

    

# ============================================================
# ChromeDriver Playwright — Chrome déjà lancé par classe parente
# ============================================================
class ChromeDriver(Chrome):   # ← ta classe parente
    def __init__(self, url: str, port=9222):
        super().__init__(url)             # ← tu l’as demandé

        # 1. Attendre que Chrome ouvre le port CDP
        import socket
        for _ in range(50):
            try:
                s = socket.socket()
                s.settimeout(0.1)
                s.connect(("127.0.0.1", port))
                s.close()
                break
            except:
                time.sleep(0.1)

        # 2. Connexion Playwright via CDP
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")

        # 3. Récupérer le contexte Chrome existant
        self.context = self.browser.contexts[0]

        # 4. Récupérer l’onglet existant ou en ouvrir un
        pages = self.context.pages
        self.page = PageEx(pages[0]) if pages else PageEx(self.context.new_page())

        # 5. Charger l’URL demandée
        if url:
            self.page.goto(url)

        self._window_stack = []

    # ============================================================
    # findElement / findElements — API identique à Selenium
    # ============================================================
    
    def findElement(self, selector, base=None):
        b = self.page if base is None else base._loc
        if selector.startswith("//") or selector.startswith(".//"):
            selector = f"xpath={selector}"
        loc = b.locator(selector)
        return ILocator(loc) if loc.count() > 0 else None

    def findElements(self, selector, base=None):
        # XPATH → Playwright format
        if selector.startswith("//") or selector.startswith(".//"):
            selector = f"xpath={selector}"

        # Base = page ou locator
        root = self.page if base is None else base.locator

        # Récupération SANS scroll
        handles = root.locator(selector).element_handles()

        # Conversion en ILocator
        locators = [
            ILocator(root.locator(f"{selector} >> nth={i}"))
            for i in range(len(handles))
        ]

        return locators

    def findCells(self, base=None):
        return self.findElements("td", base)
    
    # ============================================================
    # Divers
    # ============================================================
    def get(self, url: str):
        self.page.goto(url)

    def waitFor(self, url: str, delay: int):
        self.page.wait_for_url(re.compile(url), timeout=delay * 1000)

    def terminate(self):
        # self.pw.stop()
        pass
    # ============================================================
    #  FENÊTRES / ONGLET — version Playwright (équivalente Selenium)
    # ============================================================

    def new_window(self, type_: str = "tab"):
        """Ouvre un nouvel onglet ou une nouvelle fenêtre."""
        # On empile la fenêtre courante
        self._window_stack.append(self.page)

        if type_ == "tab":
            # Playwright ouvre un nouvel onglet dans le même contexte
            new_page = self.context.new_page()
        else:
            # Playwright n'a pas de "window" séparée, mais new_page() suffit
            new_page = self.context.new_page()

        # On bascule sur la nouvelle page
        self.page = PageEx(new_page)


    def switch_to_new_window(self):
        """Bascule sur la dernière fenêtre ouverte."""
        pages = self.context.pages
        if len(pages) > 1:
            self.page = PageEx(pages[-1])


    def get_back_to_original_window(self):
        """Retourne à la fenêtre précédente."""
        if self._window_stack:
            previous = self._window_stack.pop()
            self.page = previous


    def close_window(self):
        """Ferme la fenêtre courante et revient à la précédente."""
        # On ferme la page Playwright
        self.page._page.close()

        # Si on a une fenêtre précédente dans la pile
        if self._window_stack:
            previous = self._window_stack.pop()
            self.page = previous
            return

        # Sinon fallback : dernière page restante
        pages = self.context.pages
        if pages:
            self.page = PageEx(pages[-1])


    # ============================================================
    # Exécution de scripts JavaScript dans Playwright
    # ============================================================
    def execute_script(self, script: str, *args: Any):
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
            if hasattr(a, "_loc"):  # ton wrapper ILocator
                fixed_args.append(a._loc.element_handle())
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
