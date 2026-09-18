import json
import win32com.client as win32  # installé par pip install pywin32
from Monitor.utils import winmgt
import os.path
from Monitor.utils.ExcelWindowManager import ExcelWindowManager
from Banque.core.Ope import Ope
from abc import ABC, abstractmethod
from decimal import Decimal
import re
class TablibError(Exception):
    pass


class Excel(ABC):
    """Classe pour gérer les opérations bancaires dans un fichier Excel."""
     
    EXIST, OPEN, NEW = range(3)

    def __init__(self, acct:str, rep:str='', worksheetname:str='', modelpath:str=''):
        self.Appli: win32.CDispatch | None = None   # L'application Excel
        self.WorkBook: win32.CDispatch | None = None      # Le classeur Excel
        self.WorkSheet: win32.CDispatch | None = None      # La feuille de calcul Excel

        match = re.search(r"(.*) N° (\S+) (.*)", acct)
        type_compte, numero, titulaire = match.groups()

        WorkBookname = titulaire + '.xlsx'             # Nom du classeur Excel pour le compte
        self.nomfic = rep + WorkBookname          # Chemin complet du fichier Excel pour le compte
 
        self.mgr = ExcelWindowManager()     # Active ou crée une instance d'Excel
        winmgt.focus(self.mgr.get_hwnd())       # Essentiel: SetForegroundWindow effectué par focus

        self.Appli = self.mgr.appli           # On récupère l'instance Excel 
                
        self.Appli.Visible = True
        self.Appli.FeatureInstall = 0  # Empêche Excel de chercher des fonctionnalités manquantes sur le réseau     
        #self.Appli.WindowState = -4140      # xlMinimized

        # On récupère la liste des classeurs ouverts 
        # et on vérifie si le classeur pour le compte existe déjà
        WorkBooks = self.Appli.Workbooks
        openWorkBooks= [w.Name for w in WorkBooks]
        if WorkBookname in openWorkBooks:
            self.WorkBook = WorkBooks[WorkBookname]
            self.status = Excel.EXIST
        else:
            if os.path.exists(self.nomfic):
                self.WorkBook = self.Appli.Workbooks.Open(self.nomfic) 
                #focus(self.WorkBook.Windows[0].Hwnd)   #Ouvre le classeur existant
                self.status = Excel.OPEN
            else:
                self.WorkBook = self.Appli.Workbooks.Add(modelpath)  # Crée un nouveau classeur à partir du modèle
                self.WorkBook.SaveAs(self.nomfic)  # Enregistre le nouveau classeur sous le nom de fichier spécifié
                self.status = Excel.NEW
        assert self.WorkBook is not None
        self.hwnd = self.Appli.Hwnd

        # On récupère la feuille de calcul du classeur
        sheets= self.WorkBook.Worksheets
        wsModèle = self.WorkBook.Worksheets(worksheetname)
        for ws in self.WorkBook.Worksheets:
            if ws.Name == type_compte:
                self.WorkSheet = ws
                self.newAccount = False
                break
        else:
            wsModèle.Copy(After=self.WorkBook.Worksheets(sheets.Count))
            self.Appli.ActiveSheet.Name = type_compte
            self.WorkSheet = self.Appli.ActiveSheet
            lo = self.WorkSheet.ListObjects.Add(
                SourceType=1,  # xlSrcRange
                Source= self.WorkSheet.UsedRange,
                XlListObjectHasHeaders=True  # Plage de données actuelle
            )
            lo.Name = type_compte  # Renomme le tableau de la nouvelle feuille
            self.newAccount = True  

        self.WorkSheet.Activate()  # Active la feuille de calcul pour la rendre visible


        # Si le tableau est filtré, on affiche toutes les données 
        # pour éviter les problèmes d'ajout de ligne
        assert self.WorkSheet is not None
        if (self.WorkSheet.AutoFilterMode and self.WorkSheet.FilterMode) or self.WorkSheet.FilterMode : 
            self.WorkSheet.ShowAllData()
        
        # On récupère la liste des lignes de la feuille de calcul Excel
        self.listRows = self.getlistRows()  # Traité par HTML_LBP

        # On charge le fichier tablib pour le compte
        try:
            with open(rep + numero + '.tablib', mode='r') as file:
                self.tablib = json.loads(file.read())
        except FileNotFoundError:
            self.tablib: list[list[str]]= []

        
        # Finalement, on retourne l'objet Excel initialisé
        # 
        # 
        self.Appli.Visible = True
        # self.Appli.DisplayAlerts = True
        self.Appli.WindowState = -4143  # xlNormal


    def setVisible(self, state:bool):
        self.Appli.Visible = state

    #---------------------------------------------------------
    # Méthodes pour gérer les opérations dans le fichier Excel
    #---------------------------------------------------------

    def getLastRow(self) -> int:
        """Retourne le numéro de la dernière ligne utilisée dans la feuille de calcul Excel."""
        return self.listRows.Count

    def setVisibleRow(self, delta_row:int) -> None :
        """Se positionne sur la ligne delta_row° par rapport à la dernière ligne utilisée 
        pour assurer la visibilité de la ligne dans la fenêtre Excel.
        Args:
            delta_row (int): Le décalage (positif ou négatif)par rapport à la dernière ligne utilisée."""
        row = max(self.getLastRow()+delta_row, 1)
        self.Appli.Goto(self.WorkSheet.Cells(row, 1)) #type: ignore # Se positionne sur la ligne pour la rendre visible 

    def getStatus(self) -> int:
        """Retourne le statut du classeur Excel selon que le fichier était déjà ouvert, ouvert, ou nouveau."""
        return self.status

    def getStatusString(self) -> str:
        """Retourne une chaîne de caractères représentant le statut du classeur Excel."""
        return ["DEJA OUVERT", "OUVERTURE", "NOUVEAU"][self.status] 
    
    def saveWorkBook(self) -> None:
        """Enregistre le classeur Excel selon son statut."""                        
        if self.status == Excel.NEW:
            self.WorkBook.SaveAs(self.nomfic) #type: ignore
        else:
            self.WorkBook.Save() #type: ignore
        
    def getRow(self, rownum:int) -> win32.CDispatch:  # Range Object
        """Retourne la ligne de la feuille de calcul Excel correspondant au numéro de ligne."""
        return self.listRows(rownum).Range  #type: ignore

    def addRow(self) -> win32.CDispatch:    # Range object
        """Ajoute une ligne à la feuille de calcul Excel et retourne la plage de la nouvelle ligne."""
        ret = self.listRows.Add()
        return ret.Range

    def getXLOpe(self, row:int) -> Ope:
        """Retourne un objet Ope représentant l'opération bancaire dans la ligne Excel spécifiée."""                                                                  
        return self.XLOpe(self.getRow(row))

    # Membres définis dans une classe dérivée
    #----------------------------------------
    @abstractmethod
    def getlistRows(self) -> win32.CDispatch:
        ...

    @abstractmethod
    def StoreOpe(self, ope:Ope) -> None:
        ...

    @abstractmethod
    def XLOpe(self, range:win32.CDispatch)->Ope:
        ...

    @property
    @abstractmethod
    def solde_initial(self) -> Decimal:
        ...

    @solde_initial.setter
    @abstractmethod
    def solde_initial(self, value:Decimal):
        ...                                                                                                                                                    

    
    
