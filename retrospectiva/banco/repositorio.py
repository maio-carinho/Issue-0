from retrospectiva.banco.banco import (
    Edicao, Serie, Criador, Personagem, Leitura, EdicaoCriador
)

class Repositorio:
    def __init__(self, sessao):
        self.sessao = sessao
        
    def ids(self):
        return {linha[0] for linha in self.sessao.query(Edicao.id).all()}
    
    def lidar_edicao(self, edicao):
        e = self.sessao.query(Edicao).filter_by(id=edicao.id).first()
        if e:
            return e, False
        self.sessao.add(edicao)
        self.sessao.commit()
        return edicao, True
    
    def lidar_criador(self, criador):
        c = self.sessao.query(Criador).filter_by(id=criador.id).first()
        if c:
            return c, False
        self.sessao.add(criador)
        self.sessao.commit()
        return criador, True
    
    def lidar_personagem(self, personagem):
        p = self.sessao.query(Personagem).filter_by(id=personagem.id).first()
        if p:
            return p, False
        self.sessao.add(personagem)
        self.sessao.commit()
        return personagem, True
    
    def achar_serie(self, serie_id):
        return self.sessao.query(Serie).filter_by(id=serie_id).first()
    
    def lidar_serie(self, serie):
        s = self.achar_serie(serie.id)
        if s:
            return s, False
        self.sessao.add(serie)
        self.sessao.commit()
        return serie, True
    
    def lidar_leitura(self, edicao_id, data_leitura):
        l = self.sessao.query(Leitura).filter_by(edicao_id=edicao_id).first()
        if l:
            return l, False
        leitura = Leitura(edicao_id=edicao_id, data=data_leitura)
        self.sessao.add(leitura)
        self.sessao.commit()
        return leitura, True
    
    def associar_criador(self, edicao_id, criador_id, cargo):
        edc = self.sessao.query(EdicaoCriador).filter_by(
            edicao_id=edicao_id, criador_id=criador_id, cargo=cargo
        ).first()
        if edc:
            return edc, False
        associacao = EdicaoCriador(edicao_id=edicao_id, criador_id=criador_id, cargo=cargo)
        self.sessao.add(associacao)
        self.sessao.commit()
        return associacao, True
    
    def associar_personagem(self, edicao, personagem):
        if personagem not in edicao.personagens:
            edicao.personagens.append(personagem)
            self.sessao.commit()
            return True
        return False
    
    def atualizar_serie(self, edicao, serie_id):
        if edicao.serie_id != serie_id:
            edicao.serie_id = serie_id
            self.sessao.commit()
