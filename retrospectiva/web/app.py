from datetime import date
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from retrospectiva.banco.sessao import nova_sessao
from retrospectiva.analise.periodo import Periodo
from retrospectiva.analise.analise import Analise
from retrospectiva.web.textos import NOMES_MES, NOMES_ESTACAO, INICIO_SEMESTRE

app = FastAPI()
app.mount("/static", StaticFiles(directory="retrospectiva/web/static"), name="static")
templates = Jinja2Templates(directory="retrospectiva/web/templates")

def _inteiro(texto: str):
    return int(texto) if texto else None

def _data(texto: str):
    return date.fromisoformat(texto) if texto else None

def _estacao(texto: str):
    return texto or None

def _preenchidos(ano, mes, trimestre, semestre, estacao, dias, inicio, fim):
    tipos = [ano, mes, trimestre, semestre, estacao, dias]
    total = sum(1 for campo in tipos if campo is not None)
    if inicio is not None or fim is not None:
        total += 1
    return total

def _mensagem(ano, mes, trimestre, semestre, estacao, dias, inicio, fim):
    if ano:
        return f"Você deseja analisar o ano de {ano}?"
    if mes:
        return f"Você deseja analisar o mês de {NOMES_MES[mes]}?"
    if trimestre:
        return f"Você deseja analisar um trimestre partindo de {NOMES_MES[trimestre]}?"
    if semestre:
        return f"Você deseja analisar o {semestre}° semestre?"
    if estacao:
        return f"Você deseja analisar o {NOMES_ESTACAO[estacao]}?"
    if dias:
        return f"Você deseja analisar {dias} dias?"
    if inicio or fim:
        return f"Você deseja analisar do dia {inicio} até o dia {fim}?"
    return None

def _parametros(ano, mes, trimestre, semestre, estacao, dias, inicio, fim):
    return {
        "ano": _inteiro(ano),
        "mes": _inteiro(mes),
        "trimestre": _inteiro(trimestre),
        "semestre": _inteiro(semestre),
        "estacao": _estacao(estacao),
        "dias": _inteiro(dias),
        "inicio": _data(inicio),
        "fim": _data(fim)
    }

@app.get("/", response_class=HTMLResponse)
def pagina_inicial(
        request: Request,
        ano: str = "",
        mes: str = "",
        trimestre: str = "",
        semestre: str = "",
        estacao: str = "",
        dias: str = "",
        inicio: str = "",
        fim: str = "",
        confirmado: str = ""
    ):
    
    valores = _parametros(ano, mes, trimestre, semestre, estacao, dias, inicio, fim)
    algo_preenchido = _preenchidos(**valores)
    
    contexto = {"request": request, "ano_atual": date.today().year}
    
    if algo_preenchido > 1:
        contexto["erro"] = "Só preencha um filtro por vez"
    elif algo_preenchido == 1:
        contexto["confirmacao"] = _mensagem(**valores)
        contexto["params"] = {
            "ano": ano, "mes": mes, "trimestre": trimestre, "semestre": semestre,
            "estacao": estacao, "dias": dias, "inicio": inicio, "fim": fim
        }

    return templates.TemplateResponse(request, "index.html", contexto)

@app.get("/resultado", response_class=HTMLResponse)    
def pagina_resultado(
    request: Request,
    ano: str = "",
    mes: str = "",
    trimestre: str = "",
    semestre: str = "",
    estacao: str = "",
    dias: str = "",
    inicio: str = "",
    fim: str = "",
):
    valores = _parametros(ano, mes, trimestre, semestre, estacao, dias, inicio, fim)
 
    if _preenchidos(**valores) > 1:
        return RedirectResponse(url="/")
 
    hsemestre = valores.pop("semestre")
    hsemestre_mes = INICIO_SEMESTRE.get(hsemestre) if hsemestre else None
    
    periodo = Periodo.partindo_de(semestre=hsemestre_mes, **valores)
    
    with nova_sessao() as sessao:
        analise = Analise(sessao, periodo)
 
        contexto = {
            "request": request,
            "periodo": str(analise.periodo),
            "roteiristas": analise.roteirista_favorito(),
            "artistas": analise.artista_favorito(),
            "editoras": analise.editora_favorito(),
            "numeros": analise.numeros(),
        }
        
        return templates.TemplateResponse(request, "resultado.html", contexto)