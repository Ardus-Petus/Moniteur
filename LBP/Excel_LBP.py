import win32com.client as win32  # installé par pip install pywin32
from datetime import datetime
from Banque.core.Excel import Excel
from Banque.core.Ope import Ope
import os
from decimal import Decimal

class Excel_LBP(Excel):
    """Classe dérivée de Excel pour gérer les opérations bancaires dans un fichier Excel spécifique à la Banque Postale."""
 
    def __init__(self, acct:str):
        """Initialise l'objet COM Excel et affiche le classeur pour un compte donné.
        
        Args:
            acct (str): Le nom du compte bancaire.
        """
        super().__init__(
            acct, 
            worksheetname='banque', 
            rep='o:\\onedrive\\perso\\', 
            modelpath=os.path.join(os.path.dirname(__file__),"modbanque.xltx")
        )

    def getlistRows(self) -> win32.CDispatch: #(Objet listrows)
        """Retourne la liste des lignes de la feuille de calcul Excel."""
        return self.WorkSheet.ListObjects("Banque").ListRows # type: ignore

    def StoreOpe(self, ope:Ope) -> None:
        """Enregistre une opération à la fin du tableau Excel."""    
        rowRng = self.addRow()                  # Renvoie le Range d'une nouvelle ligne ajoutée au tableau
        self.Appli.Goto(rowRng.Cells(1, 1))     # type: ignore # Se positionne sur la nouvelle ligne pour la rendre visible
        rowRng.Columns("A").Value = rowRng.Row
        rowRng.Columns("B").Value = ope.date.toordinal() - 693594  # Conversion de la date en format Excel
        rowRng.Columns("C").Value = ope.lib
        rowRng.Columns("D").Value = ope.montant
    
        for entry in self.tablib:
            # on teste la présence du premier champ dans le libellé de l'opération
            if ope.lib.lower().find(entry[0].lower()) >= 0:
                # si présent, on remplit les champs Opération et Ventilation
                rowRng.Columns("G").Value = entry[1]  	# Opération
                rowRng.Columns("H").Value = entry[2]	# Ventilation
                break
 
    def XLOpe(self, range:win32.CDispatch)->Ope:
        return Ope(
            datetime.strptime(range.Columns("B").Text, '%d/%m/%Y'),        #date
            ' '.join(range.columns('C').Text.replace('\n', ' ').split()),  #lib
            range.Columns("D").Value                                       #montant
        )
        
    @property
    def solde_initial(self) -> Decimal:
        return Decimal(str(self.WorkSheet.Cells(2, "D").Value)) # type: ignore
    
    @solde_initial.setter
    def solde_initial(self, value: Decimal) -> None:
        self.WorkSheet.Cells(2,"D").Value = float(value)    #type: ignore                                                                                                                                                  

if __name__ == '__main__':
    test = Excel_LBP('test')