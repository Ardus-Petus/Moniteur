from selenium.webdriver.remote.webelement import WebElement
from Banque.core.HTML import HTML
from Banque.core.Ope import Ope
import datetime
import time
from typing import Any
import sys
import re


class HTML_LBP(HTML):
    """Classe pour gérer les opérations bancaires dans un site WEB spécifique à La Banque Postale."""
    DELAY = 180  # 3 minutes   
    CNXRELEVE = "releve_ccp.ea|releve_cne.ea"
    CNXCOMPTE = "afficheSyntheseCCP-synthese_ccp.ea"
    URL = 'https://voscomptesenligne.labanquepostale.fr/wsost/OstBrokerWeb/loginform?TAM_OP=login&ERROR_CODE=0x00000000&URL=%2Fvoscomptes%2FcanalXHTML%2Fidentif.ea%3Forigin%3Dparticuliers'

    
    def __init__(self, driver):
        super().__init__(self.URL, driver)

        # Saisie de l'identifiant et du mot de passe, puis validation de la connexion
        if len(sys.argv) == 3:
            e_identifiant = self.findElement('input#identifiant')
            e_identifiant.set_value(sys.argv[1])
            e_continuer = self.findElement('div#btnContinuer>button')
            e_continuer.click() 
            buttons = self.findElements('button.tb-btn-k')
            for x in sys.argv[2]:
                for button in buttons:
                    if button.text == x:
                        button.click()
                        time.sleep(0.2)
                        break
            self.findElement('button#btnConfirmer').click()
        
    def get_liste_comptes(self) -> list[str]:
        self.get(self.url_page_liste_comptes)
        # Retourne la liste des comptes disponibles
        options = self.findElements('select#liste-comptes>option') #liste des options du select>option
        self.dict_comptes = {i.text:i for i in options}   # on mémorise dans un dictionnaire les comptes disponibles
        return self.dict_comptes.keys()                   # clé = nom du compte, valeur = élément option correspondant

    def charger_page_releve(self, compte) -> None:
        assert self.chrome.current_url == self.url_page_liste_comptes, "La page des comptes n'est pas chargée"
        # on positionne l'attribut 'selected=True' sur l'option correspondant au compte choisi
        elem = self.dict_comptes[compte]
        self.execute_script("arguments[0].setAttribute('selected', 'true')", elem)
        # On clique sur le bouton "Consulter le compte" pour accéder au relevé du compte choisi
        bouton_consulter=self.findElement('button[aria-label="Consulter le compte"]')
        # self.execute_script('arguments[0].click()', bouton_consulter) 
        bouton_consulter.click() 
        pass

                 
    def waitForCnxComptes(self) -> None:
        """Attend que la page Comptes et Contrats soit chargée."""
        self.waitFor(self.CNXCOMPTE, self.DELAY)
        self.url_page_liste_comptes = self.findElement('h3.title>a').get_attribute('href')
    
    def waitForRelevé(self) -> None:                        
        # Attend que la page Relevé soit chargée.
        # Initialise le tableau self.rows avec la liste des opérations,
        self.waitFor(self.CNXRELEVE, self.DELAY)
        try:
            # On clique sur le bouton "Voir l'historique" s'il est présent
            button = self.findElement("a#voirHisto")
            button.click()
            time.sleep(1) # Petit temps d'attente pour le déploiement du tableau
        except:
            pass

        # Chargement des lignes du tableau
        self.rows = self.findElements('table#mouvementsTable>tbody>tr')

    def getAcctNo(self) -> str:
        """Retourne le numéro de compte.""" 
               
        elem = self.findElement('h2.fake-ttl-1')
        return elem.text.split('\n')[0][-11:]
    
    def getSolde(self) -> float:
        """Retourne le solde du compte."""
        solde = self.findElement('p.infos-cpt span.amount').text
        n = re.sub('[ \u00a0€]', '', solde).replace(',', '.').replace('\u2212', '-')
        return float(n)
    
    def getHTMLOpe(self, i: int) -> Ope:
        """Retourne l'opération à l'index i, renvoie EOF si l'index est hors du tableau.
        Args:
            i (int): L'index dans le tableau self.rows de l'opération à récupérer."""

        # Fonction interne pour traiter une ligne du tableau self.rows
        def _extraire_ope(row: Any) -> Ope:             
            """Prend une ligne de tableau HTML self.rowset retourne un objet Ope pur.
            Args:
                row: Un élément WebElement ou locator représentant une ligne de tableau HTML."""
            cells =self.findCells(row)  # Récupère les cellules de la ligne

            # Il arrive épisodiquement que le texte soit précédé d'un intitulé préfixe
            # Fonction interne pour récupérer la valeur d'une cellule et retirer le préfixe str si présent
            def _getstr(j:int,str:str) -> str:       
                val = (cells[j]).text
                if val.startswith(str):
                    val = val[len(str)+1:]          # +1 car il y a un \n après le préfixe
                return val.strip()

            # corps de extraire_ope
            dte = _getstr(0, "Date")
            date = datetime.datetime.strptime(dte, '%d/%m/%Y')
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

