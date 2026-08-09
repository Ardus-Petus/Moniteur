# main_LBP.py
import threading
import queue
import tkinter as tk
from typing import Any
from Monitor.core.wrapper import Wrapper           # Application

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
        t = threading.Thread(target=self.lancer_metier, daemon=True)
        t.start()

        # Affichage du GUI dans le Thread principal
        root.after(100, gui_update, mygui, root)
        root.mainloop()

        nettoyage = self.context['appli'].get("nettoyage")
        if nettoyage: nettoyage()

    def lancer_metier(self):
        """Lance l'application métier dans un thread."""
        wrap = Wrapper(self.context)
        wrap.run()
