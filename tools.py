import re
from bs4 import BeautifulSoup

from banco import *
from datetime import date

base = "https://leagueofcomicgeeks.com"
sessao = Session()

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
                        
        link = issue.select_one('.title a')
        if link:
            href = link.get('href', '')
            if href.startswith('/'):
                href = base + href
            busca = re.search(r'/comic(?:s)?/(\d+)', href)
            if busca:
                e_id = int(busca.group(1))
                e = sessao.query(Edicao).filter_by(id=e_id).first()
                if not e:
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
    busca = re.search(r'(#\d+|Vol\.\s*\d+|HC|TP)', numero, re.IGNORECASE)
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