import ctypes
import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
import queue
from Monitor.utils import winmgt

# ============================================================
# GUI
# ============================================================
PINK = "#FFAED0"
GREY = "#B5B5B5"

class MLFrame(tk.Frame):
    def __init__(self, parent: tk.Widget|tk.Tk, text: str, label_bg: str = GREY):
        super().__init__(parent, bd=3, relief="groove")
        fontBold = tkfont.nametofont('TkDefaultFont').copy()
        fontBold.configure(weight='bold')
        self.label = tk.Label(self, text=text, bg=label_bg, font=fontBold)
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
   
        scaling = float(root.tk.call('tk', 'scaling'))
        self.row_height = int(12 * scaling)   # 12 = hauteur "normale" de base
        #root.title("Extraction des opérations bancaires")
        root.title(__file__)
        icon_path = os.path.join(os.path.dirname(__file__), '_gui_.ico')
        root.iconbitmap(icon_path) #type: ignore
        W = root.winfo_screenwidth()
        #H = root.winfo_screenheight()
        self.ratio = W/1920
        root.geometry('1000x1000+500+500')
        fontBold = tkfont.nametofont('TkDefaultFont').copy()
        fontBold.configure(weight='bold')
        
        root.grid_rowconfigure(0, weight=0)  # Journal
        root.grid_rowconfigure(1, weight=1)  # Tableau -> prend le reste
        root.grid_rowconfigure(2, weight=0)  # Erreur
        root.grid_rowconfigure(3, weight=0)  # Boutons

        root.grid_columnconfigure(0, weight=1)
       
       # Journal
        bloc_log = MLFrame(root, text="Journal d'exécution")

        self.log = tk.Text(bloc_log, height=10, wrap="word")
        self.log.pack(fill="x", padx=5, pady=5)

        # Tableau
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("MonStyle.Treeview", rowheight=self.row_height)

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

        self.tree.pack(fill="both", expand=True, anchor='n', padx=10, pady=10)
        self.tree.bind("<Configure>", self.resize_columns)

        # Erreur
        bloc_erreur = MLFrame(root, "Message d'erreur")
        self.erreur = tk.Entry(bloc_erreur)
        self.erreur.pack(fill='both', expand=True)

        # Boutons
        bloc_buttons = tk.Frame(root)
        
        frame_buttons = tk.Frame(bloc_buttons)
        frame_buttons.pack(padx=10, pady=10)
 
        # bouton Fermeture
        self.btn_close = tk.Button(
            frame_buttons,
            width=20,   # largeur en caractères, pas en pixels
            text="Fermeture",
            state='normal',
            background=GREY,
            font=fontBold,
            command=self.close
        )
        self.btn_close.pack(side='left', padx=5, pady=5, anchor='center')

        # On place les différents blocs dans la fenêtre principale
        bloc_log.grid(      row=0, column=0, sticky="ew",   padx=10, pady=10)
        bloc_tree.grid(     row=1, column=0, sticky="nsew", padx=10, pady=10)
        bloc_erreur.grid(   row=2, column=0, sticky="ew",   padx=10, pady=10)
        bloc_buttons.grid(  row=3, column=0, sticky='ew',   padx=10, pady=10)

    def resize_columns(self, event: tk.Event) -> None:
        width_total = event.width
        for row in self.columns:
            name, _, percent, min_width, _, _ = row
            self.tree.column(name, width=max(int(width_total * percent), min_width))
    
    def close(self) -> None:
        self.root.destroy()

    # ============================================================
    # GUI update loop
    # ============================================================

    def update(self):
        if self.premier_appel:
            setpos = self.context.get('position')
            if setpos:
                setpos(ctypes.windll.user32.GetParent(root.winfo_id()))
            self.premier_appel = False
    
        def setEntry(field, value):
            field.delete(0, 'end')
            field.insert(0, value)
        try:
            while True:
                msg_type, payload = self.gui_queue.get_nowait()

                if msg_type == 'title':
                    root.title(payload)

                elif msg_type == "log":
                    self.log.insert("end", payload)
                    self.log.see("end")

                elif msg_type == "row":
                    self.tree.insert("", "end", values=payload) # payload est un tuple
                    self.tree.yview_moveto(1)  # On scroll vers le bas pour voir la dernière ligne ajoutée
                
                elif msg_type == 'Erreur':
                    setEntry(self.erreur, payload)
                    self.erreur.configure(background=PINK)
        except queue.Empty:
            pass
        self.root.after(100, self.update)

if __name__ == "__main__":
    context = {}
    root = tk.Tk()
    gui_queue = queue.Queue()
    context['queues'] = gui_queue, None
    context['gui_root'] = root
    mygui = gui(context)
    root.after(100, mygui.update)
    root.mainloop()
    