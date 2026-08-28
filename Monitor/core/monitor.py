# main_LBP.py
import threading
import pythoncom
import queue
import tkinter as tk
from typing import Any
import traceback
# Queues
gui_queue : queue.Queue[tuple[str, Any]]= queue.Queue()
metier_queue : queue.Queue[tuple[str, Any]]= queue.Queue()

class Monitor():   
    def __init__(self, context):
        self.context = context

    def run(self):
        # Création de la fenêtre Tkinter
        root = tk.Tk()

        # Préparation du GUI
        gui =  self.context['core']['gui']
        gui_update = gui.update
        # instanciation du gui
        self.context['gui']['gui_root'] = root
        self.context['gui']['queues'] = gui_queue, metier_queue
      
        mygui = gui(self.context['gui'])
        
        # Lancement de l'application dans un thread
        self.context['appli']['queues'] = gui_queue, metier_queue
        self.test_presentation()
        t = threading.Thread(target=self.wrap_metier, daemon=True)
        t.start()

        # Affichage du GUI dans le Thread principal
        root.after(100, mygui.update)
        root.mainloop()

        nettoyage = self.context['appli'].get("nettoyage")
        if nettoyage: nettoyage()

    def test_presentation(self):
        self.filter = None
        clsPresentation, pos_gui, pos_appli = \
            self.context['core'].get('presentation',[None, None, None]) 
        if clsPresentation:
            presentation = clsPresentation()
            if hasattr(presentation, 'filter'):
                self.filter = presentation.filter
            self.context['gui']['position']=presentation.position(pos_gui)
            self.context['appli']['position']=presentation.position(pos_appli)
            self.pos_appli = presentation.position(pos_appli)

    def wrap_metier(self):
        pythoncom.CoInitialize()
        
        """Lance l'application métier dans un thread."""
        self.context['appli']['putgui'] = self.putGUI
        self.context['appli']['getgui'] = self.getGUI
 
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
        gui_queue.put((msg_type, payload))

    def getGUI(self, msg_type, payload, timeout=60):
        self.putGUI(msg_type, payload)
        try:
            _, reponse = metier_queue.get(True,timeout=timeout)
        except queue.Empty:
            raise TimeoutError(f"Timeout sur saisie {payload}")
        return reponse

class Context(dict):
    def __init__(self):
        self['gui']={}
        self['core']={}
        self['appli']={}
        self.gui=self['gui']
        self.core=self['core']
        self.appli=self['appli']

    def set_application(self, appli):
        if not callable(appli):
            raise TypeError("Application not callable")
        self.core['application'] = appli

    def set_gui(self, gui):
        self.core['gui']=gui

    def set_presentation(self, pres, pos_gui, pos_appli):
        self.core['presentation']=(pres, pos_gui, pos_appli)

    def set_appli_param(self, key, value):
        self.appli[key]=value

    def set_gui_param(self, key, value):
        self.gui[key]=value
