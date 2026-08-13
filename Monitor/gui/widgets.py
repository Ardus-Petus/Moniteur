import tkinter as tk
from tkinter import ttk
from typing import Literal
from Monitor.gui.guiBase import guiBase, font_bold, PINK, GREY

class MLFrame(tk.Frame):
    def __init__(self, parent: tk.Widget|tk.Tk, text: str, label_bg: str = GREY):
        super().__init__(parent, bd=3, relief="groove")
        self.label = tk.Label(self, text=text, bg=label_bg, font=font_bold())
        self.label.pack(fill="x")
        self.content = tk.Frame(self)
        self.content.pack(fill="both", expand=True)

# Journal
def Journal(parent: tk.Widget|tk.Tk, text:str="Journal d'exécution"):
    bloc_log = MLFrame(parent, text=text)
    log = tk.Text(bloc_log, height=10, wrap="word")#type: ignore
    log.pack(fill="x", padx=5, pady=5) # type: ignore
    return bloc_log, log

def Options(
    parent: tk.Widget|tk.Tk, 
    text:str, 
    options:list[tuple[str, str]], 
    default: int, 
    side:Literal['top', 'left', 'right', 'bottom'],
    command                     
):    
    bloc_options = MLFrame(parent, text=text)
    frame=tk.Frame(bloc_options.content)
    frame.pack(anchor='center')
    buttons= RadioButtons(parent=frame, text="Choisir un traitement", options=options, default=default, side=side)
    buttons.pack(side='left', padx=5, pady=5)
    # field1 = ttk.Entry(frame, style='MonMix.TEntry')
    # field1.pack(side='left', padx=5, pady=5)
    bouton_valid = tk.Button(frame, text='valider', font=font_bold(), bg=GREY, command=command)
    bouton_valid.pack(side='left', padx=5, pady=5)
    bouton_valid.config(state=tk.DISABLED)
    user_options_form = {                       
        'buttons': buttons,
        }
    return bloc_options, user_options_form, bouton_valid

def Champs(parent: tk.Widget|tk.Tk, text:str, champs:dict):    # Champs
    bloc_champs  = MLFrame(parent, text=text)
        
    frame_val = tk.Frame(bloc_champs.content)
    frame_val.pack(fill="none", padx=10, pady=10)

    nbcol = len(champs.keys())-2  # type: ignore
    r=0
    dict_champs:dict[str, tk.Entry] = {}        # dictionnaire des champs réutilisé dans gui_update
    for i, champ in enumerate(champs.keys()):          
        frame = tk.Frame(frame_val)

        label = tk.Label(frame, text=champ)
        label.pack(expand=False, side='left', fill='x', anchor='e', padx=5, pady=2)
    
        field = tk.Entry(frame, width=champs[champ])   # type: ignore
        field.pack(expand=True, side='left', fill='x', anchor='w', padx=5, pady=2)
        field.configure(justify='center')

        dict_champs[champ] = field       # type: ignore  # initialisation du dictionnaire dict_champs
        if i < nbcol:
            frame.grid(row=r, column=i, padx=5, pady=5)
        else:
            r += 1
            frame.grid(row=r, column=0, columnspan=nbcol, padx=5, pady=5, sticky='w')

    return bloc_champs, dict_champs

def Tableau(parent: tk.Widget|tk.Tk, text="Opérations détectées", columns=[], style: ttk.Style=None, scaling: float = 1.0):    # type: ignore # Tableau
    row_height = int(12 * scaling)   # type: ignore
    style.configure("MonStyle.Treeview", rowheight=row_height)
    bloc_tree = MLFrame(parent, text=text)

    tree = ttk.Treeview(           # type: ignore
        bloc_tree.content,
        height=5,
        columns=[name for name, *_ in columns],  # type: ignore
        show="headings",
        style="MonStyle.Treeview",
    )

    for name, text, _, min_width, stretch, anchor in columns   :  
        tree.heading(name, text=text)  
        tree.column(name, width=min_width, stretch=stretch, anchor=anchor) 

    tree.pack(fill="both", expand=True, anchor='n', padx=5, pady=5)   
    def resize_columns(event: tk.Event) -> None:
            width_total = tree.winfo_width() -20 
            for row in columns:        # type: ignore
                name, _, percent, min_width, _, _ = row
                tree.column(name, width=max(int(width_total * percent), min_width))    
    tree.bind("<Configure>", resize_columns)   
    return bloc_tree, tree    

class RadioButtons(tk.Frame):
    def __init__(
        self, 
        parent: tk.Widget|tk.Tk, 
        text: str, 
        options: list[tuple[str, str]], 
        default: int = 0, side:Literal['top', 'left', 'right', 'bottom'] = 'top'
    ):
        super().__init__(parent)
        self.label = tk.Label(self, text=text, font=font_bold())
        self.label.pack(side=side, fill="x")
        self.radio_frame = tk.Frame(self)
        self.radio_frame.pack(fill="both", expand=True)
        self.variable = tk.StringVar(value=options[default][1])  # Default to the first option's value
        for option_text, option_value in options:
            radio_button = tk.Radiobutton(self.radio_frame, text=option_text, variable=self.variable, value=option_value)
            radio_button.pack(side=side, anchor='w', padx=5, pady=2)
    def get(self) -> str:
        return self.variable.get()