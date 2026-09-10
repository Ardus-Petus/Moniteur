import threading
import traceback
import ctypes
import tkinter as tk
from tkinter import messagebox
from typing import Any
import sys
import queue
import pythoncom
from inspect import isclass
gui_queue = queue.Queue()
metier_queue = queue.Queue()
mygui = None
root = None

class Monitor:
    def __init__(self, context):
        self.context = context
        self.exc_info = None   # <--- Exception globale remontée ici

    # ------------------------------------------------------------------
    # Point d'entrée Monitor : capture globale
    # ------------------------------------------------------------------
    def run(self):
        try:
            self.runtask()

            # Si une exception a été remontée
            if self.exc_info:
                exc_type, exc, tb = self.exc_info
                raise exc.with_traceback(tb)

        except Exception as err:
            self.traiter_exception(err, err.__traceback__)

    # ------------------------------------------------------------------
    # Lancement du GUI + thread métier
    # ------------------------------------------------------------------
    def runtask(self):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        global root, mygui, gui_queue, metier_queue
        root = tk.Tk()

        gui_class = self.context['core']['gui']
        if not isclass(gui_class):
            raise TypeError("GUI not callable")
        
        self.context['gui']['gui_root'] = root
        self.context['gui']['queues'] = gui_queue, metier_queue


        # Surveillance des exceptions dans mygui.__init__
        try:
            mygui = gui_class(self.context['gui'])
        except Exception as err:
            self.exc_info = (err.__class__, err, err.__traceback__)
            return

        # Thread métier
        self.context['appli']['queues'] = gui_queue, metier_queue
        self.test_presentation()

        t = ThreadMetier(target=self.wrap_metier)
        t.start()

        root.after(50, self.surveiller_thread, t)
        root.after(100, self.safe_gui_update)

        root.mainloop()

        # Nettoyage
        nettoyage = self.context['appli'].get("nettoyage")
        if nettoyage and callable(nettoyage):
            nettoyage()

    # ------------------------------------------------------------------
    # Gestion centralisée des exceptions (appelée uniquement par run())
    # ------------------------------------------------------------------
    def traiter_exception(self, err, traceBack):
        global mygui, gui_queue
        fdump = 'O:\\ftrace.txt'
        message = f"{err.__class__.__name__} : {err}"

        with open(fdump, 'w') as dump:
            dump.write(''.join(traceback.format_tb(traceBack))+'\n')
            dump.write(message)

        if hasattr(mygui, 'traiter_erreur'):
            self.putGUI("erreur", message)
        if hasattr(mygui, 'traiter_log'):
            self.putGUI("log", "Fin anormale du programme")

        messagebox.showerror(
            "Erreur",
            message + '\n\n'
            f"Consulter le fichier {fdump} pour plus de détails."
        )

    # ------------------------------------------------------------------
    # Surveillance du thread métier
    # ------------------------------------------------------------------
    def surveiller_thread(self, t):
        global root
        if t.exc_info:
            self.exc_info = t.exc_info
            root.quit()   # <--- stoppe mainloop pour que runtask() sorte de mainloop et traite l'exception dans run()
            return

        if t.is_alive():
            root.after(50, self.surveiller_thread, t)

    def test_presentation(self):
        self.filter = None
        clsPresentation, pos_gui, pos_appli = \
            self.context['core'].get('presentation',[None, None, None]) 
       
        if clsPresentation:
            if not isclass(clsPresentation):
                raise TypeError("Presentation n\'est pas une classe")
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
        if not isclass(appliMetier):
            raise TypeError("Application n\'est pas une classe")
        metier = appliMetier(self.context['appli'])
        metier.run()
 
    # ------------------------------------------------------------------
    # Surveillance du GUI.update()
    # ------------------------------------------------------------------
    def safe_gui_update(self):
        global mygui, root
        try:
            mygui.update()
        except Exception as err:
            self.exc_info = (err.__class__, err, err.__traceback__)
            root.quit()   # <--- stoppe mainloop pour remonter dans run()
            return

        root.after(100, self.safe_gui_update)

    def putGUI(self, msg_type:str, payload:Any):
        global mygui, gui_queue, metier_queue
        if self.filter:
            if self.filter(msg_type, payload, self.pos_appli):
                return
        if msg_type[0] == '!' :
            if not hasattr(mygui,f'Entry_{msg_type[1:].replace(" " , "_")}'):
                raise AttributeError(f"Le message \"{msg_type}\" n'est pas associé à un Entry dans le GUI")
        else:
            if not hasattr(mygui, f'traiter_{msg_type}'):
                raise AttributeError(f"Le message \"{msg_type}\" n'a pas de méthode de traitement associée")
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

class ThreadMetier(threading.Thread):
    """Thread métier qui capture les exceptions pour les remonter au thread principal."""
    def __init__(self, target, *args, **kwargs):
        super().__init__(daemon=True)
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self.exc_info = None

    def run(self):
        try:
            self._target(*self._args, **self._kwargs)
        except Exception:
            self.exc_info = sys.exc_info()

class Context(dict):
    """Contexte centralisé pour transmettreles informations au GUI, au core et à l'application."""
    def __init__(self):
        self['gui']={}
        self['core']={}
        self['appli']={}
        self.gui=self['gui']
        self.core=self['core']
        self.appli=self['appli']

    def set_application(self, appli):
        self.core['application'] = appli

    def set_gui(self, gui):
         self.core['gui']=gui

    def set_presentation(self, pres, pos_gui, pos_appli):
        self.core['presentation']=(pres, pos_gui, pos_appli)

    def set_appli_param(self, key, value):
        self.appli[key]=value

    def set_gui_param(self, key, value):
        self.gui[key]=value
