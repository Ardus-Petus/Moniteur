import os
from selenium.webdriver.remote.webelement import WebElement

import Monitor.core.chrome as chrome
from Banque.core.Ope import Ope
from abc import ABC, abstractmethod

os.environ['WDM_LOCAL'] = '0'
os.environ['WDM_SSL_VERIFY'] = '0'

class HTML(ABC):
    def __init__(self, url:str=''):
        self.rows: list[WebElement] = []    # Liste des lignes du tableau HTML
        self.chrome = chrome.ChromeDriver(url)
        self.proc = self.chrome.proc
        self.hwnd = self.chrome.hwnd
                    
    def quit(self) -> None:
        """Ferme proprement Selenium et le processus Chrome associé."""
        #self.driver.quit()
        self.proc.terminate()
        self.proc.wait()

    def waitFor(self, url:str, delay:int=10) -> None:
        """Attends que l'URL du navigateur corresponde à l'URL spécifiée."""
        self.chrome.waitFor(url, delay)

    def findElement(self, value: str) -> WebElement:
        return self.chrome.findElement(value)

    def findElements(self, value: str) -> list[WebElement]:
        return self.chrome.findElements(value)

    def findCells(self, row: WebElement) -> list[WebElement]:
        return self.chrome.findCells(row)
    
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

