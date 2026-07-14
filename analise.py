import pandas as pd
import sqlite3

from banco import *
from datetime import timedelta

sessao = Session()

crias_fav = sessao.query(
    Criador.nome.label('criador'),
    EdicaoCriador.cargo
).join(Criador, EdicaoCriador.criador_id == Criador.id)
df_crias = pd.read_sql(crias_fav.statement, engine)
df_limpo = df_crias.dropna(subset=['cargo', 'criador'])
df_crias = df_limpo.assign(
    cargo=df_limpo['cargo'].str.split(r',\s*')
).explode('cargo')
print(df_crias.head())
print("")

chars_fav = sessao.query(
    Edicao.numero,
    Personagem.nome.label('personagem')
).join(EdicaoPersonagem, Edicao.id == EdicaoPersonagem.c.edicao_id
).outerjoin(Personagem, EdicaoPersonagem.c.personagem_id == Personagem.id)
df_chars = pd.read_sql(chars_fav.statement, engine)
print(df_chars.head())
print("")

tipos_fav = sessao.query(
    Edicao.editora,
    Serie.era,
    Serie.genero
).join(Edicao, Edicao.serie_id == Serie.id)
df_tipos = pd.read_sql(tipos_fav.statement, engine)
df_tipos = df_tipos.dropna()
print(df_tipos.head())
print("")

datas_seq = sessao.query(Leitura.data).distinct().order_by(Leitura.data).all()

num = sessao.query(
    Leitura.id,
    Edicao.paginas
).join(Leitura, Edicao.id == Leitura.edicao_id)
df_num = pd.read_sql(num.statement, engine)
print(df_num.head())

sessao.close()

def roteirista_fav():
    roteiristas = df_crias[df_crias['cargo'] == 'Writer']
    roteiristas = roteiristas['criador'].value_counts()
    print(roteiristas.head(5))
    print("")

def artista_fav():
    artistas = df_crias[df_crias['cargo'] == 'Artist']
    artistas = artistas['criador'].value_counts()
    print(artistas.head(5))
    print("")
    
def colorista_fav():
    coloristas = df_crias[df_crias['cargo'] == 'Colorist']
    coloristas = coloristas['criador'].value_counts()
    print(coloristas.head(5))
    print("")
    
def capista_fav():
    print("")
        
def criador_fav():
    criadores = df_crias['criador'].value_counts()
    print(criadores.head(10))
    print("")
    
def personagem_fav():
    personagens = df_chars['personagem'].value_counts()
    print(personagens.head(10))
    print("")
    
def editora_fav():
    editoras = df_tipos['editora'].value_counts()
    print(editoras.head(5))
    print("")
    
def era_fav():
    eras = df_tipos['era'].value_counts()
    print(eras.head(5))
    print("")
    
def genero_fav():
    explode = df_tipos['genero'].str.split(r',\s*').explode()
    generos = explode.value_counts()
    print(generos.head(5))
    print("")
    
def maior_sequencia():
    datas = [linha[0] for linha in datas_seq]
    
    maior_seq = 1
    atual_seq = 1
    
    for i in range(1, len(datas)):
        delta = datas[i] - datas[i-1]
        if delta == timedelta(days=1):
            atual_seq += 1
            if atual_seq > maior_seq:
                maior_seq = atual_seq
        else:
            atual_seq = 1
    
    print(f"A maior sequência de leitura foi: {maior_seq} dias")
    print(f"A sequência atual é de: {atual_seq} dias")
    print("")

def maior_ressaca():
    datas = [linha[0] for linha in datas_seq]
    
    maior_res = timedelta(days=0)
    
    for i in range(1, len(datas)):
        delta = datas[i] - datas[i-1]
        if delta > maior_res:
            maior_res = delta
    
    print(f"A maior ressaca literária foi de: {maior_res.days} dias")
    print("")
    
def melhor_mes():
    print("")
    
def numeros():
    edicoes = len(df_num)
    paginas = int(df_num['paginas'].sum ())
    print(f"Foram lidas: {edicoes} edições")
    print(f"Totalizando {paginas} páginas lidas")
    print("")

def analise():
    roteirista_fav()
    artista_fav()
    colorista_fav()
    criador_fav()
    personagem_fav()
    editora_fav()
    era_fav()
    genero_fav()
    maior_sequencia()
    maior_ressaca()
    melhor_mes()
    numeros()
    
if __name__ == "__main__":
    analise()