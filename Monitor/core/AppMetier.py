from abc import ABC, abstractmethod
from typing import Callable

class AppMetier(ABC):
    def __init__(self, context: dict):
        self.context:dict = context
        self.putgui: Callable = context.get('putgui', None) #type: ignore
        self.getgui: Callable = context.get('getgui', None) #type: ignore

    @abstractmethod
    def run(self):
        pass