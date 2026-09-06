import os
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = "perfil"

BASE = "https://leagueofcomicgeeks.com"
PERFIL = "valadyne"
URL_PERFIL = f"{BASE}/profile/{PERFIL}/reading"

MESES = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
}

PADRAO_ID_EDICAO = re.compile(r'/comic/(\d+)')
PADRAO_ID_SERIE = re.compile(r'/series/(\d+)')
PADRAO_ID_CRIADOR = re.compile(r'/people/(\d+)')
PADRAO_ID_PERSONAGEM = re.compile(r'/character/(\d+)')

DELAY_INICIO = 10000
DELAY_CARREGAMENTO = 8000
DELAY_BLOCO = 2000

BANCO_URL = os.environ.get(
    "BANCO_URL",
    f"sqlite:///{RAIZ / 'banco.db'}",
)
