# main_LBP.py
import threading
import pythoncom
import queue
import tkinter as tk
from tkinter import messagebox  
from typing import Any
import traceback
import ctypes


# Queues
gui_queue : queue.Queue[tuple[str, Any]]= queue.Queue()
metier_queue : queue.Queue[tuple[str, Any]]= queue.Queue()
mygui: Any = None   

class Monitor():   
    def __init__(self, context):
        self.context = context  

    def run(self):
        # Création de la fenêtre Tkinter avec lancement du thread Application métier
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 2 = Per Monitor DPI Aware
        root = tk.Tk()

        # Préparation du GUI
        gui =  self.context['core']['gui']
        gui_update = gui.update
        # instanciation du gui
        self.context['gui']['gui_root'] = root
        self.context['gui']['queues'] = gui_queue, metier_queue

        global mygui
        mygui = gui(self.context['gui'])
        
        # Lancement de l'application métier dans un thread
        self.context['appli']['queues'] = gui_queue, metier_queue
        self.test_presentation()
        t = threading.Thread(target=self.wrap_metier, daemon=True)
        t.start()

        # Affichage du GUI dans le Thread principal
        root.after(100, mygui.update)
        root.mainloop()

        nettoyage = self.context['appli'].get("nettoyage")
        if nettoyage: 
            nettoyage()

    def test_presentation(self):
        self.filter = None
        clsPresentation, pos_gui, pos_appli = \
            self.context['core'].get('presentation',[None, None, None]) 
        if clsPresentation:
            presentation = clsPresentation()
            if hasattr(presentation, 'filter'):
                self.filter = presentation.filter
            self.pos_appli = presentation.position(pos_appli)
            self.putGUI("position", presentation.position(pos_gui))

    
    def wrap_metier(self):
        """Code du thread de l'application métier (business logic thread)"""
        pythoncom.CoInitialize()
        
        self.context['appli']['putgui'] = self.putGUI
        self.context['appli']['getgui'] = self.getGUI
 
        appliMetier = self.context['core']['application']
        metier = appliMetier(self.context['appli'])

        try:
            metier.run()
        except Exception as err:
            fdump = 'O:\\ftrace.txt'
            with open(fdump, 'w') as dump:
                dump.write(traceback.format_exc())
            if hasattr(mygui, 'traiter_erreur'):
                self.putGUI("erreur", f"{err.__class__.__name__} : {err}")
                if hasattr(mygui, 'traiter_log'):
                    self.putGUI("log", "Fin anormale du programme")
            messagebox.showerror("Erreur", f"{err.__class__.__name__} : {err}\n\n"
                                 f"Consulter le fichier {fdump} pour plus de détails.")

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
