import os
from typing import Any
# from Monitor.core.chrome_Selenium import ChromeDriver
from Monitor.core.chrome_Protocol import ChromeProtocol, ILocatorProtocol, PageExProtocol
from Banque.core.Ope import Ope
from abc import ABC, abstractmethod

os.environ['WDM_LOCAL'] = '0'
os.environ['WDM_SSL_VERIFY'] = '0'

class HTML(ABC):
    URL: str  # à définir dans chaque sous-classe

    def __init__(self, cls_driver):
        self.chrome: ChromeProtocol = cls_driver(self.URL)
        self.proc = self.chrome.proc
        self.hwnd = self.chrome.hwnd

    def quit(self) -> None:
        """Ferme proprement Selenium et le processus Chrome associé."""
        self.chrome.terminate()
        self.proc.terminate()
        self.proc.wait()

    def waitFor(self, url: str, delay: int) -> str:
        ret = self.chrome.waitFor(url, delay)
        return ret

    def findElement(self, selector: str, base: Any = None) -> ILocatorProtocol:
        return self.chrome.findElement(selector, base)

    def findElements(self, selector: str, base: Any = None) -> list[ILocatorProtocol]:
        return self.chrome.findElements(selector, base)

    def findCells(self, base: Any = None) -> list[ILocatorProtocol]:
        return self.chrome.findCells(base)

    def get(self, url: str) -> None:
        self.chrome.get(url)

    def download(self, bouton: ILocatorProtocol) -> str:
        return self.chrome.download(bouton)

    def new_window(self) -> None:
        self.chrome.new_window()

    def switch_to_new_window(self) -> None:
        self.chrome.switch_to_new_window()

    def get_back_to_original_window(self) -> None:
        self.chrome.get_back_to_original_window()

    def close_window(self) -> None:
        self.chrome.close_window()

    def execute_script(self, script: str, *args: Any) -> Any:
        return self.chrome.execute_script(script, *args)
    
    # Méthodes qui doivent être implémentées dans une classe dérivée
    @abstractmethod
    def waitForCnxComptes(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def waitForRelevé(self) -> None:                        # Initialise le tableau self.rows avec la liste des opérations,
        raise NotImplementedError()
    
    @abstractmethod
    def getAcctNo(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def getSolde(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def getHTMLOpe(self, i: int) -> Ope:
        raise NotImplementedError()

    @abstractmethod
    def get_liste_comptes(self) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def charger_page_releve(self, compte) -> None:
        raise NotImplementedError
