from retrospectiva.config import (
    URL_PERFIL, MESES, DELAY_INICIO, DELAY_SCROLL, DELAY_PAGINA
)
from retrospectiva.banco.sessao import nova_sessao
from retrospectiva.banco.repositorio import Repositorio
from retrospectiva.scraping.navegador import abrir_navegador, abrir_aba
from retrospectiva.scraping import tools

def scraper(limite=None):
    with nova_sessao() as sessao:
        repo = Repositorio(sessao)
        with abrir_navegador() as navegador:
            aba = navegador.pages[0] if navegador.pages else navegador.new_page()
            aba.goto(URL_PERFIL)
            print("Delay de 10s antes de acessar o site")
            aba.wait_for_timeout(DELAY_INICIO)
            scroll(aba)
            
            todos = tools.historico(aba.content())
            ids = repo.ids()
            links = [item for item in todos if item['id'] not in ids]
            if limite is not None:
                links = links[:limite]
            print(f"Foram extraídas {len(links)} edições novas, passando pra análise")
            
            for indice, issue in enumerate(links, 1):
                print('-' * 50)
                print(f"{indice} de {len(links)} - url: {issue['url']}")
                processar_edicao(navegador, repo, issue)
            
def scroll(aba):
    tamanho = aba.evaluate("document.body.scrollHeight")
    while True:
        aba.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        aba.wait_for_timeout(DELAY_SCROLL)
        altura = aba.evaluate("document.body.scrollHeight")
        if altura == tamanho:
            break
        tamanho = altura

def processar_edicao(navegador, repo, issue):
    try:
        with abrir_aba(navegador) as aba:
            aba.goto(issue['url'], wait_until="domcontentloaded")
            aba.wait_for_timeout(DELAY_PAGINA)
            html = aba.content()
            
            nova_edicao = tools.edicao(html)
            nova_edicao.id = issue['id']
            edicao, _ = repo.lidar_edicao(nova_edicao)
            
            data = tools.montar_data(issue['dia'], issue['mes'], issue['ano'], MESES)
            repo.lidar_leitura(edicao.id, data)
            
            for novo_criador, cargo in tools.criador(html):
                criador, _ = repo.lidar_criador(novo_criador)
                repo.associar_criador(edicao.id, criador.id, cargo)
                
            for novo_personagem in tools.personagem(html):
                personagem, _ = repo.lidar_personagem(novo_personagem)
                repo.associar_personagem(edicao, personagem)
                
            processar_serie(navegador, repo, edicao, html)       
    
    except Exception as erro:
        print(f"Falha ao processar a edição {issue['url']}: {erro}")

def processar_serie(navegador, repo, edicao, html):
    href = tools.serie_link(html)
    if not href:
        return
    
    serie_id = tools.id_serie(href)
    if serie_id is None:
        return
    
    serie = repo.achar_serie(serie_id)
    if serie:
        print(f"Série {serie.titulo} de Id {serie.id} já foi analisada")
        repo.atualizar_serie(edicao, serie.id)
        return
    
    try:
        with abrir_aba(navegador) as aba:
            print(f"Acessando página da série: {href}")
            aba.goto(href, wait_until="domcontentloaded")
            aba.wait_for_timeout(DELAY_PAGINA)
            
            nova_serie = tools.serie(aba.content(), href)
            serie, _ = repo.lidar_serie(nova_serie)
            repo.atualizar_serie(edicao, serie.id)
    
    except Exception as erro:
        print(f"Falha ao processar a série {href}: {erro}")

if __name__ == "__main__":
    scraper()
