# metier_Cesu.py
from abc import abstractmethod

from Monitor.core.AppMetier import AppMetier
from Monitor.core.chrome import webdriver, ChromeDriver, By 
from Monitor.utils.Parser import Parser            
from collections import defaultdict
import re
from typing import Any
import time
import os

# PATH_OUT = os.environ['CESU_PATH']

class ExtractionMetier(AppMetier):

    def __init__(self, context):
        super().__init__(context)
        self.Path_out = context['Path_out']
        if not os.path.exists(self.Path_out):
            raise ValueError(f"le répertoire {self.Path_out} n\'existe pas")
        self.oHTML = None

    def run(self):
        getgui = self.getgui        
        putgui = self.putgui
     
        def _send(msgtype:str, value:Any):
            putgui(msgtype, value) # pyright: ignore[reportOptionalCall]
        def _trace(msg:str):
            _send("log", msg+'\n')

        # Définition de la procédure de nettoyage
        def nettoyage():
            if self.oHTML:
                self.oHTML.proc.terminate()
        self.context['nettoyage'] = nettoyage
            
        # Ouverture HTML
        self.oHTML = ChromeDriver('https://www.cesu.urssaf.fr/info/accueil.html')
       
        # Raccourcis pour les méthodes de recherche d'éléments HTML
        waitFor = self.oHTML.waitFor
        driver:webdriver.Chrome = self.oHTML.driver
        parser = Parser(driver)

        # Demander à la présentation de redimensionnerr la fenêtre
        _send("html_opened", self.oHTML.hwnd)
        _send('title', f'CESU')

        _trace("Connexion au site...")

        # On ouvre le menu hamb
        but_hamb = parser.getElementById('button', 'menuhamb')
        driver.execute_script("arguments[0].click();", but_hamb)   # .click direct ne fonctionne pas
        time.sleep(0.3)
        ul_menu = parser.getElement('//ul[@id="headerBandeauBasMenuListe"]')
        # On regarde si l'élément de menu 'Tableau de bord' existe
        but_tdb = parser.getElement('.//a[contains(., "Tableau de bord")]', ul_menu)
        if  but_tdb is None:
            # L'élément de menu 'Tableau de bord' n'existe pas.
            # On exploite l'élément 'Se connecter'
            but_cnx = parser.getElementById('a', 'page_se_connecter_link_i1')
            href = str(but_cnx.get_attribute('href'))
            driver.get(href)
            time.sleep(0.4)
            # On atteind la page de connexion.
            # Les champs user et password sont déjà remplis
            user = parser.getElementById('input', 'username')   
            user.send_keys('\u0001francoisegoudal')  # Ctrl+A to select all text before typing

            password = parser.getElementById('input', 'password')
            password.send_keys('\u0001Grouch337282!')  # Ctrl+A to select all text before typing

            but_valider = parser.getElementById('button', 'btn-valider')
            driver.execute_script('arguments[0].click()', but_valider)
        else:
            but_tdb.click()
        time.sleep(0.5)

        assert driver.current_url == 'https://www.cesu.urssaf.fr/decla/index.html?page=page_empl_tableau_bord&LANG=FR'
        _trace("Choisir un traitement")
        dic = getgui('input', 'form', 999999) # pyright: ignore[reportOptionalCall]
        trt = dic['buttons']
        _trace(f'traitement choisi: {trt}')

        _send('title', f'CESU - {trt}')
        # On est sur le tableau de bord.

        _send('label', f'Extraction des {trt} en cours...')
       
        URLs = {'prelevements':"https://www.cesu.urssaf.fr/decla/index.html?page=page_empl_mes_prelevements&LANG=FR",
                'declarations':"https://www.cesu.urssaf.fr/decla/index.html?page=page_empl_mes_declarations&LANG=FR"}

        driver.get(URLs[trt])
        if trt == 'prelevements':
            #--------------------------------------
            # Traitement des prélèvements
            #-----------,---------------------------
            time.sleep(0.5)
            _trace("Page prélèvements")    
            result:defaultdict[str, list[tuple]] = defaultdict(list)
            parser.getElementById('button', 'periodeParDefaut').click()
            time.sleep(0.5) # Petit temps d'attente pour le déploiement
            prélevements = parser.getElements('//div[@id="resultatsAffiches"]/div')
            for div_prelevement in prélevements[::-1]:
                date_prelevement = parser.getElement('.//p[@name="date_prelevement"]', div_prelevement).text
                bouton_se_connecter = parser.getElementByClass('button','bouton_recapitulatif', div_prelevement)
                bouton_se_connecter.click()
                time.sleep(0.1) # Petit temps d'attente pour le déploiement du tableau
                avis = parser.getElements('.//div[@class="ligne avis_donnees"]', div_prelevement)
                for lig in range(0, len(avis)-1, 4):
                    dict = {}
                    for i in range(4):
                        time.sleep(0.1) # Petit temps d'attente
                        lib = parser.getElementByClass('div', 'bloc_libelle', avis[lig + i]).text
                        val = parser.getElementByClass('div', 'bloc_champs', avis[lig + i]).text
                        dict[lib] = val
                    
                    nom = dict['Salarié :']
                    periode = dict['Période d\'emploi :']
                    montant = dict['Montant des cotisations et de l’impôt sur le revenu prélevé :']
                    montant = re.sub('[^0-9,]', '', montant)
                    declaration = dict['Déclaration :']
                    _send('row', (periode, nom, montant))
                    result[nom].append((periode, montant, declaration))
                bouton_se_connecter.click()
            #--------------------------------------------------------
            # On a fini de balayer les div_prelevement
            # On recopie le dictionnaire result dans des fichiers csv
            #--------------------------------------------------------
            with open(f'{self.Path_out}\\employés.csv', 'w', encoding='utf-8') as emp:
                emp.write("Employé\n")
                for employe in result:
                    emp.write(f'"{employe}"\n')
                    with open(f"{self.Path_out}\\prelevements_{employe}.csv", 'w', encoding='utf-8') as f:
                        f.write("Période;Montant;Déclaration\n")
                        infos = result[employe]
                        for periode, montant, declaration in infos:
                            f.write(f"{periode};{montant};{declaration}\n")

        elif trt == "declarations":
            #--------------------------------------
            # Traitement des déclarations
            #--------------------------------------

            _trace("Page déclarations")    
            result:defaultdict[str, list[tuple]] = defaultdict(list)
            #parser.getElementById('button', 'periodeSpecifique').click()
            #time.sleep(5) # Gros temps d'attente pour le déploiement
            declarations = lazy_load(driver, '//div[@id="resultatsAffiches"]/div')                       
            _trace(f"Nombre de déclarations: {len(declarations)}")

            for div_declaration in declarations[::-1]:
                driver.execute_script("arguments[0].scrollIntoView(true)", div_declaration)
                div_data = parser.getElementByClass('div', 'bloc_accordeon', div_declaration)
                #On force l'ouverture du bloc
                driver.execute_script("arguments[0].classList.add('show');", div_data)
                def getvar(name:str):
                    # relatif à div_declaration car certains éléments sont dans button, d'autres dans div_data
                    return parser.getElement(f'.//span[@name="{name}"]', div_declaration).text
                employe = getvar('nom')
                periode = getvar('periode')
                nature_act = getvar('nature_activite')
                declaration = getvar('numCheque')   
                heures = getvar('heures')
                salaire_horaire = getvar('salaire_horaire')
                complements = getvar('complements_salaire')
                total_net_declare = getvar('total_net_delcare')
                total_net_paye = getvar('total_net_paye_PAS') + ' €' # type: ignore
                _send('row',(periode, employe, total_net_paye))
                result[employe].append(                                 # type: ignore
                    (periode, nature_act, declaration, heures, salaire_horaire,complements, total_net_declare, total_net_paye)
                )
                driver.execute_script("arguments[0].classList.remove('show');", div_data)

            # Exploitation du résultat et écriture des fichiers csv
            # -----------------------------------------------------    
            for employe in result:
                with open(f'{self.Path_out}\\declarations_{employe}.csv', 'w', encoding='utf-8') as f:
                    f.write("periode;nature_act;declaration;heures;salaire_horaire;complements;total_net_declare;total_net_paye\n")
                    infos = result[employe]
                    for periode, nature_act, declaration, heures, salaire_horaire,complements, total_net_declare, total_net_paye in infos:
                        f.write(f"{periode};{nature_act };{declaration};{heures};{salaire_horaire};{complements};{total_net_declare};{total_net_paye}\n")

        _send('label', f'Extraction des {trt} terminée')

        _trace("Fin normale du programme")
        _send("fnorm", None)

        return

def lazy_load(driver:webdriver.Chrome, ref:str):
    # On scroll jusqu'en bas de la page pour forcer le chargement de tous les éléments
    # On répète l'opération tant que le nombre d'éléments chargés augmente
    # On suppose que le site charge les éléments par paquets, et qu'il n'y a pas de bouton "Charger plus"
    # On peut aussi utiliser ActionChains pour simuler un scroll plus naturel
    from selenium.webdriver.common.action_chains import ActionChains

    actions = ActionChains(driver)

    previous_count = 0

    while True:
        # scroll comme un humain
        actions.scroll_by_amount(0, 4000).perform()
        time.sleep(1)
        # compter les éléments chargés
        items = driver.find_elements(By.XPATH, ref)
        count = len(items)
        if count == previous_count:
            break  # plus rien ne se charge
        previous_count = count
    return items
