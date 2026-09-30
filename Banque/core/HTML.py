import os
# from Monitor.core.chrome_Selenium import ChromeDriver
from Monitor.core.chrome_Protocol import ChromeProtocol
from Banque.core.Ope import Ope
from abc import ABC, abstractmethod

os.environ['WDM_LOCAL'] = '0'
os.environ['WDM_SSL_VERIFY'] = '0'

class HTML(ABC):
    def __init__(self, url:str, cls_driver):
        self.chrome: ChromeProtocol = cls_driver(url)
        self.proc = self.chrome.proc
        self.hwnd = self.chrome.hwnd

        # self.waitFor = self.chrome.waitFor
        self.findElement = self.chrome.findElement
        self.findElements = self.chrome.findElements
        self.findCells = self.chrome.findCells
        self.get = self.chrome.get
        self.execute_script = self.chrome.execute_script    
        self.terminate = self.chrome.terminate
        self.new_window = self.chrome.new_window
        self.switch_to_new_window = self.chrome.switch_to_new_window
        self.get_back_to_original_window = self.chrome.get_back_to_original_window
        self.close_window = self.chrome.close_window
        self.download = self.chrome.download

    def quit(self) -> None:
        """Ferme proprement Selenium et le processus Chrome associé."""
        self.chrome.terminate()
        self.proc.terminate()
        self.proc.wait()

    def waitFor(self, url: str, delay: int) -> str:
        ret = self.chrome.waitFor(url, delay)
        return ret
    
    # Méthodes qui doivent être implémentées dans une classe dérivée
    @abstractmethod
    def waitForCnxComptes(self) -> None:
        pass

    @abstractmethod
    def waitForRelevé(self) -> None:                        # Initialise le tableau self.rows avec la liste des opérations,
        pass
    
    @abstractmethod
    def getAcctNo(self) -> str:
        pass

    @abstractmethod
    def getSolde(self) -> float:
        pass

    @abstractmethod
    def getHTMLOpe(self, i: int) -> Ope:
        pass

