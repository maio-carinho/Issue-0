import re
from datetime import date
from bs4 import BeautifulSoup

from retrospectiva.config import (
    BASE, PADRAO_ID_EDICAO, PADRAO_ID_SERIE, PADRAO_ID_CRIADOR, PADRAO_ID_PERSONAGEM
)
from retrospectiva.banco.banco import  Serie, Edicao, Criador, Personagem, Leitura

def id_serie(url):
    m = PADRAO_ID_SERIE.search(url)
    return int(m.group(1)) if m else None

def id_edicao(url):
    m = PADRAO_ID_EDICAO.search(url)
    return int(m.group(1)) if m else None

def id_criador(url):
    m = PADRAO_ID_CRIADOR.search(url)
    if not m:
        raise ValueError(f"id de criador não encontrado: {url!r}")
    return int(m.group(1))

def id_personagem(url):
    m = PADRAO_ID_PERSONAGEM.search(url)
    if not m:
        raise ValueError(f"id de personagem não encontrado: {url!r}")
    return int(m.group(1))

def historico(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    user = soup.select_one('.profile-heading a').get_text(strip=True)
    print(f"Usuário: {user}")
    
    resultado = []
    dia = mes = ano = None
    for issue in soup.select('ul.latest-activity-list-grid li.grid-item'):
        if "skeleton" in issue.get("class", []):
            continue
        
        cal = issue.select_one('.calendar-style')
        if cal and "invisible" not in cal.get("class", []):
            dia = issue.select_one('.day').get_text(strip=True)
            mes = issue.select_one('.month').get_text(strip=True)
            ano = issue.select_one('.year').get_text(strip=True)
            
        link = issue.select_one('.title a')
        if not link or dia is None:
            continue
        
        href = link.get('href', '')
        if href.startswith('/'):
            href = BASE + href
        
        edicao_id = id_edicao(href)
        if edicao_id is None:
            continue
        
        resultado.append({
            'id': edicao_id,
            'url': href,
            'dia': dia,
            'mes': mes,
            'ano': ano
        })
        
    return resultado

def montar_data(dia, mes, ano, meses):
    return date(int(ano), meses[mes], int(dia))

def leitura(edicao_id, data):
    return Leitura(edicao_id=edicao_id, data=data)

def edicao(html):
    soup = BeautifulSoup(html, 'html.parser')

    titulo = soup.select_one('.page-details h1').get_text(strip=True)
    busca = re.search(r'(#\d+|Vol\.\s*\d+|HC|TP)', titulo, re.IGNORECASE)
    numero = busca.group(1) if busca else ""

    editora = soup.select_one('.header-intro a').get_text(strip=True)

    paginas = 0
    tag = soup.select_one('.col.copy-small.font-italic').get_text(strip=True)
    if tag:
        busca = re.search(r'(\d+)\s*pages', tag)
        if busca:
            paginas = int(busca.group(1))

    print(f"Número: {numero} | Editora: {editora} | Páginas: {paginas}")
    return Edicao(numero=numero, editora=editora, paginas=paginas)

def criador(html):
    soup = BeautifulSoup(html, 'html.parser')

    criadores = []
    blocos = soup.select('[id^="creators-"], #cover-artists')
    if not blocos:
        print("Seção criadores ausente")
        return criadores

    for bloco in blocos:
        for item in bloco.select('.d-flex.flex-column'):
            tag = item.select_one('.name a')
            nome = tag.get_text(strip=True)
            cargo = item.select_one('.role').get_text(strip=True)
            criador_id = id_criador(tag.get('href', ''))

            print(f'Criador: {nome:<20} | Id: {criador_id}')
            criadores.append((Criador(id=criador_id, nome=nome), cargo))

    return criadores

def personagem(html):
    soup = BeautifulSoup(html, 'html.parser')

    personagens = []
    bloco = soup.select_one('[id^="characters-"]')
    if not bloco:
        print("Seção personagens ausente")
        return personagens

    for item in bloco.select('.name a'):
        nome = item.get_text(strip=True)
        personagem_id = id_personagem(item.get('href', ''))

        print(f'Personagem: {nome:<20} | Id: {personagem_id}')
        personagens.append(Personagem(id=personagem_id, nome=nome))

    return personagens

def serie_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    link = soup.select_one('.series-pagination a:nth-child(2)')
    if not link:
        return None
    
    href = link['href']
    if href.startswith('/'):
        href = BASE + href
    
    return href

def serie(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    serie_id = id_serie(url)
    titulo = soup.select_one('.page-details h1').get_text(strip=True)

    genero = ""
    bloco = soup.find('div', class_='col-lg-2 col-3', string=lambda t: t and 'Genres' in t)
    if bloco:
        genero = bloco.find_next_sibling('div').get_text(strip=True)

    era = ""
    bloco = soup.find('div', class_='col-lg-2 col-3', string=lambda t: t and 'Comic Age' in t)
    if bloco:
        era = bloco.find_next_sibling('div').get_text(strip=True)

    print(f"Título: {titulo} | Id: {serie_id} | Gênero: {genero} | Era: {era}")
    return Serie(id=serie_id, titulo=titulo, era=era, genero=genero)