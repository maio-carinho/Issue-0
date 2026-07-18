from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from retrospectiva.config import BANCO_URL
from retrospectiva.banco.banco import Base

engine = create_engine(BANCO_URL)
Sessao = sessionmaker(bind=engine)

def criar():
    Base.metadata.create_all(engine)

@contextmanager
def nova_sessao():
    sessao = Sessao()
    try:
        yield sessao
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()
