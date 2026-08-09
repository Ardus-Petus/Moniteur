
from Monitor.core.chrome import webdriver, By, WebElement

class Parser:
    def __init__(self, driver):
        self.driver:webdriver.Chrome = driver

    def getElement(self, ref, base=None)->WebElement:   
        if base is None:
            base = self.driver
        try:
            res = base.find_element(By.XPATH, ref)
        except BaseException as e:
            return None # type: ignore
        return res

    def getElements(self, ref:str, base=None)->list[WebElement]:   
        if base is None:
            base = self.driver
        try:
            res = base.find_elements(By.XPATH, ref)
        except:
            return None # type: ignore
        return res

    def getElementById(self, tag:str, id:str, base=None)->WebElement:
        rel = '' if base is None else '.'
        return self.getElement(f'{rel}//{tag}[@id="{id}"]', base)

    def getElementByClass(self, tag:str, cls:str, base=None)->WebElement:
        rel = '' if base is None else '.'
        return self.getElement(f'{rel}//{tag}[contains(@class, "{cls}")]', base)