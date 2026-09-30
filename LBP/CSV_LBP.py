from LBP.HTML_LBP import HTML_LBP 
from Banque.core.Ope import Ope
import datetime
import time
import os
import re
import csv

class CSV_LBP(HTML_LBP):
    """Classe pour gérer les opérations bancaires avec téléchargement CSV spécifique à La Banque Postale."""
 
    
    def waitForRelevé(self) -> None:                        # Initialise le tableau self.rows avec la liste des opérations,
        # Cette méthode remplace la méthode waitForRelevé de la classe parente HTML_LBP
        # pour gérer le téléchargement du relevé au format CSV  
        # et initialiser le tableau self.rows avec la liste des opérations
        self.waitFor(self.CNXRELEVE, self.DELAY)
        time.sleep(0.5)  # Attendre un court instant pour s'assurer que la page est complètement chargée
        page_releve = self.chrome.current_url

        # Accès au lien de téléchargement du relevé
        bouton_download = self.findElement('a[title^="Télécharger"]')
        href = bouton_download.get_attribute('href')
        self.chrome.get(href) # Simule un clic sur bouton_download
        bouton_download_ops = self.findElement('button[aria-label^="Télécharger"]')
       
        file = self.download(bouton_download_ops)

        #  Ouverture du fichier csv
        csvfile = open(file, 'r')
        reader = csv.reader(csvfile, delimiter=';')
        # Chargement des lignes du tableau [[date, lib, montant]]
        self.rows = list(reader)[7:] #On exclut les 7 premières lignes (en-têtes)
        csvfile.close()
        #os.remove(path_csv)
        
        self.get(page_releve)

    def getHTMLOpe(self, i: int) -> Ope:
        """Retourne l'opération à l'index i, renvoie EOF si l'index est hors du tableau.
        Args:
            i (int): L'index dans le tableau self.rows de l'opération à récupérer."""

        # Fonction interne pour traiter une ligne du tableau self.rows
        def _extraire_ope(row) -> Ope:             
            _date, _lib, _montant = row
            date = datetime.datetime.strptime(_date, '%d/%m/%Y')
            lib = " ".join(_lib.replace('\n', ' ').split())
            montant = float(_montant.replace(',', '.'))
            
            # On instancie directement la classe Ope
            return Ope(
                date=date,
                lib=lib,
                montant=montant
            )

        # corps de getHTMLOpe
        if i < len(self.rows):
            return _extraire_ope(self.rows[i])
        else:
            return Ope.EOF()

# class CSV:
#     def __init__(self, path_csv: str):
#         self.path_csv = path_csv
#         self.rows = []
#         csvfile = open(path_csv, 'r')
#         reader = csv.reader(csvfile, delimiter=';')
#         self.rows = list(reader)[8:]
#         csvfile.close()
#         pass

