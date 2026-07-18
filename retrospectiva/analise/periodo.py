from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

@dataclass(frozen=True)
class Periodo:
    inicio: Optional[date] = None
    fim: Optional[date] = None
    
    @classmethod
    def tudo(cls) -> "Periodo":
        return cls(None, None)
    
    @classmethod
    def mes(cls, ano: int, mes: int) -> "Periodo":
        inicio = date(ano, mes, 1)
        fim = date(ano, 12, 31) if mes == 12 else date(ano, mes + 1, 1) - timedelta(days=1)
        return cls(inicio, fim)
    
    @classmethod
    def ano(cls, ano: int) -> "Periodo":
        return cls(date(ano, 1, 1), date(ano, 12, 31))
    
    @classmethod
    def dias(cls, dias: int, referencia: Optional[date] = None) -> "Periodo":
        referencia = referencia or date.today()
        return cls(referencia - timedelta(days=dias), referencia)
    
    def __str__(self):
        if self.inicio is None and self.fim is None:
            return "todo o período"
        inicio = str(self.inicio) if self.inicio else "o início"
        fim = str(self.fim) if self.fim else "o fim"
        return f"Começa em {inicio} e vai até {fim}"
