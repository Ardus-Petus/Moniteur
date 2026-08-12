import tkinter as tk
from tkinter import ttk
from Monitor.gui.guiBase import guiBase, font_bold, PINK, GREY

class MLFrame(tk.Frame):
    def __init__(self, parent: tk.Widget|tk.Tk, text: str, label_bg: str = GREY):
        super().__init__(parent, bd=3, relief="groove")
        self.label = tk.Label(self, text=text, bg=label_bg, font=font_bold())
        self.label.pack(fill="x")
        self.content = tk.Frame(self)
        self.content.pack(fill="both", expand=True)

# Journal
def Journal(parent: tk.Widget|tk.Tk, base:object, text:str="Journal d'exécution"):
    bloc_log = MLFrame(parent, text=text)
    base.log = tk.Text(bloc_log, height=10, wrap="word")#type: ignore
    base.log.pack(fill="x", padx=5, pady=5) # type: ignore
    return bloc_log

def Input(parent: tk.Widget|tk.Tk, base:object):    # Input
    bloc_input = MLFrame(parent, text="Zones de saisie")
    frame=tk.Frame(bloc_input.content)
    frame.pack(anchor='center')
    combo = ttk.Combobox(frame, values=['declarations', 'prelevements'], style='MonMix.TCombobox')
    combo.pack(side='left', padx=5, pady=5)
    combo.set('Choisir un traitement...')
    # field1 = ttk.Entry(frame, style='MonMix.TEntry')
    # field1.pack(side='left', padx=5, pady=5)
    base.bouton_valid = tk.Button(frame, text='valider', font=font_bold(), bg=GREY, command=lambda : base.parse(None)) #type: ignore
    base.bouton_valid.pack(side='left', padx=5, pady=5) #type: ignore
    base.bouton_valid.config(state=tk.DISABLED)     #type: ignore
    base.user_input_form = {                        #type: ignore
        'combo': combo,
        }
    return bloc_input

def Champs(parent: tk.Widget|tk.Tk, base:object):    # Champs
    bloc_champs  = MLFrame(parent, text="Résultats")
        
    frame_val = tk.Frame(bloc_champs.content)
    frame_val.pack(fill="none", padx=10, pady=10)

    nbcol = len(base.champs)-2  # type: ignore
    r=0
    base.dict_champs:dict[str, tk.Entry] = {}        # type: ignore  # dictionnaire des champs réutilisé dans gui_update
    for i, champ in enumerate(base.champs):          # type: ignore
        frame = tk.Frame(frame_val)

        label = tk.Label(frame, text=champ)
        label.pack(expand=False, side='left', fill='x', anchor='e', padx=5, pady=2)
    
        field = tk.Entry(frame, width=base.champs[champ])   # type: ignore
        field.pack(expand=True, side='left', fill='x', anchor='w', padx=5, pady=2)
        field.configure(justify='center')

        base.dict_champs[champ] = field       # type: ignore  # initialisation du dictionnaire dict_champs
        if i < nbcol:
            frame.grid(row=r, column=i, padx=5, pady=5)
        else:
            r += 1
            frame.grid(row=r, column=0, columnspan=nbcol, padx=5, pady=5, sticky='w')

    return bloc_champs

def Tableau(parent: tk.Widget|tk.Tk, base:object):    # Tableau
    row_height = int(12 * base.scaling)   # type: ignore
    base.style.configure("MonStyle.Treeview", rowheight=row_height)# type: ignore

    bloc_tree = MLFrame(parent, text="Opérations détectées")
    

    base.tree = ttk.Treeview(           # type: ignore
        bloc_tree.content,
        height=5,
        columns=[name for name, *_ in base.columns],  # type: ignore
        show="headings",
        style="MonStyle.Treeview",
    )

    for name, text, _, min_width, stretch, anchor in base.columns   :  # type: ignore
        base.tree.heading(name, text=text)  # type: ignore
        base.tree.column(name, width=min_width, stretch=stretch, anchor=anchor) # type: ignore

    base.tree.pack(fill="both", expand=True, anchor='n', padx=5, pady=5)    # type: ignore
    def resize_columns(event: tk.Event) -> None:
            width_total = base.tree.winfo_width() -20 # type: ignore
            for row in base.columns:        # type: ignore
                name, _, percent, min_width, _, _ = row
                base.tree.column(name, width=max(int(width_total * percent), min_width))    # type: ignore
    base.tree.bind("<Configure>", resize_columns)   # type: ignore
    return bloc_tree    