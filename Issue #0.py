import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def historico(html):
    soup = BeautifulSoup(html, 'html.parser')
    base = "https://leagueofcomicgeeks.com"
    
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
            links.append(href)
            
        if len(links) == 20:
            break     
    return links     

def criadores(html):
    soup = BeautifulSoup(html, 'html.parser')
    
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
    
def issue0():
    url = "https://leagueofcomicgeeks.com/profile/valadyne/reading"
    
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
            
            links = historico(aba.content())
            print(f"Foram extraídas {len(links)} edições, passando pra análise")
            
            for indice, edicao in enumerate(links, 1):
                print(f'-' * 50)
                print(f"{indice} de {len(links)} - url: {edicao}")
                
                outraAba = navegador.new_page()
                try:
                    outraAba.goto(edicao, wait_until="domcontentloaded")
                    print("Delay de 3s antes de acessar a edição")
                    outraAba.wait_for_timeout(3000)
                    
                    criadores(outraAba.content())
                except Exception as e:
                    print(f"Paia dms slk: {e}")
                finally:
                    outraAba.close()                            
        except Exception as e:
            print(f"Paia dms: {e}")     
        finally:
            navegador.close()

if __name__ == "__main__":
    issue0()