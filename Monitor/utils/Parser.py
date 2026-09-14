
# from Monitor.core.chrome import webdriver, By, WebElement

class Parser:
    def __init__(self, chrome):
        self.chrome = chrome

    def getElement(self, selector, base=None):
        return self.chrome.findElement(selector, base)

    def getElements(self, selector:str, base=None):
        return self.chrome.findElements(selector, base)

    def getElementById(self, tag:str, id:str, base=None):
        rel = '' if base is None else '.'
        return self.chrome.findElement(f'{rel}//{tag}[@id="{id}"]', base)

    def getElementByClass(self, tag:str, cls:str, base=None):
        rel = '' if base is None else '.'
        return self.chrome.findElement(f'{rel}//{tag}[contains(@class, "{cls}")]', base)