# metier_CESU.py
from Monitor.core.AppMetier import AppMetier
from Monitor.core.chrome_Protocol import ChromeProtocol
from collections import defaultdict
import re
from typing import Any
import time
import os

PATH_OUT = os.path.join(os.curdir, "CESU", "Résultats") 
ROOT = 'https://www.cesu.urssaf.fr'
if not os.path.exists(PATH_OUT):
    raise ValueError(f'{PATH_OUT} n\'existe pas')            

class ExtractionMetier(AppMetier):

    def __init__(self, context):
        super().__init__(context)
        self.oHTML = None
        self.ChromeDriver = context['Driver']

    def run(self):
        getgui = self.getgui        
        putgui = self.putgui
     
        def _send(msgtype:str, value:Any):
            putgui(msgtype, value) 
        def _trace(msg:str):
            _send("log", msg+'\n')

        # Définition de la procédure de nettoyage
        # def nettoyage():
        #     if self.oHTML:
        #         self.oHTML.proc.terminate()
        # self.context['nettoyage'] = nettoyage
            
        # Ouverture HTML
        self.oHTML: ChromeProtocol = self.ChromeDriver(ROOT+'/info/accueil.html')
       
        # Raccourcis pour les méthodes de recherche d'éléments HTML
        
        # Demander à la présentation de redimensionnerr la fenêtre
        _send("HTML_pos", self.oHTML.hwnd)
        _send('title', f'CESU')

        _trace("Connexion au site...")

        # On ouvre le menu hamb
        but = self.oHTML.findElement('button#menuhamb')
        but.click()
        time.sleep(0.3)
        but_cnx = self.oHTML.findElement('a[title="Se connecter"]')
        if but_cnx:
            # Si le bouton "Se connecter" est affiché (on ne peut pas le cliquer)
            href = str(but_cnx.get_attribute('href'))
            if not href.startswith('https:'): href = ROOT+href

            self.oHTML.get(href)
            time.sleep(0.4)
            # On atteind la page de connexion.
            # Les champs user et password ne sont pas déjà remplis
            but_accepter_cookies = self.oHTML.findElement('button#footer_tc_privacy_button')
            if but_accepter_cookies:
                but_accepter_cookies.click()
            # self.oHTML.findElementById('input', 'username').send_keys('francoisegoudal')
            # self.oHTML.findElementById('input', 'password').send_keys('Grouch337282!')           
            time.sleep(0.3)
            self.oHTML.findElement('button#btn-valider').click()
        else:
            but = self.oHTML.findElement('//a[text()="Tableau de bord"]')
            but.click()
        time.sleep(0.5)


        _trace("Choisir un traitement")
        dic = getgui(msg_type='input', payload='form', timeout=999999)
        trt = dic['buttons']
        _trace(f'traitement choisi: {trt}')

        _send('title', f'CESU - {trt}')
        # On est sur le tableau de bord.

        _send('label', f'Extraction des {trt} en cours...')
       
        # URLs = {'prelevements':ROOT+"/decla/index.html?page=page_empl_mes_prelevements&LANG=FR",
        #         'declarations':ROOT+"/decla/index.html?page=page_empl_mes_declarations&LANG=FR"}
        id = { 
            'prelevements': 'page_empl_prelevements',
            'declarations': 'page_empl_mes_declarations'
        }
        time.sleep(0.3)
        button = self.oHTML.findElement('a#' + id[trt])
        button.click()
        if trt == 'prelevements':
            #--------------------------------------
            # Traitement des prélèvements
            #-----------,---------------------------
            time.sleep(0.5)
            _trace("Page prélèvements")    
            result:defaultdict[str, list[tuple]] = defaultdict(list)
            self.oHTML.findElement('button#periodeParDefaut').click()
            time.sleep(0.1) # Petit temps d'attente pour le déploiement
            prélevements = self.oHTML.findElements('div#resultatsAffiches>div')
            for div_prelevement in prélevements[::-1]:
                self.oHTML.execute_script("arguments[0].scrollIntoView(true);", div_prelevement)
                date_prelevement = self.oHTML.findElement('p[name="date_prelevement"]', div_prelevement).text
                bouton_se_connecter = self.oHTML.findElementByClass('button','bouton_recapitulatif', div_prelevement)
                bouton_se_connecter.click()
                time.sleep(0.1) # Petit temps d'attente pour le déploiement du tableau
                avis = self.oHTML.findElements('div.ligne.avis_donnees', div_prelevement)
                for lig in range(0, len(avis)-1, 4):
                    dict = {}
                    for i in range(4):
                        time.sleep(0.1) # Petit temps d'attente
                        lib = self.oHTML.findElement('div.bloc_libelle',avis[lig + i]).text[:-2]
                        val = self.oHTML.findElement('div.bloc_champs', avis[lig + i]).text
                        dict[lib] = val
                    
                    nom = dict['Salarié']
                    periode = dict['Période d\'emploi']
                    montant = dict['Montant des cotisations et de l’impôt sur le revenu prélevé']
                    montant = re.sub('[^0-9,]', '', montant)
                    declaration = dict['Déclaration']
                    _send('row', (periode, nom, montant))
                    result[nom].append((periode, montant, declaration))
                bouton_se_connecter.click()
            #--------------------------------------------------------
            # On a fini de balayer les div_prelevement
            # On recopie le dictionnaire result dans des fichiers csv
            #--------------------------------------------------------
            with open(f'{PATH_OUT}\\employés.csv', 'w', encoding='utf-8') as emp:
                emp.write("Employé\n")
                for employe in result:
                    emp.write(f'"{employe}"\n')
                    with open(f"{PATH_OUT}\\prelevements_{employe}.csv", 'w', encoding='utf-8') as f:
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
            self.oHTML.findElement('//button[@id="periodeSpecifique"]').click()
            self.oHTML.execute_script("window.scrollTo(0, document.body.scrollHeight)");
            time.sleep(2)
            declarations = self.oHTML.findElements('//div[@id="resultatsAffiches"]/div') 

            for div_declaration in declarations[::-1]:
                self.oHTML.execute_script("arguments[0].scrollIntoView(true)", div_declaration)
                div_button = self.oHTML.findElement('button.bouton_declaration', div_declaration)
                div_data = self.oHTML.findElement('div[name="sansGDA"]', div_declaration)
                #On force l'ouverture du bloc
                div_accordeon = self.oHTML.findElement('div.bloc_accordeon', div_declaration)
                self.oHTML.execute_script("arguments[0].classList.add('show')", div_accordeon)
                def getvar(name:str, div):
                    # relatif à div_declaration car certains éléments sont dans button, d'autres dans div_data
                    return self.oHTML.findElement(f'span[name="{name}"]', div).text
                employe = getvar('nom', div_button)
                periode = getvar('periode', div_button)
                nature_act = getvar('nature_activite', div_button)
                declaration = getvar('numCheque', div_button)   
                heures = getvar('heures', div_data)
                salaire_horaire = getvar('salaire_horaire', div_data)
                complements = getvar('complements_salaire', div_data)
                total_net_declare = getvar('total_net_delcare', div_data)
                total_net_paye = getvar('total_net_paye_PAS', div_data)
                _send('row',(periode, employe, total_net_paye))
                result[employe].append(
                    (periode, nature_act, declaration, heures, salaire_horaire,complements, total_net_declare, total_net_paye)
                )
                self.oHTML.execute_script("arguments[0].classList.remove('show');", div_accordeon)

            # Exploitation du résultat et écriture des fichiers csv
            # -----------------------------------------------------    
            for employe in result:
                with open(f'{PATH_OUT}\\declarations_{employe}.csv', 'w', encoding='utf-8') as f:
                    f.write("periode;nature_act;declaration;heures;salaire_horaire;complements;total_net_declare;total_net_paye\n")
                    infos = result[employe]
                    for periode, nature_act, declaration, heures, salaire_horaire,complements, total_net_declare, total_net_paye in infos:
                        f.write(f"{periode};{nature_act };{declaration};{heures};{salaire_horaire};{complements};{total_net_declare};{total_net_paye}\n")

        _send('label', f'Extraction des {trt} terminée')

        _trace("Fin normale du programme")
       

        return
