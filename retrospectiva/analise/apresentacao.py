from datetime import date

from retrospectiva.analise.analise import Analise

esse_ano = date.today().year

def imprimir_relatorio(analisador: Analise):
    print(f"Retrospectiva - {analisador.periodo}")
    print("-" * 50)
    
    imprimir_top("Roteirista mais lido", analisador.roteirista_favorito())
    imprimir_top("Artista mais lido", analisador.artista_favorito())
    imprimir_top("Colorista mais lido", analisador.colorista_favorito())
    imprimir_top("Capista favorito", analisador.capista_favorito())
    imprimir_top("Criador favorito", analisador.criador_favorito())
    imprimir_top("Personagem mais lido", analisador.personagem_favorito())
    imprimir_top("Editora mais lido", analisador.editora_favorito())
    imprimir_top("Era mais lido", analisador.era_favorito())
    imprimir_top("Gênero mais lido", analisador.genero_favorito())
    
    maior_seq, atual_seq = analisador.maior_sequencia()
    print(f"\nMaior sequência de leitura: {maior_seq} dias (sequência atual: {atual_seq} dias)")
    
    ressaca = analisador.maior_ressaca()
    print(f"Maior ressaca literária: {ressaca.days} dias")
    
    melhor_mes = analisador.melhor_mes()
    if melhor_mes:
        mes, total = melhor_mes
        print(f"Melhor mês: {mes:02d}/{esse_ano} ({total} edições lidas)")
        
    edicoes, paginas = analisador.numeros()
    print(f"\nForam lidas {edicoes} edições, totalizando {paginas} páginas lidas")
    
def imprimir_top(topico, df, top=5):
    print(f"\n{topico}:")
    if df.empty:
        print("Sem dados nesse período")
        return
    
    for nome, contagem in df.head(top).items():
        print(f"   {nome}: {contagem}")