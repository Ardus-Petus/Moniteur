import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
import queue

# ============================================================
# GUI
# ============================================================
PINK = "#FFAED0"
GREY = "#B5B5B5"

class MLFrame(tk.Frame):
    def __init__(self, parent: tk.Widget|tk.Tk, text: str, label_bg: str = GREY):
        super().__init__(parent, bd=3, relief="groove")
        bold_font = tkfont.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight="bold")
        self.label = tk.Label(self, text=text, bg=label_bg, font=bold_font)
        self.label.pack(fill="x")
        self.content = tk.Frame(self)
        self.content.pack(fill="both", expand=True)

class gui:
    def __init__(self, context):
        self.context = context
        root=context['gui_root']
        self.root = root
        self.gui_queue, self.metier_queue = context["queues"]

        self.premier_appel = True           # Flag pour gui_updater
        self.responseform=None
        bold_font = tkfont.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight="bold")

        scaling = float(root.tk.call('tk', 'scaling'))
        self.row_height = int(12 * scaling)   # 12 = hauteur "normale" de base
        root.title(__file__)
        icon_path = os.path.join(os.path.dirname(__file__), '_gui_.ico')
        root.iconbitmap(icon_path) #type: ignore
        W = root.winfo_screenwidth()
        H = root.winfo_screenheight()
        root.bind('<Return>', self.parse)
        root.bind('<Tab>', self.parse)
        self.ratio = W/1920
        root.geometry('700x700+50+50')
        root.grid_rowconfigure(0, weight=0)  # Journal
        root.grid_rowconfigure(1, weight=0)  # Input
        root.grid_rowconfigure(2, weight=1)  # Tableau -> prend le reste
        root.grid_rowconfigure(3, weight=0)  # Erreur
        root.grid_rowconfigure(4, weight=0)  # Boutons

        root.grid_columnconfigure(0, weight=1)

        self.style = ttk.Style()
        self.style.theme_use("clam")


        # 2. Définition des styles initiaux (ici en relief plat)
        self.style.configure('MonMix.TEntry', relief='flat', borderwidth=3, padding=3)
        self.style.configure('MonMix.TCombobox', relief='flat', borderwidth=3, padding=3)     

        # Fonction pour changer dynamiquement le relief des deux widgets simultanément

        # Journal
        bloc_log = MLFrame(root, text="Journal d'exécution")

        self.log = tk.Text(bloc_log, height=10, wrap="word")
        self.log.pack(fill="x", padx=5, pady=5)

        # Input
        bloc_input = MLFrame(root, text="Zones de saisie")
        frame=tk.Frame(bloc_input.content)
        frame.pack(anchor='center')
        combo = ttk.Combobox(frame, values=['declarations', 'prelevements'], style='MonMix.TCombobox')
        combo.pack(side='left', padx=5, pady=5)
        combo.set('Choisir un traitement...')
        field1 = ttk.Entry(frame, style='MonMix.TEntry')
        field1.pack(side='left', padx=5, pady=5)
        self.valid = tk.Button(frame, text='valider', font=bold_font, bg=GREY, command=self.parse_)
        self.valid.pack(side='left', padx=5, pady=5)
        self.valid.config(state=tk.DISABLED)
        self.user_input_form = {
            'combo': combo,
         }

        # Tableau
        self.style.configure("MonStyle.Treeview", rowheight=self.row_height)

        bloc_tree = MLFrame(root, text="Opérations détectées")
     
        self.columns = [
            ('date',    'Date',     0.10, int(150*self.ratio),    False,  'w'),
            ('libelle', 'Libellé',  0.65, int(0),                 True,   'w'),
            ('montant', 'Montant',  0.15, int(150*self.ratio),    False,  'e'),
        ]

        self.tree = ttk.Treeview(
            bloc_tree.content,
            columns=[name for name, *_ in self.columns],
            show="headings",
            style="MonStyle.Treeview",
        )

        for name, text, _, min_width, stretch, anchor in self.columns:
            self.tree.heading(name, text=text)
            self.tree.column(name, width=min_width, stretch=stretch, anchor=anchor) # pyright: ignore[reportArgumentType]

        self.tree.pack(fill="both", expand=True, anchor='n', padx=5, pady=5)
        self.tree.bind("<Configure>", self.resize_columns)

        # Erreur
        bloc_erreur = MLFrame(root, "Message d'erreur")
        self.erreur = tk.Entry(bloc_erreur)
        self.erreur.pack(fill='both', expand=True, padx=5, pady=5)

        # Boutons
        bloc_buttons = tk.Frame(root)
        
        frame_buttons = tk.Frame(bloc_buttons)
        frame_buttons.pack(padx=5, pady=5)
 
        # bouton Fermeture
        self.btn_close = tk.Button(
            frame_buttons,
            width=10,   # largeur en caractères, pas en pixels
            text="Fermeture",
            state='normal',
            background=GREY,
            font=bold_font,
            command=self.close
        )
        self.btn_close.pack(side='left', padx=5, pady=5, anchor='center')

        # On place les différents blocs dans la fenêtre principale
        bloc_log.grid(      row=0, column=0, sticky="ew",   padx=5, pady=5)
        bloc_input.grid(    row=1, column=0, sticky="ew",   padx=5, pady=5)
        bloc_tree.grid(     row=2, column=0, sticky="nsew", padx=5, pady=5)
        bloc_erreur.grid(   row=3, column=0, sticky="ew",   padx=5, pady=5)
        bloc_buttons.grid(  row=4, column=0, sticky='ew',   padx=5, pady=5)

    def resize_columns(self, event: tk.Event) -> None:
        width_total = event.width
        for row in self.columns:
            name, _, percent, min_width, _, _ = row
            self.tree.column(name, width=max(int(width_total * percent), min_width))
    
    def close(self) -> None:
        self.root.destroy()

    def parse_(self):
        self.parse(None)

    def parse(self, event):
        if self.responseform is None: return
        form_new = {}
        for key in self.responseform: # type: ignore
            self.responseform[key].configure(background='white')
            form_new[key] = self.responseform[key].get()
        self.metier_queue.put(('form', form_new))
        self.responseform = None
        self.valid.config(state=tk.DISABLED)
        self.changer_dynamique('flat')

    def changer_dynamique(self, relief_type):
        if relief_type == 'solid':
            # On force des bordures sombres pour simuler un relief solid/sunken
            self.style.configure('MonMix.TEntry', fieldbackground=PINK, lightcolor='black', darkcolor='black', borderwidth=2)
            self.style.configure('MonMix.TCombobox', fieldbackground=PINK, lightcolor='black', darkcolor='black', borderwidth=2)
        else:
            # On efface les bordures pour simuler un relief flat
            self.style.configure('MonMix.TEntry', fieldbackground='white', lightcolor='white', darkcolor='white', borderwidth=0)
            self.style.configure('MonMix.TCombobox', fieldbackground='white', lightcolor='white', darkcolor='white', borderwidth=0)

# ============================================================
# GUI update loop
# ============================================================
import ctypes
def gui_update(_gui: gui, root: tk.Tk):
    if _gui.premier_appel:
        setpos = _gui.context.get('position')
        if setpos:
            setpos(ctypes.windll.user32.GetParent(root.winfo_id()))
    _gui.premier_appel = False
 
    def setEntry(field, value):
        field.delete(0, 'end')
        field.insert(0, value)
    try:
        while True:
            msg_type, payload = _gui.gui_queue.get_nowait()

            if msg_type == 'input':
                form = {
                    'form': _gui.user_input_form
                }[payload]
                for _field in form.values():
                    _field.configure(background='lightgrey')
                _gui.valid.config(state=tk.NORMAL)
                _gui.changer_dynamique('solid')

                _gui.responseform = form # pyright: ignore[reportAttributeAccessIssue]
            
            elif msg_type == 'title':
                 root.title(payload)

            elif msg_type == "log":
                _gui.log.insert("end", payload)
                _gui.log.see("end")

            elif msg_type == "row":
                _gui.tree.insert("", "end", values=payload) # payload est un tuple
                _gui.tree.yview_moveto(1)  # On scroll vers le bas pour voir la dernière ligne ajoutée
            
            elif msg_type == 'Erreur':
                setEntry(_gui.erreur, payload)
                _gui.erreur.configure(background=PINK)
    except queue.Empty:
        pass
    root.after(100, gui_update, _gui, root)

if __name__ == "__main__":
    context = {}
    root = tk.Tk()
    gui_queue = queue.Queue()
    context['queues'] = gui_queue, None
    context['gui_root'] = root
    mygui = gui(context)
    root.after(100, gui_update, mygui, root)
    root.mainloop()
    