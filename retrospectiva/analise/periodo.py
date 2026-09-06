from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
from retrospectiva.analise.constantes import INICIO_ESTACAO

def _fim_periodo(ano: int, inicio: int, meses: int) -> date:
    seguinte = inicio + meses
    ano_final = ano + (seguinte - 1) // 12
    mes_final = (seguinte - 1) % 12 + 1
    return date(ano_final, mes_final, 1) - timedelta(days=1)

@dataclass(frozen=True)
class Periodo:
    inicio: Optional[date] = None
    fim: Optional[date] = None
    
    @classmethod
    def tudo(cls) -> "Periodo":
        return cls(None, None)
    
    @classmethod
    def ano(cls, ano: int) -> "Periodo":
        return cls(date(ano, 1, 1), date(ano, 12, 31))
    
    @classmethod
    def mes(cls, mes: int) -> "Periodo":
        ano = date.today().year
        return cls(date(ano, mes, 1), _fim_periodo(ano, mes, 1))
    
    @classmethod
    def trimestre(cls, mes: int) -> "Periodo":
        ano = date.today().year
        return cls(date(ano, mes, 1), _fim_periodo(ano, mes, 3))
    
    @classmethod
    def semestre(cls, mes: int) -> "Periodo":
        ano = date.today().year
        return cls(date(ano, mes, 1), _fim_periodo(ano, mes, 6))
    
    @classmethod
    def estacao(cls, nome: str) -> "Periodo":
        return cls.trimestre(INICIO_ESTACAO[nome])
    
    @classmethod
    def dias(cls, dias: int, referencia: Optional[date] = None) -> "Periodo":
        referencia = referencia or date.today()
        return cls(referencia - timedelta(days=dias), referencia)
    
    @classmethod
    def partindo_de(cls, ano=None, mes=None, trimestre=None, semestre=None,
                    estacao=None, dias=None, inicio=None, fim=None) -> "Periodo":
        if ano:
            return cls.ano(ano)
        if mes:
            return cls.mes(mes)
        if trimestre:
            return cls.trimestre(trimestre)
        if semestre:
            return cls.semestre(semestre)
        if estacao:
            return cls.estacao(estacao)
        if dias:
            return cls.dias(dias)
        if inicio or fim:
            return cls(inicio, fim)
        return cls.tudo() 
    
    def __str__(self):
        if self.inicio is None and self.fim is None:
            return "todo o período"
        inicio = str(self.inicio) if self.inicio else "o início"
        fim = str(self.fim) if self.fim else "o fim"
        return f"Começa em {inicio} e vai até {fim}"
