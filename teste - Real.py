import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def historico(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
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
    except AttributeError:
        print("Erro: URL errada")

def criadores(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        edicao = soup.select_one('.page-details h1').get_text(strip=True)
        editora = soup.select_one('.header-intro a').get_text(strip=True)
        print(f"{edicao} | Editora: {editora}")
        print("-" * 50)
        
        criadores = soup.select_one('[id^="creators-"]')
        blocos = criadores.select('.d-flex.flex-column')    
        for bloco in blocos:
            nome = bloco.select_one('.name a').get_text(strip=True)
            cargo = bloco.select_one('.role').get_text(strip=True)
            
            print(f'{nome:<20} - {cargo}')
        
        print("-" * 50)
        
        characters = soup.select_one('[id^="characters-"]') 
        if characters:
            personagens = characters.select('.name a')
            for personagem in personagens:
                nome = personagem.get_text(strip=True)
                link = personagem.get('href', '')
                
                linkID = "Desconhecido"
                if "/character/" in link:
                    linkID = link.split("/character/")[1].split("/")[0]
                
                print(f'{nome:<20} | Id: {linkID}')  
        else:
            print("Seção personagens ausente")
            
    except AttributeError:
         print("Erro: URL errada")

def generoera(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        genero = ""
        era = ""
        
        genres = soup.find('div', class_='col-lg-2 col-3', string=lambda t: t and 'Genres' in t)
        if genres:
            genero = genres.find_next_sibling('div').get_text(strip=True)
                
        comic_age = soup.find('div', class_='col-lg-2 col-3', string=lambda t: t and 'Comic Age' in t)
        if comic_age:
            era = comic_age.find_next_sibling('div').get_text(strip=True)
                
        print(f"Gênero: {genero} | Era: {era}")
    
    except AttributeError:
         print("Erro: URL errada")
    
def testeWeb():
    # url = "https://leagueofcomicgeeks.com/profile/valadyne/reading"
    # url = "https://leagueofcomicgeeks.com/comic/6863939/absolute-batman-22"
    url = "https://leagueofcomicgeeks.com/comics/series/178012/absolute-batman"
    print(f"Iniciando Playwright para acessar: {url}")
    
    perfil = os.path.join(os.getcwd(), "perfil")
    html = ""
    with sync_playwright() as p:
        navegador = p.chromium.launch_persistent_context(
            perfil,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            no_viewport=True
        )
        
        aba = navegador.pages[0] if navegador.pages else navegador.new_page()
        try:
            aba.goto(url)
            aba.wait_for_timeout(10000)
            
            tamanho = aba.evaluate("document.body.scrollHeight")
            while True:
                aba.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                aba.wait_for_timeout(2000)
                altura = aba.evaluate("document.body.scrollHeight")
                
                if altura == tamanho:
                    break
                
                tamanho = altura
            
            html = aba.content()
        
        except Exception as e:
            print(f"Paia dms: {e}")
        
        finally:
            navegador.close()
    
    if html:
        # historico(html)
        # criadores(html)
        generoera(html)

if __name__ == "__main__":
    testeWeb()