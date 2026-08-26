"""
Benchmark — Emparelhamento em Grafos Gerais (não bipartidos). Harness compartilhado.

Duas suítes, cobrindo os dois problemas dos capítulos de grafos gerais:

  CARDINALIDADE MÁXIMA (cap. 5.1):
    - Blossom/Edmonds (adharshkamath) — exato, implementado
    - NetworkX (maxcardinality) — baseline

  PESO MÁXIMO (cap. 5.2):
    - van Rantwijk (mwmatching) — exato, implementado
    - NetworkX (max_weight_matching) — baseline (MESMA LINHAGEM de van Rantwijk, D9)
    - Path Growing (Drake-Hougardy) — heurística 1/2-aproximada

Todos em Python puro (nenhum núcleo compilado aqui), então a comparação de tempo
é justa. A ressalva de linhagem NetworkX↔van Rantwijk vai declarada no capítulo
de Resultados.
"""

import io
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.algorithms import AlgorithmSpec, EXATO, HEURISTICA, BASELINE, PYTHON  # noqa: E402
from common.harness import executar_suite  # noqa: E402
from common import report, growth  # noqa: E402
from common.loader import carregar_funcao  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_RESULTS = Path(__file__).resolve().parent.parent.parent / "results"

_blossom = carregar_funcao("src/general/blossom/general_mcm_blossom.py",
                           "max_cardinality_matching_blossom")
_vanrantwijk = carregar_funcao("src/general/weighted/general_weighted_vanrantwijk.py",
                               "max_weight_matching_vanrantwijk")
_path_growing = carregar_funcao("src/general/heuristics/general_path_growing.py",
                                "max_weight_matching_path_growing")
_nx = carregar_funcao("src/general/networkx/general_networkx_matching.py",
                      "max_cardinality_matching_networkx")
_nxw = carregar_funcao("src/general/networkx/general_networkx_matching.py",
                       "max_weight_matching_networkx")


# --- geradores de grafo geral ---
def _grafo(n, p, seed):
    rng = random.Random(seed)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append((u, v))
    return edges


def build_card_esparso(n, seed=42):
    return _grafo(n, 3.0 / max(n, 1), seed)      # grau médio ~3


def build_card_denso(n, seed=42):
    return _grafo(n, 0.3, seed)


def build_weight_esparso(n, seed=42):
    rng = random.Random(seed + 1)
    return [(u, v, rng.randint(1, 100)) for (u, v) in _grafo(n, 3.0 / max(n, 1), seed)]


def build_weight_denso(n, seed=42):
    rng = random.Random(seed + 1)
    return [(u, v, rng.randint(1, 100)) for (u, v) in _grafo(n, 0.3, seed)]


SIZES = [10, 20, 30, 50, 75, 100]
RUNS = 5

SPECS_CARD = [
    AlgorithmSpec("blossom", "Blossom (Edmonds)", "O(V³)", "O(V²)",
                  EXATO, PYTHON, lambda inst: _blossom(inst[0], inst[1]),
                  source_url="https://github.com/adharshkamath/Edmonds-Algorithm"),
    AlgorithmSpec("nx_card", "NetworkX (cardinalidade)", "O(V³)", "O(V+E)",
                  BASELINE, PYTHON, lambda inst: _nx(inst[0], inst[1]),
                  source_url="https://networkx.org/"),
]
SPECS_WEIGHT = [
    AlgorithmSpec("vanrantwijk", "van Rantwijk (mwmatching)", "O(V³)", "O(V+E)",
                  EXATO, PYTHON, lambda inst: _vanrantwijk(inst[0], inst[1]),
                  source_url="https://jorisvr.nl/article/maximum-matching"),
    AlgorithmSpec("nx_weight", "NetworkX (peso máximo)", "O(V³)", "O(V+E)",
                  BASELINE, PYTHON, lambda inst: _nxw(inst[0], inst[1]),
                  source_url="https://networkx.org/",
                  notes="mesma linhagem de van Rantwijk (D9)"),
    AlgorithmSpec("path_growing", "Path Growing", "O(E)", "O(V+E)",
                  HEURISTICA, PYTHON, lambda inst: _path_growing(inst[0], inst[1])),
]

INST_CARD = [
    ("Cardinalidade — esparso (grau ~3)", build_card_esparso),
    ("Cardinalidade — denso (p=0.3)", build_card_denso),
]
INST_WEIGHT = [
    ("Peso — esparso (grau ~3)", build_weight_esparso),
    ("Peso — denso (p=0.3)", build_weight_denso),
]


def _inst(builder):
    return lambda n: (n, builder(n))


def run_benchmark():
    registros = []
    registros += executar_suite(
        "general-card", SPECS_CARD, [(r, _inst(b)) for r, b in INST_CARD], SIZES,
        runs=RUNS, qualidade_fn=lambda r, _i: r[0], chave_referencia="blossom", seed=42)
    registros += executar_suite(
        "general-weight", SPECS_WEIGHT, [(r, _inst(b)) for r, b in INST_WEIGHT], SIZES,
        runs=RUNS, qualidade_fn=lambda r, _i: r[0], chave_referencia="vanrantwijk", seed=42)

    report.imprimir_tabelas(registros, "general")
    report.gravar_csv(registros, _RESULTS / "general.csv")
    report.gravar_qualidade_canonica(registros, _RESULTS / "general-qualidade.csv")
    report.gravar_tabelas_latex(registros, _RESULTS / "tex", "general")
    growth.gravar_crescimento_csv(registros, _RESULTS / "general-crescimento.csv")
    return registros


if __name__ == "__main__":
    print("=" * 82)
    print("  BENCHMARK — EMPARELHAMENTO EM GRAFOS GERAIS")
    print("=" * 82)
    run_benchmark()
