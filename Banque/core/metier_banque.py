# metier_banque.py
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
        # timer.time("Initialisation extraction métier", __name__)
        super().__init__(context)
        
        self.tout_traiter = context.get('tout_traiter', False)
        self.tabexcl = res.read_text('LBP', 'exclusions.txt')
        self.oHTML:HTML|None = None
        locale.setlocale(category=locale.LC_ALL, locale='')
        def nettoyage():
            if self.oHTML:
                self.oHTML.quit()
            try: 
                ewm = ExcelWindowManager()
                ewm.appli.ActiveWorkbook.Worksheets(3).Activate() # Activation de la troisième feuille de calcul : CCP
                ewm.cascade()
            except: 
                pass
        context['nettoyage'] = nettoyage
        
    def run(self):
        # timer.time("Début de la méthode run", __name__)

        def _cb(msgtype:str, value:Any):
            self.putgui(msgtype, value) # type: ignore
        def _tr(msg:str):
            _cb("log", msg+'\n')

        nom_compte:str|None = None

        _tr('Début du programme d\'extraction')
        _cb("title", "Extraction Metier")
        _cb('!Date', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        # Ouverture HTML
        clsHTML = self.context['Source']
        if not (isclass(clsHTML) and issubclass(clsHTML, HTML)):
            raise TypeError("La classe HTML fournie n'est pas un sous-type de HTML")
        clsDriver = self.context['Driver']
        self.oHTML = clsHTML(clsDriver)
        # timer.time("HTML ouvert et driver initialisé", __name__)
        chrome = self.oHTML.chrome
        # Signaler au GUI que HTML est ouvert (pour positionnements fenêtre)
        _cb("HTML_pos", self.oHTML.hwnd)
        
        # Attente connexion + relevé
        _tr("Attente de la connexion au site...")
        self.oHTML.waitForCnxComptes()
        # timer.time("Connexion au site et relevé attendus",__name__)
        # Minimiser la fenêtre HTML pour ne pas gêner l'utilisateur
        # qui ne verra que les fenêtres Excel
        winmgt.minimize(self.oHTML.hwnd)

        dejavu = []

        while True:
            _tr("Choix du compte en cours...")

            comptes = self.oHTML.get_liste_comptes() # retourne la liste des noms de comptes
            # Si tous les comptes ont l  traités,on sort de la boucle while
            if len(dejavu) == len(comptes):
                break

            if self.tout_traiter:       # si on est en mose automatique (tout_traiter)
                for nom_compte in comptes:
                    if nom_compte not in dejavu:
                        break           # On sort du for avec un compte non encore traité
                else:
                    break  # On sort du while (Tous les comptes ont été traités)
            else:                       # si on est en mode manuel                               
                nom_compte = self.getgui('popup', comptes, 999999)   # Lecture du compte choisi par l'utilisateur
                if nom_compte == '__fermer__':  # L'utilisteur a cliqué sur "Fermer"
                    break
                elif nom_compte == '__tout__':  # L'utilisateur a cliqué sur "Tout traiter"
                    self.tout_traiter = True
                    continue
            # On arrive ici après avoir choisi un compte dans nom_compte (soit par l'utilisateur, soit automatiquement)
            
            # timer.time(f"Compte sélectionné : {nom_compte}",__name__)
            _tr(f"Compte sélectionné : {nom_compte}")
            assert nom_compte is not None, "Aucun compte n'a été sélectionné"
            dejavu.append(nom_compte)                               
            self.oHTML.charger_page_releve(nom_compte)
            pass

            # Traitement du compte choisi
            # timer.time(f"Début du traitement du compte : {nom_compte}",__name__)
            compte = TrtCompte(self.context, self.oHTML)
            compte.run( nom_compte)
            # timer.time(f"Fin du traitement du compte : {nom_compte}",__name__)

        _tr("Fin normale du programme")
        #if self.tout_traiter:
        if True:
            _cb("stop", None)       # On arrete le GUI
        return                      # Fin du programme (fin du thread)
