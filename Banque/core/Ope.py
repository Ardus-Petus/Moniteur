from dataclasses import dataclass
from datetime import date as _date

@dataclass
class Ope:
    date: _date
    lib: str
    montant: float

    DATE_EOF = _date(9999, 12, 31)

    def __str__(self)->str:
        return f"[{self.date.strftime('%d/%m/%Y')} / {self.lib[:50]:<50} / {self.montant}]"

    def isEOF(self)->bool:
        return self.date == Ope.DATE_EOF

    @staticmethod
    def EOF()->Ope:
        return Ope(Ope.DATE_EOF, '', 0)
