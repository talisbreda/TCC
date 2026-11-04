"""
Regenera as tabelas LaTeX dos resultados a partir dos CSVs ja medidos.

Os benchmarks gravam as tabelas ao final de cada medicao (`report.py`). Este
script refaz so essa ultima etapa, lendo `results/<problema>.csv`, para que
ajustes de formatacao (legendas, rotulos, fonte) nao exijam medir de novo.
Nenhum numero e alterado: as celulas saem dos mesmos campos do CSV.

Uso: python3 scripts/regera_tabelas.py [diretorio_de_saida]
"""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from common import report  # noqa: E402
from common.result import ResultRecord  # noqa: E402

# arquivo CSV -> nome do problema usado nos arquivos .tex
PROBLEMAS = {
    "mcm": "mcm",
    "assignment": "assignment",
    "bottleneck": "bottleneck",
    "stable-marriage": "stable-marriage",
    "general": "general",
    "mim": "mim",
}


def _numero(texto):
    return None if texto == "" else float(texto)


def _qualidade(texto):
    """Numero quando o CSV traz numero; texto (ex. "0 =ref") caso contrario."""
    if texto == "":
        return None
    try:
        return float(texto)
    except ValueError:
        return texto


def carregar(caminho):
    registros = []
    with open(caminho, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            registros.append(ResultRecord(
                problem=linha["problem"],
                algorithm=linha["algorithm"],
                algorithm_key=linha["algorithm_key"],
                kind=linha["kind"],
                language=linha["language"],
                instance=linha["instance"],
                n=int(linha["n"]),
                seed=int(linha["seed"]) if linha["seed"] else None,
                complexity_time=linha["complexity_time"],
                complexity_space=linha["complexity_space"],
                runs=int(linha["runs"]) if linha["runs"] else 0,
                time_median_ms=_numero(linha["time_median_ms"]),
                quality=_qualidade(linha["quality"]),
                reference_optimum=_numero(linha["reference_optimum"]),
                quality_ratio=_numero(linha["quality_ratio"]),
                status=linha["status"],
                detail=linha["detail"],
            ))
    return registros


def main():
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "results" / "tex"
    for arquivo, problema in PROBLEMAS.items():
        registros = carregar(RAIZ / "results" / f"{arquivo}.csv")
        gerados = report.gravar_tabelas_latex(registros, saida, problema)
        print(f"{problema}: {len(gerados)} tabelas")


if __name__ == "__main__":
    main()
