import argparse
from datetime import date, datetime

from retrospectiva.banco.sessao import nova_sessao, criar
from retrospectiva.analise.periodo import Periodo
from retrospectiva.analise.analise import Analise
from retrospectiva.analise.apresentacao import imprimir_relatorio
from retrospectiva.scraping.scraper import scraper

def data(texto):
    return datetime.strptime(texto, "%Y-%m-%d").date()

def comando_coletar(args):
    criar()
    scraper(limite=args.limite)

def comando_analisar(args):
    periodo = Periodo.partindo_de(
        ano=args.ano,
        mes=args.mes,
        trimestre=args.trimestre,
        semestre=args.semestre,
        dias=args.dias,
        inicio=args.inicio,
        fim=args.fim,
    )
        
    with nova_sessao() as sessao:
        analise = Analise(sessao, periodo)
        imprimir_relatorio(analise)

def main():
    parser = argparse.ArgumentParser(description="Retrospectiva de quadrinhos lidos")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_coletar = subparsers.add_parser("coletar", help="Roda o scraper e atualiza o banco local")
    p_coletar.add_argument("--limite", type=int, help="Limita até N° edições novas processasdas")

    p_analisar = subparsers.add_parser("analisar", help="Gera a retrospectiva")
    p_analisar.add_argument("--ano", type=int, help="Filtra um ano específico")
    p_analisar.add_argument("--mes", type=int, help="Filtra um mês específico")
    p_analisar.add_argument("--trimestre", type=int, help="Filtra um trimestre partindo do mês X")
    p_analisar.add_argument("--semestre", type=int, help="Filtra um semestre partindo do mês X")
    p_analisar.add_argument("--inicio", type=data, help="Data inicial (AAAA-MM-DD)")
    p_analisar.add_argument("--fim", type=data, help="Data final (AAAA-MM-DD)")
    p_analisar.add_argument("--dias", type=int, dest="dias", help="Filtra pelos últimos N dias")

    args = parser.parse_args()
    if args.comando == "coletar":
        comando_coletar(args)
    elif args.comando == "analisar":
        comando_analisar(args)


if __name__ == "__main__":
    main()
