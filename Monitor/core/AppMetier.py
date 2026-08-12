from abc import ABC, abstractmethod
class AppMetier(ABC):
    def __init__(self, context: dict):
        self.context = context
        self.putgui = context.get('putgui', None)
        self.getgui = context.get('getgui', None)

    @abstractmethod
    def run(self):
        pass