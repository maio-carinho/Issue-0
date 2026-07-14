import os
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from banco import *
from tools import *

base = "https://leagueofcomicgeeks.com"
url = "https://leagueofcomicgeeks.com/profile/valadyne/reading"
sessao = Session()

def scraper():
    perfil = os.path.join(os.getcwd(), "perfil")
    with sync_playwright() as p:
        print(f"Iniciando o Playwright")
        navegador = p.chromium.launch_persistent_context(
            perfil,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            no_viewport=True
        )
        
        aba = navegador.pages[0] if navegador.pages else navegador.new_page()
        try:
            aba.goto(url)
            print("Delay de 10s antes de acessar o site")
            aba.wait_for_timeout(10000)            
            
            tamanho = aba.evaluate("document.body.scrollHeight")
            while True:
                aba.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                aba.wait_for_timeout(2000)
                altura = aba.evaluate("document.body.scrollHeight")
                if altura == tamanho:
                    break
                tamanho = altura
                
            links = historico(aba.content())
            print(f"Foram extraídas {len(links)} edições, passando pra análise")
            
            meses = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                          'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
            for indice, issues in enumerate(links, 1):
                issue = issues['url']
                
                print(f'-' * 50)
                print(f"{indice} de {len(links)} - url: {issue}")
                
                outraAba = navegador.new_page()
                try:
                    outraAba.goto(issue, wait_until="domcontentloaded")
                    print("Delay de 3s antes de acessar a edição")
                    outraAba.wait_for_timeout(3000)
                    atual = outraAba.content()
                    
                    ed_obj = edicao(atual)
                    ed_url = base + "/comic/"
                    ed_obj.id = int(issue.split(ed_url)[1].split("/")[0])
                    e = sessao.query(Edicao).filter_by(id=ed_obj.id).first()
                    if not e:
                        sessao.add(ed_obj)
                        sessao.commit()
                        e = ed_obj
                    
                    dia = int(issues['dia'])
                    mes = meses.get(issues['mes'])
                    ano = int(issues['ano'])
                    
                    data = leitura(e, dia, mes, ano)
                    d = sessao.query(Leitura).filter_by(edicao_id=e.id).first()
                    if not d:
                        sessao.add(data)
                        sessao.commit()
                    
                    criadores = criador(atual)
                    for cri_obj, cargo in criadores:
                        c = sessao.query(Criador).filter_by(id=cri_obj.id).first()
                        if not c:
                            sessao.add(cri_obj)
                            sessao.commit()
                            c = cri_obj
                        
                        edcar = edicao_criador(e, c, cargo)    
                        ec = sessao.query(EdicaoCriador).filter_by(
                            edicao_id=e.id,
                            criador_id=c.id,
                            cargo=edcar.cargo
                        ).first()
                        if not ec:
                            sessao.add(edcar)
                            sessao.commit()
                    
                    personagens = personagem(atual)
                    for per_obj in personagens:
                        p = sessao.query(Personagem).filter_by(id=per_obj.id).first()
                        if not p:
                            sessao.add(per_obj)
                            sessao.commit()
                            p = per_obj
                            
                        if p not in e.personagens:
                            e.personagens.append(p)
                            sessao.commit()
                    
                    soup = BeautifulSoup(atual, 'html.parser')
                    link = soup.select_one('.series-pagination a:nth-child(2)')
                    href = link['href']
                    if href.startswith('/'):
                            href = base + href
                            
                    busca = re.search(r'/series/(\d+)', href)
                    if busca:
                        busca_serie = int(busca.group(1))
                        s = sessao.query(Serie).filter_by(id=busca_serie).first()
                        if s:
                            print(f"Série {s.titulo} de Id {s.id} já foi analisada")
                            if e.serie_id != s.id:
                                e.serie_id = s.id
                                sessao.commit()
                        else:
                            try:                     
                                maisAba = navegador.new_page()
                                print(f"Acessando página da série: {href}")
                            
                                maisAba.goto(href, wait_until="domcontentloaded")
                                print("Delay de 3s na série")
                                maisAba.wait_for_timeout(3000)
                                
                                ser_obj = serie(maisAba.content(), href)
                                s = sessao.query(Serie).filter_by(id=ser_obj.id).first()
                                if not s:
                                    sessao.add(ser_obj)
                                    sessao.commit()
                                    s = ser_obj
                                    
                                if e.serie_id != s.id:
                                    e.serie_id = s.id
                                    sessao.commit() 
                                
                            except Exception as erro:
                                print(f"AINDA MAIS PAIA MDS: {erro}")
                            finally:
                                maisAba.close()
                        
                except Exception as erro:
                    print(f"Paia dms slk: {erro}")
                finally:
                    outraAba.close()   
                                             
        except Exception as erro:
            print(f"Paia dms: {erro}")     
        finally:
            navegador.close()

if __name__ == "__main__":
    scraper()