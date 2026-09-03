import tkinter as tk
from tkinter import ttk
import queue
from Monitor.gui.guiBase import guiBase, font_bold, PINK, GREY
from Monitor.gui.widgets import MLFrame, Journal, Tableau, Input

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
        champs = {
            "Date": 20,
            "N° compte": 20,
            "Excel": 20,
            "Nb ope": 10,
            "Dern. ": 98,
            "Erreur" :98
        }
        
        # Tableau
        tree_columns = [
            ('date',    'Date',     0.10, int(100*self.ratio),    False,  'w'),
            ('libelle', 'Libellé',  0.65, int(0),                 True,   'w'),
            ('montant', 'Montant',  0.15, int(150*self.ratio),    False,  'e'),
        ]

        options_options = [
            ('Prélèvements', "prelevements"),
            ('Déclarations', "declarations"),
        ]
        #------------------------------------------------
        # Erreur
        #------------------------------------------------
        bloc_erreur = MLFrame(root, "Message d'erreur")
        self.erreur = ttk.Entry(bloc_erreur)
        self.erreur.pack(fill='x', expand=True, padx=2, pady=2)
        #------------------------------------------------
        # Boutons
        #------------------------------------------------
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
        bloc_options, self.user_options_form, self.bouton_valid = \
            Input(parent=root, text="Options", options=options_options, default=0, side='left', command=lambda:self.parse(None))
        bloc_tree, self.tree = \
            Tableau(parent=root, text="Opérations détectées", columns=tree_columns)
        # bloc_champs, self.dict_champs = \
        #     Champs(parent=root, text="Champs", champs=champs)
        
        # On place les différents blocs dans la fenêtre principale
        bloc_journal.pack(fill="x", padx=5, pady=5)
        bloc_options.pack(fill="x", padx=5, pady=5)        # bloc_champs.pack(fill="x", padx=5, pady=5)
        bloc_tree.pack(fill="both", expand=True, padx=5, pady=5)
        bloc_erreur.pack(fill="x", padx=5, pady=5)  
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
        self.bouton_valid.config(state=tk.DISABLED)
        self.changer_background('white')

    def changer_background(self, color):
        # On force des bordures sombres pour simuler un relief solid/sunken
        self.style.configure('MonMix.TEntry', fieldbackground=color )
        self.style.configure('MonMix.TCombobox', fieldbackground=color)

#
# Procedures de traitement des commandes reçues par update
# ========================================================
    def traiter_input(self, msg_type, payload):
        form = {
            'form': self.user_options_form
        }[payload]
        for _field in form.values():
            _field.configure(background='lightgrey')
        self.bouton_valid.config(state=tk.NORMAL)
        self.changer_background('lightgrey')
        self.responseform = form 

    def traiter_log(self, msg_type, payload):
        self.log.insert("end", payload)
        self.log.see("end")

    def traiter_title(self, msg_type, payload):
        self.root.title(payload)

    def traiter_Erreur(self, msg_type, payload):
        self.erreur.delete(0, 'end')
        self.erreur.insert(0, payload)
        self.erreur.configure(background=PINK)

    def traiter_row(self, msg_type, payload):
        self.tree.insert("", "end", values=payload) # payload est un tuple
        self.tree.yview_moveto(1)  # On scroll vers le bas pour voir la dernière ligne ajoutée

    # def traiter_champ(self, msg_type, payload):
    #     entry = self.dict_champs.get(msg_type)
    #     if entry is not None:
    #         entry.delete(0, 'end')
    #         entry.insert(0, payload)
    #         if msg_type == "Erreur":
    #             entry.configure(background=PINK)

    def traiter_label(self, msg_type, payload):
        self.bloc_label.label.configure(text=payload)
        self.bloc_label.label.update_idletasks()  # Force la mise à jour immédiate de l'affichage        

if __name__ == "__main__":
    context = {}
    root = tk.Tk()
    gui_queue = queue.Queue()
    context['queues'] = gui_queue, None
    context['gui_root'] = root
    mygui = gui(context)
    root.after(100, mygui.update)
    root.mainloop()
    