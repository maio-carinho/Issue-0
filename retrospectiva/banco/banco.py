from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

EdicaoPersonagem = Table(
    'edicao_personagem',
    Base.metadata,
    Column('edicao_id', Integer, ForeignKey('edicoes.id'), primary_key=True),
    Column('personagem_id', Integer, ForeignKey('personagens.id'), primary_key=True),
)

class Serie(Base):
    __tablename__ = 'series'

    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    era = Column(String, nullable=True)
    genero = Column(String, nullable=True)

    edicoes = relationship('Edicao', back_populates='serie')

    def __repr__(self):
        return f"<Serie id={self.id} titulo={self.titulo!r}>"

class Edicao(Base):
    __tablename__ = 'edicoes'

    id = Column(Integer, primary_key=True)
    serie_id = Column(Integer, ForeignKey('series.id'))
    numero = Column(String)
    editora = Column(String)
    paginas = Column(Integer, nullable=True)

    serie = relationship('Serie', back_populates='edicoes')
    personagens = relationship('Personagem', secondary=EdicaoPersonagem, backref='edicoes')
    leituras = relationship('Leitura', back_populates='edicao')

    def __repr__(self):
        return f"<Edicao id={self.id} numero={self.numero!r} editora={self.editora!r}>"

class Criador(Base):
    __tablename__ = 'criadores'

    id = Column(Integer, primary_key=True)
    nome = Column(String)

    def __repr__(self):
        return f"<Criador id={self.id} nome={self.nome!r}>"

class Personagem(Base):
    __tablename__ = 'personagens'

    id = Column(Integer, primary_key=True)
    nome = Column(String)

    def __repr__(self):
        return f"<Personagem id={self.id} nome={self.nome!r}>"

class EdicaoCriador(Base):
    __tablename__ = 'edicao_criador'

    id = Column(Integer, primary_key=True, autoincrement=True)
    edicao_id = Column(Integer, ForeignKey('edicoes.id'))
    criador_id = Column(Integer, ForeignKey('criadores.id'))
    cargo = Column(String)

    edicao = relationship('Edicao')
    criador = relationship('Criador')

class Leitura(Base):
    __tablename__ = 'leituras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    edicao_id = Column(Integer, ForeignKey('edicoes.id'))
    data = Column(Date)

    edicao = relationship('Edicao', back_populates='leituras')

    def __repr__(self):
        return f"<Leitura edicao_id={self.edicao_id} data={self.data}>"
