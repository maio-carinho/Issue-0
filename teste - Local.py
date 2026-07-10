from bs4 import BeautifulSoup

def historico(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    user = soup.select_one('.profile-heading a').get_text()
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

def criadores(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    edicao = soup.select_one('.page-details h1').get_text(strip=True)
    editora = soup.select_one('.header-intro a').get_text(strip=True)
    print(f"{edicao} | Editora: {editora}")
    
    criadores = soup.select_one('[id^="creators-"]')
    blocos = criadores.select('.d-flex.flex-column')    
    for bloco in blocos:
        nome = bloco.select_one('.name a').get_text(strip=True)
        cargo = bloco.select_one('.role').get_text(strip=True)
        
        print(f'{nome:<20} - {cargo}')
    
    characters = soup.select_one('[id^="characters-"]') 
    if characters:
        personagens = characters.select('.name a')
        for personagem in personagens:
            nome = personagem.get_text(strip=True)
            link = personagem.get('href', '')
            
            if "/character/" in link:
                linkID = link.split("/character/")[1].split("/")[0]
            
            print(f'{nome:<20} | Id: {linkID}')  
    else:
        print("Seção personagens ausente")
    
def testeLocal():
    # arquivo = "Absolute Batman #22 Reviews.html"
    arquivo = "Valadyne's Profile _ League of Comic Geeks.html"
    print(f"Lendo arquivo de teste: {arquivo}")
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # criadores(html)
        historico(html)
    except FileNotFoundError:
        print("arquivo nn encontrado, escreve direito")
    
if __name__ == "__main__":
    testeLocal()