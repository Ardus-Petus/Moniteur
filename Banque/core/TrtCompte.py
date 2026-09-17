from inspect import isclass
from Banque.core.Ope import Ope
from Banque.core.Excel import Excel
from decimal import Decimal
import locale
from typing import Any
import importlib.resources as res

class TrtCompte():
    def __init__(self, context, oHTML):
        self.putgui = context['putgui']
        self.oHTML = oHTML
        self.oXL = None
        self.context = context
        self.tabexcl = res.read_text('LBP', 'exclusions.txt')
 
    def run(self):
        def _cb(msgtype:str, value:Any):
            self.putgui(msgtype, value) # type: ignore
        def _tr(msg:str):
            _cb("log", msg+'\n')
         
        # _tr("Attente du choix du compte...")
        self.oHTML.waitForRelevé()

        acctNo = self.oHTML.getAcctNo()
        _cb("!N° compte", acctNo)

        # Ouverture Excel
        # _tr("Ouverture classeur Excel")
        clsExcel = self.context['Excel']
        if not (isclass(clsExcel) and issubclass(clsExcel, Excel)):
               raise TypeError("La classe Excel fournie n'est pas un sous-type de Excel")
        self.oXL = clsExcel(acctNo)
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
            if ope.lib in self.tabexcl:
                _trace_ope(ope, "exclue ")
                tot_excl += Decimal(ope.montant)
                idxHTML += 1
            else:
                break

        # Empiler les opérations HTML jusqu’à lastope ou EOF
        operations:list[Ope] = []
        while not (ope == lastope or ope.isEOF()):
            _trace_ope(ope)
            operations.append(ope)
            idxHTML += 1
            ope = self.oHTML.getHTMLOpe(idxHTML)

        nb_ope = len(operations)
        _cb("!Nb ope", nb_ope)

        soldeHTML = Decimal(self.oHTML.getSolde())

        #self.oHTML.quit()

        # Vérifier l’historique
        if self.oXL.status != Excel.NEW and ope.isEOF():
            raise ValueError(
                "Le relevé HTML ne contient pas assez d'historique pour remplir le fichier Excel."
            )

        # Dépiler vers Excel
        tot_ope = Decimal(0)
        while operations:
            ope = operations.pop()
            self.oXL.StoreOpe(ope)
            tot_ope += Decimal(ope.montant)

        # Solde initial + sauvegarde
        if self.oXL.status == Excel.NEW:
            self.oXL.solde_initial = soldeHTML - tot_ope - tot_excl
            self.oXL.saveWorkBook()

        # On ne sauvgarde pas les éventuelles modifications aux fichiers existants

        _tr(
            f"Solde: {locale.currency(soldeHTML, grouping=True, symbol=True)}\n"
            f"Résultat: {nb_ope} opération(s) ajoutée(s)\n"
        )

