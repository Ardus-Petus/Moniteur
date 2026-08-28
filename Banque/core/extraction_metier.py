# extraction_metier.py
from decimal import Decimal
import locale
from typing import Type, Any, Callable
from Banque.core.Excel import Excel
from Banque.core.HTML import HTML
from Banque.core.Ope import Ope
from Monitor.core.AppMetier import AppMetier
from datetime import datetime

import importlib.resources as res

class ManqueHistorique(Exception):
    pass

class ExtractionMetier(AppMetier):
    def __init__(self, context):
        super().__init__(context)
        self.tabexcl = res.read_text('LBP', 'exclusions.txt')
        self.oHTML:HTML|None = None
        self.oXL:Excel|None = None
        locale.setlocale(category=locale.LC_ALL, locale='')

    def run(self):

        def _cb(msgtype:str, value:Any):
            self.putgui(msgtype, value) # type: ignore
        def _tr(msg:str):
            _cb("log", msg+'\n')

        def _trace_ope(ope:Ope, inc_excl:str='incluse'):
            _cb(
                    "row",
                    (
                        inc_excl,
                        ope.date.strftime("%d/%m/%Y"),
                        ope.lib,
                        locale.currency(ope.montant, grouping=True, symbol=True),
                    ),
                )
        def nettoyage():
            if self.oHTML: 
                self.oHTML.quit()
            if self.oXL:
                self.oXL.mgr.maximize()
        self.context['nettoyage'] = nettoyage

        # Affichage de la date
        _cb("Date", datetime.now().strftime('%d/%m/%Y %H:%M:%Sd'))

        # Ouverture HTML
        self.oHTML = self.context['HTML']()

        # Signaler au GUI que HTML est ouvert (pour positionnement fenêtre)
        _cb("html_opened", self.oHTML.hwnd)

        # Attente connexion + relevé
        _tr("Attente de la connexion au site...")
        self.oHTML.waitForCnxComptes()

        _tr("Attente du choix du compte...")
        self.oHTML.waitForRelevé()

        acctNo = self.oHTML.getAcctNo()
        _cb("N° compte", acctNo)

        # Ouverture Excel
        _tr("Ouverture classeur Excel")
        self.oXL = self.context['Excel'](acctNo)
        _cb("XL_opened", self.oXL.hwnd)   # pour que la présentation positionne la fenêtre Excel
        _cb("Excel", self.oXL.getStatusString())

        # Recherche dernière opération Excel
        lastrow = self.oXL.getLastRow()
        try:
            lastope = self.oXL.getXLOpe(lastrow)
        except:
            raise ValueError("La dernière ligne du tableau Excel n\'est pas une écriture")
        _tr(f"Dern. opé: {lastope}")
        _cb("Dern. ", lastope)

        idxHTML = 0
        tot_excl = Decimal(0)

        # Ignorer les opérations exclues
        while True:
            ope = self.oHTML.getHTMLOpe(idxHTML)
            if ope.lib in self.tabexcl:
                _trace_ope(ope, "exclue ")
                tot_excl += Decimal(ope.montant)
                idxHTML += 1
            else:
                break

        # Empiler les opérations HTML jusqu’à lastope ou EOF
        operations:list[Ope] = []
        while not (ope == lastope or ope.isEOF()):
            _trace_ope(ope, 'incluse')
            operations.append(ope)
            idxHTML += 1
            ope = self.oHTML.getHTMLOpe(idxHTML)

        nb_ope = len(operations)
        _cb("Nb ope", nb_ope)

        soldeHTML = Decimal(self.oHTML.getSolde())
        self.oHTML.quit()

        # Vérifier l’historique
        if self.oXL.status != self.oXL.NEW and ope.isEOF():
            raise ManqueHistorique(
                "Le relevé HTML ne contient pas assez d'historique pour remplir le fichier Excel."
            )

        # Dépiler vers Excel
        row = lastrow + 1
        tot_ope = Decimal(0)
        while operations:
            ope = operations.pop()
            self.oXL.StoreOpe(ope)
            tot_ope += Decimal(ope.montant)
            row += 1

        # Solde initial + sauvegarde
        if self.oXL.status == self.oXL.NEW:
            self.oXL.solde_initial = soldeHTML - tot_ope - tot_excl
            self.oXL.saveWorkBook()

        # On ne sauvgarde pas les éventuelles modifications aux fichiers existants

        _cb(
                "log",
                f"Solde: {locale.currency(soldeHTML, grouping=True, symbol=True)}\n"
                f"Résultat: {nb_ope} opération(s) ajoutée(s)\n"
            )
        _tr("Fin normale du programme")

        return 
