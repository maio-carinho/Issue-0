import pandas as pd

from retrospectiva.banco.banco import (
    Edicao, EdicaoCriador, Criador, EdicaoPersonagem, Personagem, Serie, Leitura
)

class Repositorio:
    def __init__(self, sessao, periodo):
        self.sessao = sessao
        self.periodo = periodo
        
    def filtrar_data(self, query, data):
        if self.periodo.inicio:
            query = query.filter(data >= self.periodo.inicio)
        if self.periodo.fim:
            query = query.filter(data <= self.periodo.fim)
        
        return query 
    
    def datas(self) -> list:
        query = self.sessao.query(Leitura.data).distinct().order_by(Leitura.data)
        query = self.filtrar_data(query, Leitura.data)
        
        return [linha[0] for linha in query.all()]
    
    def edicoes_periodo(self):
        query = self.sessao.query(Leitura.edicao_id).distinct()
        
        return self.filtrar_data(query, Leitura.data).scalar_subquery()
    
    def leituras_periodo(self) -> pd.DataFrame:
        query = self.sessao.query(
            Leitura.id,
            Leitura.data,
            Edicao.paginas
        ).join(Edicao, Edicao.id == Leitura.edicao_id)
        
        query = self.filtrar_data(query, Leitura.data)
        return pd.read_sql(query.statement, self.sessao.get_bind())
    
    def criadores_periodo(self) -> pd.DataFrame:
        subquery = self.edicoes_periodo()
        query = self.sessao.query(
            EdicaoCriador.edicao_id,
            Criador.nome.label('criador'),
            EdicaoCriador.cargo
        ).join(Criador, EdicaoCriador.criador_id == Criador.id
        ).filter(EdicaoCriador.edicao_id.in_(subquery))
        
        df_cria = pd.read_sql(query.statement, self.sessao.get_bind())
        return df_cria.assign(cargo=df_cria['cargo'].str.split(r',\s*')).explode('cargo')
    
    def personagens_periodo(self) -> pd.DataFrame:
        subquery = self.edicoes_periodo()
        query = self.sessao.query(
            Edicao.id.label('edicao_id'),
            Personagem.nome.label('personagem')
        ).join(EdicaoPersonagem, Edicao.id == EdicaoPersonagem.c.edicao_id
        ).outerjoin(Personagem, EdicaoPersonagem.c.personagem_id == Personagem.id
        ).filter(Edicao.id.in_(subquery))
        
        return pd.read_sql(query.statement, self.sessao.get_bind())
    
    def classificacao_periodo(self) -> pd.DataFrame:
        subquery = self.edicoes_periodo()
        query = self.sessao.query(
            Edicao.editora,
            Serie.era,
            Serie.genero
        ).join(Serie, Edicao.serie_id == Serie.id
        ).filter(Edicao.id.in_(subquery))
        
        df_tipos = pd.read_sql(query.statement, self.sessao.get_bind())
        df_tipos = df_tipos.replace('', pd.NA)
        return df_tipos.dropna()
