# application.py
import locale
import pythoncom
import traceback
from typing import Any

from Monitor.utils import winmgt

class Wrapper:
    """Wrapper de l'application métier"""

    def __init__(self, context:dict[str,Any]):
 
        self.context = context
        self.gui_queue, self.metier_queue = context['appli']['queues']
        self.presentation = None
        self.filter = None

    def run(self):
        pythoncom.CoInitialize()
        locale.setlocale(locale.LC_ALL, 'fr_FR')

        self.context['appli']['putgui'] = self.putGUI
        clsPresentation, pos_gui, pos_appli = \
            self.context['core'].get('presentation',[None, None, None]) 
        if clsPresentation:
            presentation = clsPresentation()
            if hasattr(presentation, 'filter'):
                self.filter = presentation.filter
            self.context['gui']['position']=presentation.position(pos_gui)
            self.context['appli']['position']=presentation.position(pos_appli)
            self.pos_appli = presentation.position(pos_appli)

        appliMetier = self.context['core']['application']
        metier = appliMetier(self.context['appli'])

        try:
            metier.run()
        except Exception as err:
            with open('.\\ftrace.txt', 'w') as dump:
                dump.write(traceback.format_exc())
            self.putGUI("log", "Fin anormale du programme")
            self.putGUI("Erreur", f"{err.__class__.__name__} : {err}")
        return True

    def putGUI(self, msg_type:str, payload:Any):
        if self.filter:
            if self.filter(msg_type, payload, self.pos_appli):
                return
            # réactions côté présentation
          
             # transmettre directement au GUI
        self.gui_queue.put((msg_type, payload))

 