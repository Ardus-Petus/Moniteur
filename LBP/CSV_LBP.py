from selenium.webdriver.remote.webelement import WebElement
from Banque.core.HTML import HTML
from Banque.core.Ope import Ope
import datetime
import time
import os
import re
import csv

class CSV_LBP(HTML):
    """Classe pour gérer les opérations bancaires dans un site WEB spécifique à La Banque Postale."""
    DELAY = 180  # 3 minutes   
    CNXRELEVE = "releve_ccp.ea|releve_cne.ea"
    CNXCOMPTE = "afficheSyntheseCCP-synthese_ccp.ea"
    URL = 'https://www.labanquepostale.fr/particulier/connexion-espace-client.html'

    
    def __init__(self):
        """Initialise l'objet HTML et démarre le navigateur Chrome avec Selenium.
           accède à la page de connexion à l'espace client de La Banque Postale
        """
        super().__init__(self.URL)
        

    def waitForCnxComptes(self) -> None:
        """Attend que la page Comptes et Contrats soit chargée."""
        self.waitFor(self.CNXCOMPTE, self.DELAY)
    
    def waitForRelevé(self) -> None:                        # Initialise le tableau self.rows avec la liste des opérations,
        """Attend que la page Relevé soit chargée."""
        self.waitFor(self.CNXRELEVE, self.DELAY)

        # Accès au lien de téléchargement du relevé
        bouton_download = self.chrome.findElement('a[title^="Télécharger"]')
        href = bouton_download.get_attribute('href')
        self.chrome.new_window()       
        self.chrome.get(href) # Simule un clic sur bouton_download
        bouton_download_ops = self.findElement('button[aria-label^="Télécharger"]')
        self.chrome.execute_script('(arg) => arg.click()', bouton_download_ops)
        # time.sleep(1)  # Attendre un peu pour s'assurer que le téléchargement a commencé
        # Attendre que le téléchargement soit terminé
        download = self.chrome.page.wait_for_event("download")
        path_csv = r"O:\OneDrive\Téléchargements\Releves\Relevé.csv"     
        if os.path.exists(path_csv):
            os.remove(path_csv)
        download.save_as(path_csv)
        self.chrome.close_window()

        #  Ouverture du fichier csv
        csvfile = open(path_csv, 'r')
        reader = csv.reader(csvfile, delimiter=';')
        # Chargement des lignes du tableau [[date, lib, montant]]
        self.rows = list(reader)[7:] #On exclut les 7 premières lignes (en-têtes)
        csvfile.close()
        #os.remove(path_csv)

       
    def getAcctNo(self) -> str:
        """Retourne le numéro de compte.""" 
               
        elem = self.findElement('//h2[@class="fake-ttl-1"]')
        return elem.text.split('\n')[0][-11:]
    
    def getSolde(self) -> float:
        """Retourne le solde du compte."""
        t = self.findElement('//p[@class="infos-cpt"]//span[contains(@class,"amount")]').text
        n = re.sub('[ \u00a0€]', '', t).replace(',', '.').replace('\u2212', '-')
        return float(n)
    
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

class CSV:
    def __init__(self, path_csv: str):
        self.path_csv = path_csv
        self.rows = []
        csvfile = open(path_csv, 'r')
        reader = csv.reader(csvfile, delimiter=';')
        self.rows = list(reader)[8:]
        csvfile.close()
        pass

