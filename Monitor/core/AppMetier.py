from abc import ABC, abstractmethod
from typing import Callable, Any

class AppMetier(ABC):
    def __init__(self, context: dict):
        self.context:dict = context
        self.putgui: Callable[[str, Any], None] = context['putgui']
        self.getgui: Callable[[str, Any, int], Any] = context['getgui']

    @abstractmethod
    def run(self):
        pass