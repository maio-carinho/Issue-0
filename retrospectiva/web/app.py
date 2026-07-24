from datetime import date
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from retrospectiva.banco.sessao import nova_sessao
from retrospectiva.analise.periodo import Periodo
from retrospectiva.analise.analise import Analise

app = FastAPI()
templates = Jinja2Templates(directory="retrospectiva/web/templates")

def _inteiro(texto: str):
    return int(texto) if texto else None

def _data(texto: str):
    return date.fromisoformat(texto) if texto else None

def _preenchidos(ano, mes, trimestre, semestre, dias, inicio, fim):
    tipos = [ano, mes, trimestre, semestre, dias]
    total = sum(1 for campo in tipos if campo is not None)
    if inicio is not None or fim is not None:
        total += 1
    return total

@app.get("/", response_class=HTMLResponse)
def pagina_inicial(
        request: Request,
        ano: str = "",
        mes: str = "",
        trimestre: str = "",
        semestre: str = "",
        dias: str = "",
        inicio: str = "",
        fim: str = ""
    ):
    
    hano=_inteiro(ano)
    hmes=_inteiro(mes)
    htrimestre=_inteiro(trimestre)
    hsemestre=_inteiro(semestre)
    hdias=_inteiro(dias)
    hinicio=_data(inicio)
    hfim=_data(fim)
    
    if _preenchidos(hano, hmes, htrimestre, hsemestre, hdias, hinicio, hfim) > 1:
        contexto = {"erro": "Preencha um tipo de filtro por vez"}
        return templates.TemplateResponse(request, "index.html" , contexto)
    
    periodo = Periodo.partindo_de(
        ano=hano,
        mes=hmes,
        trimestre=htrimestre,
        semestre=hsemestre,
        dias=hdias,
        inicio=hinicio,
        fim=hfim
    )
    
    with nova_sessao() as sessao:
        analise = Analise(sessao, periodo)
        
        contexto={
            "request": request,
            "periodo": str(analise.periodo),
            "roteiristas": analise.roteirista_favorito(),
            "artistas": analise.artista_favorito(),
            "editoras": analise.editora_favorito(),
            "numeros": analise.numeros()
        }
        
        return templates.TemplateResponse(request, "index.html", contexto)
