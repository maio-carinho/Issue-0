from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

base = declarative_base()

EdicaoPersonagem = Table(
    'edicao_personagem',
    base.metadata,
    Column('edicao_id', Integer, ForeignKey('edicoes.id'), primary_key=True),
    Column('personagem_id', Integer, ForeignKey('personagens.id'), primary_key=True)
)

class EdicaoCriador(base):
    __tablename__ = 'edicao_criador'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    edicao_id = Column(Integer, ForeignKey('edicoes.id'))
    criador_id = Column(Integer, ForeignKey('criadores.id'))
    cargo = Column(String)

class Serie(base):
    __tablename__ = 'series'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    era = Column(String, nullable=True)
    genero = Column(String, nullable=True)

class Edicao(base):
    __tablename__ = 'edicoes'
    
    id = Column(Integer, primary_key=True)
    serie_id = Column(Integer, ForeignKey('series.id'))
    numero = Column(String)
    editora = Column(String)
    paginas = Column(Integer, nullable=True)
    
    personagens = relationship("Personagem", secondary=EdicaoPersonagem, backref="edicoes")

class Criador(base):
    __tablename__ = 'criadores'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)

class Personagem(base):
    __tablename__ = 'personagens'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)

class Leitura(base):
    __tablename__ = 'leituras'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    edicao_id = Column(Integer, ForeignKey('edicoes.id'))
    data = Column(Date)    
    
def criar():
    engine = create_engine('sqlite:///banco.db', echo=True)
    base.metadata.create_all(engine)

if __name__ == "__main__":
    criar()    