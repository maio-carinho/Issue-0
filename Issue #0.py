import os
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from banco import  Leitura, Serie, Edicao, Criador, Personagem, EdicaoCriador, EdicaoPersonagem
from datetime import datetime, date

base = "https://leagueofcomicgeeks.com"
engine = create_engine('sqlite:///banco.db')
Session = sessionmaker(bind=engine)

def historico(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    links = []
    user = soup.select_one('.profile-heading a').get_text(strip=True)
    print(f"Usuário: {user}")
    
    issues = soup.select('ul.latest-activity-list-grid li.grid-item')
    for issue in issues:
        if "skeleton" in issue.get("class", []):
            continue
        
        cal = issue.select_one('.calendar-style')
        if cal and "invisible" not in cal.get("class", []):
            dia = issue.select_one('.day').get_text(strip=True)
            mes = issue.select_one('.month').get_text(strip=True)
            ano = issue.select_one('.year').get_text(strip=True)
            print(f'-' * 50)
            print(f'Data da leitura: {dia} de {mes} de {ano}')
                    
        titulo = issue.select_one('.title a').get_text(strip=True)
        editora = issue.select_one('.date span.font-weight-bold').get_text(strip=True)
        print(f'{titulo} | Editora: {editora}')
        
        link = issue.select_one('.title a')
        if link:
            href = link.get('href', '')
            if href.startswith('/'):
                href = base + href
            links.append({
                'url': href,
                'dia': dia,
                'mes': mes,
                'ano': ano
            })
    return links     

def leitura(edicao, dia, mes, ano):
    leitura = Leitura(
        edicao_id=edicao.id,
        data=date(ano, mes, dia)
    )
    
    return leitura

def edicao(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    paginas = 0    
    numero = soup.select_one('.page-details h1').get_text(strip=True)
    busca = re.search(r'(#\d+|Vol\.\s*\d+)', numero, re.IGNORECASE)
    if busca:
        numero = busca.group(1)
    else:
        numero = "" 
    editora = soup.select_one('.header-intro a').get_text(strip=True)
    pages = soup.select_one('.col.copy-small.font-italic').get_text(strip=True)
    if pages:
        busca = re.search(r'(\d+)\s*pages', pages)
        if busca:
            paginas = int(busca.group(1))
        
    print(f"Número: {numero} | Editora: {editora} | Páginas: {paginas}")
    edicao = Edicao(
        numero = numero,
        editora = editora,
        paginas = paginas
    )
    
    return edicao

def criador(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    print("-" * 50)
    
    criadores = []
    bloco = soup.select_one('[id^="creators-"]')
    if bloco:
        creators = bloco.select('.d-flex.flex-column')    
        for creator in creators:
            tag = creator.select_one('.name a')
            nome = tag.get_text(strip=True)
            cargo = creator.select_one('.role').get_text(strip=True)
            link = tag.get('href', '')
            if "/people/" in link:
                id = int(link.split("/people/")[1].split("/")[0])
            
            print(f'Criador: {nome:<20} | Id: {id}')
            
            criador = Criador(id=id, nome=nome)
            criadores.append((criador, cargo))
        return criadores      
    else:
        print("Seção criadores ausente")
        return criadores
    
def personagem(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    print("-" * 50)
    
    personagens = []
    bloco = soup.select_one('[id^="characters-"]') 
    if bloco:
        characters = bloco.select('.name a')
        for character in characters:
            nome = character.get_text(strip=True)
            link = character.get('href', '')   
            if "/character/" in link:
                id = int(link.split("/character/")[1].split("/")[0])
            
            print(f'Personagem: {nome:<20} | Id: {id}')
            
            personagem = Personagem(id=id, nome=nome)     
            personagens.append(personagem)
        return personagens    
                                    
    else:
        print("Seção personagens ausente")
        return personagens
    
def serie(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    
    href = base + "/comics/series/"
    id = url.split(href)[1].split("/")[0]
    titulo = soup.select_one('.page-details h1').get_text(strip=True)
    
    genero = ""
    era = ""
    
    genres = soup.find('div', class_='col-lg-2 col-3', string=lambda t: t and 'Genres' in t)
    if genres:
        genero = genres.find_next_sibling('div').get_text(strip=True)
            
    comic_age = soup.find('div', class_='col-lg-2 col-3', string=lambda t: t and 'Comic Age' in t)
    if comic_age:
        era = comic_age.find_next_sibling('div').get_text(strip=True)
            
    print(f"Título: {titulo} | Id: {id} | Gênero: {genero} | Era: {era}")
    
    serie = Serie(
        id = id,
        titulo = titulo,
        era = era,
        genero = genero
    )
    
    return serie

def edicao_criador(edicao, criador, cargo):
    edcar = EdicaoCriador(
        edicao_id=edicao.id,
        criador_id=criador.id,
        cargo = cargo
    )
    
    return edcar

def issue0():
    url = "https://leagueofcomicgeeks.com/profile/valadyne/reading"
    sessao = Session()
    
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
                    url = base + "/comic/"
                    ed_obj.id = int(issue.split(url)[1].split("/")[0])
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
    issue0()