from datetime import date
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from retrospectiva.banco.sessao import nova_sessao
from retrospectiva.analise.periodo import Periodo
from retrospectiva.analise.analise import Analise
from retrospectiva.web.textos import NOMES_MES, NOMES_ESTACAO, INICIO_SEMESTRE

app = FastAPI()
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
    
    hano=_inteiro(ano)
    hmes=_inteiro(mes)
    htrimestre=_inteiro(trimestre)
    hsemestre=_inteiro(semestre)
    hestacao = _estacao(estacao)
    hdias=_inteiro(dias)
    hinicio=_data(inicio)
    hfim=_data(fim)

    ano_atual = date.today().year
    
    if _preenchidos(hano, hmes, htrimestre, hsemestre, hestacao, hdias, hinicio, hfim) > 1:
        contexto = {"request": request, "erro": "Preencha um tipo de filtro por vez", "ano_atual": ano_atual}
        return templates.TemplateResponse(request, "index.html" , contexto)
    
    algo_preenchido = _preenchidos(hano, hmes, htrimestre, hsemestre,
                                   hestacao, hdias, hinicio, hfim) == 1
    
    if algo_preenchido and confirmado != "1":
        mensagem = _mensagem(hano, hmes, htrimestre, hsemestre,
                             hestacao, hdias, hinicio, hfim)
        contexto = {
            "request": request,
            "confirmacao": mensagem,
            "ano_atual": ano_atual,
            "params": {
                "ano": ano, "mes": mes, "trimestre": trimestre, "semestre": semestre,
                "estacao": estacao, "dias": dias, "inicio": inicio, "fim": fim,
            }
        }
        return templates.TemplateResponse(request, "index.html", contexto)
    
    hsemestre_inicio = INICIO_SEMESTRE.get(hsemestre) if (hsemestre) else None
    
    periodo = Periodo.partindo_de(
        ano=hano, mes=hmes, trimestre=htrimestre, semestre=hsemestre_inicio,
        estacao=hestacao, dias=hdias, inicio=hinicio, fim=hfim
    )
    
    with nova_sessao() as sessao:
        analise = Analise(sessao, periodo)
        
        contexto = {
            "request": request,
            "periodo": str(analise.periodo),
            "roteiristas": analise.roteirista_favorito(),
            "artistas": analise.artista_favorito(),
            "editoras": analise.editora_favorito(),
            "numeros": analise.numeros()
        }
        
        return templates.TemplateResponse(request, "index.html", contexto)
