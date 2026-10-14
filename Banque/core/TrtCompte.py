from inspect import isclass
from Banque.core.Ope import Ope
from Banque.core.Excel import Excel
from decimal import Decimal
import locale
from typing import Any
import importlib.resources as res
import timer

class TrtCompte():
    def __init__(self, context, oHTML):
        self.putgui = context['putgui']
        self.oHTML = oHTML
        self.oXL = None
        self.context = context
        self.tabexcl = res.read_text('LBP', 'exclusions.txt')
 
    def run(self, nom_compte):
        def _cb(msgtype:str, value:Any):
            self.putgui(msgtype, value) # type: ignore
        def _tr(msg:str):
            _cb("log", msg+'\n')
        # timer.time("Début du traitement du compte", __name__)
        # _tr("Attente du choix du compte...")
        self.oHTML.waitForRelevé()
        # timer.time("Retour de waitForRelevé", __name__)
        _cb("!N° compte", self.oHTML.getAcctNo())
        _tr(f"Compte: {nom_compte}")

        # Ouverture Excel
        # _tr("Ouverture classeur Excel")
        clsExcel = self.context['Destination']
        if not (isclass(clsExcel) and issubclass(clsExcel, Excel)):
               raise TypeError("La classe Excel fournie n'est pas un sous-type de Excel")
        self.oXL = clsExcel(nom_compte)
        # timer.time("Classeur Excel ouvert", __name__)
        newAccount = self.oXL.newAccount
        # _tr("Classeur Excel ouvert")
        _cb("XL_pos", self.oXL.hwnd)   # pour que la présentation positionne la fenêtre Excel
        self.oXL.setVisible(True)
        self.oXL.WorkBook.Activate()
        _cb("!Excel", self.oXL.getStatusString())
        # Recherche dernière opération Excel
        lastrow = self.oXL.getLastRow()
        try:
            lastope = self.oXL.getXLOpe(lastrow)
        except:
            raise ValueError("La dernière ligne du tableau Excel n\'est pas une écriture")
        _tr(f"Dern.opé: {lastope}")
        _cb("!Dernière", lastope)
        # timer.time(f"Lastope: {lastope}", __name__)

        self.oXL.setVisibleRow(10)

        idxHTML = 0
        tot_excl = Decimal(0)

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
        # Ignorer les opérations exclues
        while True:
            ope = self.oHTML.getHTMLOpe(idxHTML)
            if (not ope.isEOF()) and (ope.lib in self.tabexcl):
                _trace_ope(ope, "exclue ")
                tot_excl += Decimal(ope.montant)
                idxHTML += 1
            else:
                break

        # Empiler les opérations HTML jusqu’à lastope ou EOF
        operations:list[Ope] = []
        while not (ope == lastope or ope.isEOF()):
            # timer.time(f"Traitement de l'opération HTML idx={idxHTML}", __name__)
            _trace_ope(ope)
            operations.append(ope)
            idxHTML += 1
            ope = self.oHTML.getHTMLOpe(idxHTML)

        nb_ope = len(operations)
        # timer.time(f"Nombre d'opérations HTML empilées: {nb_ope}", __name__)
        _cb("!Nb ope", nb_ope)

        soldeHTML = Decimal(self.oHTML.getSolde())

        #self.oHTML.quit()

        # Vérifier l’historique
        if not newAccount and ope.isEOF():
            raise ValueError(
                "Le relevé HTML ne contient pas assez d'historique pour remplir le fichier Excel."
            )

        # Dépiler vers Excel
        tot_ope = Decimal(0)
        while operations:
            ope = operations.pop()
            self.oXL.StoreOpe(ope)
            tot_ope += Decimal(ope.montant)

        # calcul du solde initial
        solde = Decimal(self.oHTML.getSolde())  
        if newAccount:
                self.oXL.solde_initial = solde - tot_ope - tot_excl
        # On ne sauvgarde pas les éventuelles modifications aux fichiers existants

        _tr(
            f"Solde: {locale.currency(soldeHTML, grouping=True, symbol=True)}\n"
            f"Résultat: {nb_ope} opération(s) ajoutée(s)\n"
        )
        # timer.time("Fin du traitement du compte", __name__)

