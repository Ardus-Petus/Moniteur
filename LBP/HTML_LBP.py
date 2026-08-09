from selenium.webdriver.remote.webelement import WebElement

from Banque.core.HTML import HTML
from Banque.core.Ope import Ope
import datetime
import time

import re


class HTML_LBP(HTML):
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
        try:
            # On clique sur le bouton "Voir l'historique" s'il est présent
            button = self.findElement("//a[@id='voirHisto']")
            button.click()
            time.sleep(1) # Petit temps d'attente pour le déploiement du tableau
        except:
            pass

        # Chargement des lignes du tableau
        self.rows = self.findElements('//table[@id="mouvementsTable"]/tbody/tr')

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
            i (int): L'index dans le tableau self.rowsde l'opération à récupérer."""

        # Fonction interne pour traiter une ligne du tableau self.rows
        def _extraire_ope(row: WebElement) -> Ope:             
            """Prend une ligne de tableau HTML self.rowset retourne un objet Ope pur.
            Args:
                row: Un élément WebElement représentant une ligne de tableau HTML."""
            cells =self.findCells(row)  # Récupère les cellules de la ligne

            # Il arrive épisodiquement que le texte soit précédé d'un intitulé préfixe
            # Fonction interne pour récupérer la valeur d'une cellule et retirer le préfixe str si présent
            def _getstr(j:int,str:str) -> str:       
                val = cells[j].text
                if val.startswith(str):
                    val = val[len(str)+1:]          # +1 car il y a un \n après le préfixe
                return val.strip()

            # corps de extraire_ope
            date = datetime.datetime.strptime(_getstr(0, "Date"), '%d/%m/%Y')
            lib = " ".join(_getstr(1, "Libellé").replace('\n', ' ').split())
            montant_str = re.sub('[ \u00a0€]', '', _getstr(3, "Montant").replace(',', '.').replace('\u2212', '-'))
            
            # On instancie directement la classe Ope
            return Ope(
                date=date,
                lib=lib,
                montant=float(montant_str)
            )

        # corps de getHTMLOpe
        if i < len(self.rows):
            return _extraire_ope(self.rows[i])
        else:
            return Ope.EOF()

if __name__ == '__main__':
    obj = HTML_LBP()

