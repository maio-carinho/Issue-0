import pandas as pd
from datetime import date, timedelta

from retrospectiva.analise.periodo import Periodo
from retrospectiva.analise.repositorio import Repositorio

class analise:
    def __init__(self, sessao, periodo: Periodo = None):
        self.periodo = periodo or Periodo.tudo()
        self.repo = Repositorio(sessao, self.periodo)
        
        self._df_datas = None
        self._df_leituras = None
        self._df_criadores = None
        self._df_personagens = None
        self._df_classificacao = None
        
    @property
    def df_datas(self):
        if self._df_datas is None:
            self._df_datas = self.repo.datas()
        return self._df_datas
    
    @property
    def df_leituras(self):
        if self._df_leituras is None:
            self._df_leituras = self.repo.leituras_periodo()
        return self._df_leituras
    
    @property
    def df_criadores(self):
        if self._df_criadores is None:
            self._df_criadores = self.repo.criadores_periodo()
        return self._df_criadores
    
    @property
    def df_personagens(self):
        if self._df_personagens is None:
            self._df_personagens = self.repo.personagens_periodo()
        return self._df_personagens
    
    @property
    def df_classificacao(self):
        if self._df_classificacao is None:
            self._df_classificacao = self.repo.classificacao_periodo()
        return self._df_classificacao
    
    def cargos(self):
        return sorted(self.df_criadores['cargo'].unique())
    
    def top_cargo(self, cargo, top=5):
        cargos = [cargo] if isinstance(cargo, str) else cargo
        criadores = self.df_criadores[self.df_criadores['cargo'].isin(cargos)]
        return criadores['criador'].value_counts().head(top)
    
    def roteirista_favorito(self, top=5):
        return self.top_cargo('Writer', top)
        
    def artista_favorito(self, top=5):
        return self.top_cargo('Artist', top)
        
    def colorista_favorito(self, top=5):
        return self.top_cargo('Colorist', top)
        
    def capista_favorito(self, top=5):
        return self.top_cargo(['Cover Artist', 'Cover Penciller'], top)
        
    def criador_favorito(self, top=10):
        criadores = self.df_criadores.drop_duplicates(subset=['edicao_id', 'criador'])
        return criadores['criador'].value_counts().head(top)
        
    def personagem_favorito(self, top=10):
        return self.df_personagens['personagem'].value_counts().head(top)
        
    def editora_favorito(self, top=5):
        return self.df_classificacao['editora'].value_counts().head(top)
        
    def era_favorito(self, top=5):
        return self.df_classificacao['era'].value_counts().head(top)
        
    def genero_favorito(self, top=5):
        explodido = self.df_classificacao['genero'].str.split(r',\s*').explode()
        return explodido.value_counts().head(top)
    
    def maior_sequencia(self):
        datas = self.df_datas
        if not datas:
            return 0, 0
        
        maior_seq = atual_seq = 1
        for i in range(1, len(datas)):
            if datas[i] - datas[i - 1] == timedelta(days=1):
                atual_seq += 1
                maior_seq = max(maior_seq, atual_seq)
            else:
                atual_seq = 1
                
        return maior_seq, atual_seq
        
    def maior_ressaca(self):
        datas = self.df_datas
        maior = timedelta(days=0)
        for i in range(1, len(datas)):
            maior = max(maior, datas[i] - datas[i - 1])
            
        if datas:
            fim = min(self.periodo.fim, date.today()) if self.periodo.fim else date.today()
            maior = max(maior, fim - datas[-1])
            
            if self.periodo.inicio:
                maior = max(maior, datas[0] - self.periodo.inicio)
        
        return maior
    
    def melhor_mes(self):
        if self.df_leituras.empty:
            return None
        
        datas = pd.to_datetime(self.df_leituras['data'])
        conta = datas.dt.to_period('M').value_counts()
        periodo = conta.index[0]
        return periodo.month, int(conta.iloc[0]) 
        
    def numeros(self):
        edicoes = len(self.df_leituras)
        paginas = int(self.df_leituras['paginas'].sum())
        return edicoes, paginas