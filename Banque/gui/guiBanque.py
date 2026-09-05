import tkinter as tk
from tkinter import ttk
import queue
from Monitor.gui.guiBase import guiBase, GREY, PINK, font_bold
from Monitor.gui.widgets import Journal, Champs, Tableau

# ============================================================
# GUI
# ============================================================

class gui(guiBase):
    def __init__(self, context):
        super().__init__(context)
        root = self.root
        root.geometry('700x700+50+50')
        self.style.theme_use("clam")
 
        # champs
        champs_affichage = {
            "Date": 20,
            "N° compte": 20,
            "Excel": 20,
            "Nb ope": 10,
            "Dernière": 98,
            "Erreur" :98
        }
        
        # Tableau
        tree_columns = [
            ('statut',  'Statut',   0.07, int(70*self.ratio),     False,  'w'),
            ('date',    'Date',     0.10, int(100*self.ratio),    False,  'w'),
            ('libelle', 'Libellé',  0.65, int(0),                 True,   'w'),
            ('montant', 'Montant',  0.12, int(150*self.ratio),    False,  'e'),
        ]

        # # Erreur
        # bloc_erreur = MLFrame(root, "Message d'erreur")
        # self.erreur = ttk.Entry(bloc_erreur)
        # self.erreur.pack(fill='x', expand=True, padx=2, pady=2)

        # Boutons
        bloc_buttons = tk.Frame(root)
        
        frame_buttons = tk.Frame(bloc_buttons)
        frame_buttons.pack()
 
        # bouton Fermeture
        self.btn_close = tk.Button(
            frame_buttons,
            width=10,   # largeur en caractères, pas en pixels
            text="Fermeture",
            state='normal',
            background=GREY,
            font=font_bold(),
            command=self.close
        )
        self.btn_close.pack(side='left', padx=5, pady=5, anchor='center')
        #-----------------------------------------------------------------------
        # Création des autres blocs et mise en place dans la fenêtre principale
        #-----------------------------------------------------------------------
        bloc_journal, self.log = \
            Journal(parent=root, text="Journal d'exécution")
        # bloc_input, self.user_input_form, self.bouton_valid = \
        #     Options(parent=root, text="Options", options=input_options, default=0, side='left')
        bloc_tree, self.tree = \
            Tableau(parent=root, text="Opérations détectées", columns=tree_columns)
        bloc_champs = \
            Champs(base=self, parent=root, text="Champs", champs=champs_affichage)
        
        # On place les différents blocs dans la fenêtre principale
        bloc_journal.pack(fill="x", padx=5, pady=5)
        #bloc_input.pack(fill="x", padx=5, pady=5)
        bloc_champs.pack(fill="x", padx=5, pady=5)
        bloc_tree.pack(fill="both", expand=True, padx=5, pady=5)
        #bloc_erreur.pack(fill="x", padx=5, pady=5)  
        bloc_buttons.pack(fill="x", padx=5, pady=5)
            

#---------------------
# Méthodes utilitaires
# --------------------
#         
     
    def close(self) -> None:
        self.root.destroy()

    def parse(self, event):
        if self.responseform is None: return
        form_new = {}
        for key in self.responseform: # type: ignore
            self.responseform[key].configure(background='white')
            form_new[key] = self.responseform[key].get()
        self.metier_queue.put(('form', form_new))
        self.responseform = None
        self.bouton_valid.config(state=tk.DISABLED) # type: ignore
        self.changer_background('white')

    def changer_background(self, color):
        # On force des bordures sombres pour simuler un relief solid/sunken
        self.style.configure('MonMix.TEntry', fieldbackground=color )
        self.style.configure('MonMix.TCombobox', fieldbackground=color)

#
# Procedures de traitement des commandes reçues par update
# ========================================================
    # def traiter_input(self, msg_type, payload):
    #     form = {
    #         'form': self.user_input_form # pyright: ignore[reportAttributeAccessIssue]
    #     }[payload]
    #     for _field in form.values():
    #         _field.configure(background='lightgrey')
    #     self.bouton_valid.config(state=tk.NORMAL)# type: ignore
    #     self.changer_background('lightgrey')
    #     self.responseform = form 

    def traiter_log(self, msg_type, payload):
        self.log.insert("end", payload)# type: ignore
        self.log.see("end") # type: ignore
    
    def traiter_title(self, msg_type, payload):
        self.root.title(payload)

    def traiter_Erreur(self, msg_type, payload):
        self.traiter_champ('Erreur', payload)

    # def traiter_erreur(self, msg_type, payload):
    #     self.erreur.delete(0, 'end')    # type: ignore
    #     self.erreur.insert(0, payload)    # type: ignore
    #     self.erreur.configure(background=PINK)    # type: ignore

    def traiter_row(self, msg_type, payload):
        self.tree.insert("", "end", values=payload) # payload est un tuple # type: ignore
        self.tree.yview_moveto(1)  # On scroll vers le bas pour voir la dernière ligne ajoutée # type: ignore

if __name__ == "__main__":
    context = {}
    root = tk.Tk()
    gui_queue = queue.Queue()
    context['queues'] = gui_queue, None
    context['gui_root'] = root
    mygui = gui(context)
    root.after(100, mygui.update)
    root.mainloop()
    