# main_LBP.py
import threading
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
        gui, gui_update =  self.context['core']['gui']
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
        root.after(100, gui_update, mygui, root)
        root.mainloop()

        nettoyage = self.context['appli'].get("nettoyage")
        if nettoyage: nettoyage()

    def test_presentation(self):
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
        """Lance l'application métier dans un thread."""
        self.context['appli']['putgui'] = self.putGUI
 
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
