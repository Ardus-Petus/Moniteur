from playwright.sync_api import Locator, Page

# ============================================================
#  ILOCATORLIST : slicing, reverse, iteration
# ============================================================

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
#  ILOCATOR : indexable, sliceable, .text, len(), iteration
# ============================================================

class ILocator:
    """
    Wrapper autour d'un Locator Playwright.
    Ajoute __getitem__, slicing, __len__, __iter__, .text, etc.
    """

    def __init__(self, locator: Locator):
        self._loc = locator

    @property
    def text(self) -> str:
        return self._loc.inner_text()

    def click(self):
        self._loc.click()

    def __getitem__(self, index):
        if isinstance(index, slice):
            all_locators = self._loc.all()
            sliced = all_locators[index]
            return ILocatorList(sliced)
        return ILocator(self._loc.nth(index))

    def __len__(self):
        return self._loc.count()

    def __iter__(self):
        return (ILocator(l) for l in self._loc.all())

    def __getattr__(self, name):
        return getattr(self._loc, name)

    def __repr__(self):
        return f"ILocator({self._loc})"

    @property
    def inner_html(self):
        return self._loc.inner_html()

    @property
    def outer_html(self):
        return self._loc.outer_html()



# ============================================================
#  PAGEEX : retourne toujours des ILocator
# ============================================================

class PageEx:
    def __init__(self, page: Page):
        self._page = page

    def locator(self, selector: str, **kwargs) -> ILocator:
        loc = self._page.locator(selector, **kwargs)
        return ILocator(loc)

    def __getattr__(self, name):
        return getattr(self._page, name)

