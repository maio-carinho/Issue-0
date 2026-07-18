import os
from contextlib import contextmanager
from playwright.sync_api import sync_playwright

from retrospectiva.config import PASTA

@contextmanager
def abrir_navegador():
    perfil = os.path.join(os.getcwd(), PASTA)
    with sync_playwright() as p:
        navegador = p.chromium.launch_persistent_context(
            perfil,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            no_viewport=True
        )
        try:
            yield navegador
        finally:
            navegador.close()

@contextmanager
def abrir_aba(navegador):
    aba = navegador.new_page()
    try:
        yield aba
    finally:
        aba.close()