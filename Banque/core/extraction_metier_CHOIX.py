# extraction_metier.py
import locale
from typing import Type, Any, Callable
import Monitor.utils.winmgt as winmgt
from Banque.core.Excel import Excel
from Banque.core.HTML import HTML
from Banque.core.TrtCompte import TrtCompte
from Monitor.core.AppMetier import AppMetier
from Monitor.utils.ExcelWindowManager import ExcelWindowManager
from datetime import datetime
from inspect import isclass

import importlib.resources as res

class ManqueHistorique(Exception):
    pass

class ExtractionMetier(AppMetier):
    def __init__(self, context):
        super().__init__(context)
        self.tabexcl = res.read_text('LBP', 'exclusions.txt')
        self.oHTML:HTML|None = None
        locale.setlocale(category=locale.LC_ALL, locale='')
        def nettoyage():
            if self.oHTML:
                self.oHTML.quit()
            try: 
                ewm = ExcelWindowManager()
                ewm.appli.ActiveWorkbook.Worksheets(3).Activate()
                ewm.cascade()
            except: 
                pass
        context['nettoyage'] = nettoyage
        
    def run(self):

        def _cb(msgtype:str, value:Any):
            self.putgui(msgtype, value) # type: ignore
        def _tr(msg:str):
            _cb("log", msg+'\n')

        _tr('Début du programme d\'extraction')
        _cb("title", "Extraction Metier")
        _cb('!Date', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        # Ouverture HTML
        clsHTML = self.context['HTML']
        if not (isclass(clsHTML) and issubclass(clsHTML, HTML)):
            raise TypeError("La classe HTML fournie n'est pas un sous-type de HTML")
        self.oHTML = clsHTML()
        chrome = self.oHTML.chrome
        # Signaler au GUI que HTML est ouvert (pour positionnement fenêtre)
        _cb("HTML_pos", self.oHTML.hwnd)
        
        # Attente connexion + relevé
        _tr("Attente de la connexion au site...")
        self.oHTML.waitForCnxComptes()
        winmgt.minimize(self.oHTML.hwnd)

        #Pour passer de la page afficheSynthèse à la page du relevé du CCP
        releveCCP=chrome.findElement('h3.title>a').get_attribute('href') # URL du relevé du CCP (on y revient à chaque itération)
        dejavu = []

        while True:
            chrome.get(releveCCP)           # Accès à la page du relevé du CCP (on y revient à chaque itération)
            options = chrome.findElements('select#liste-comptes>option')
            comptes = {i.text:i for i in options}
            if len(dejavu) == len(comptes):
                break
            nom_compte = self.getgui('popup', comptes.keys(), 999999)   # Lecture du compte choisi par l'utilisateur
            if nom_compte == '__fermer__':
                break
            dejavu.append(nom_compte)   
            chrome.execute_script("arguments[0].setAttribute('selected', 'true')", comptes[nom_compte])
            bouton_consulter=chrome.findElement('button[aria-label="Consulter le compte"]')
            bouton_consulter.click()    # Envoie sur la page du relevé du compte désigné par nom_compte
            compte = TrtCompte(self.context, self.oHTML)
            compte.run( nom_compte)

        _tr("Fin normale du programme")

        return 
