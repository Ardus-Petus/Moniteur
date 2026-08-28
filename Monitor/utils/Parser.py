from selenium.webdriver.common.action_chains import ActionChains
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
            return None                         # type: ignore
        return res

    def getElements(self, ref:str, base=None)->list[WebElement]:   
        if base is None:
            base = self.driver
        try:
            res = base.find_elements(By.XPATH, ref)
        except:
            return []
        return res

    def getElementById(self, tag:str, id:str, base=None)->WebElement:
        rel = '' if base is None else '.'
        return self.getElement(f'{rel}//{tag}[@id="{id}"]', base)

    def getElementByClass(self, tag:str, cls:str, base=None)->WebElement:
        rel = '' if base is None else '.'
        return self.getElement(f'{rel}//{tag}[contains(@class, "{cls}")]', base)

    def Javascript_click(self, elem:WebElement):
        return self.driver.execute_script('arguments[0].click()', elem)

    def ActionClick(self, elem:WebElement):
        ActionChains(self.driver).move_to_element(elem).click().perform()

    def CDP_Click(self, elem:WebElement):
        rect = elem.rect
        self.driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {
                "type": "mousePressed",
                "x": rect["x"] + rect["width"] // 2,
                "y": rect["y"] + rect["height"] // 2,
                "button": "left",
                "clickCount": 1
            }
        )