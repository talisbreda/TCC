"""
Benchmark — Emparelhamento de Cardinalidade Maxima (MCM) em Grafos Bipartidos.

Migrado para o harness compartilhado (`src/common/`). As responsabilidades de
medicao, gravacao e formatacao vivem agora no harness; este arquivo so declara
o que e especifico do MCM: os construtores de grafo e a lista de algoritmos.

Saidas (AC-15): tabelas no terminal, `results/mcm.csv` (dados brutos),
`results/mcm-qualidade.csv` (canonico, para o AC-17), `results/mcm-crescimento.csv`
(expoente empirico) e as tabelas LaTeX em `results/tex/`.

Nomes de algoritmo e rotulos de grafo sao identicos aos da versao anterior de
proposito: sao a chave de comparacao contra o baseline pre-migracao
(`results/baseline/mcm-qualidade.csv`).
"""

import io
import random
import sys
from collections import defaultdict
from pathlib import Path

# src/ nao e pacote e os diretorios tem hifens: poe src/ no path para importar
# `common`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.algorithms import AlgorithmSpec, EXATO, BASELINE, PYTHON, C  # noqa: E402
from common.harness import executar_suite  # noqa: E402
from common import report, growth  # noqa: E402
from common.loader import carregar_funcao  # noqa: E402

# Saida UTF-8 no Windows (mantida por custo zero; ver results/ambiente.md).
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_RESULTS = Path(__file__).resolve().parent.parent.parent / "results"


# =============================================================================
# Wrappers
# =============================================================================

_aug = carregar_funcao(
    "src/mcm/augmenting/bipartite_mcm_augmenting_paths_wbchristerson.py",
    "max_cardinality_matching_augmenting_paths_wbchristerson")
_hk = carregar_funcao(
    "src/mcm/hopcroft-karp/bipartite_mcm_hopcroft_karp_sofiat.py",
    "max_cardinality_matching_hopcroft_karp_sofiat")
_ek = carregar_funcao(
    "src/mcm/edmonds-karp/bipartite_mcm_edmonds_karp_maxflow.py",
    "max_cardinality_matching_edmonds_karp_maxflow")
_nx = carregar_funcao(
    "src/mcm/networkx/bipartite_mcm_networkx_hopcroftkarp.py",
    "max_cardinality_matching_networkx_hopcroftkarp")
_ig = carregar_funcao(
    "src/mcm/igraph/bipartite_mcm_igraph.py",
    "max_cardinality_matching_igraph")


# =============================================================================
# Construtores de grafo (identicos a versao anterior)
# =============================================================================

def build_graph_1(n, seed=42):
    a_left, a_right = int(n * 0.8), int(n * 0.6)
    b_left, b_right = n - a_left, n - a_right
    edges = set()
    for i in range(a_left):
        edges.add((i, i % a_right))
        edges.add((i, (i + 1) % a_right))
    for k in range(b_left):
        for off in range(3):
            edges.add((a_left + k, a_right + (k * 2 + off) % b_right))
    return list(edges)


def build_graph_2(n, seed=42):
    edges = set()
    for i in range(n):
        edges.add((i, i))
        j = (i * 7 + 3) % n
        if j == i:
            j = (j + 1) % n
        edges.add((i, j))
    return list(edges)


def build_graph_3(n, seed=42, avg_degree=15):
    rng = random.Random(seed)
    edges = set((i, i) for i in range(n))
    target = n * avg_degree
    while len(edges) < target:
        edges.add((rng.randint(0, n - 1), rng.randint(0, n - 1)))
    return list(edges)


def graph_stats(n, edges):
    dl = defaultdict(int)
    for u, _ in edges:
        dl[u] += 1
    return {
        "edges": len(edges),
        "deg_avg": sum(dl[i] for i in range(n)) / n,
        "density": len(edges) / (n * n) * 100,
    }


# =============================================================================
# Configuracao
# =============================================================================

SIZES = [50, 100, 150, 200, 250]
RUNS = 5

# A instancia carrega n junto das arestas: o construtor recebe n e devolve
# (n, edges); cada fn desempacota para a interface (n_left, n_right, edges).
def _inst(builder):
    return lambda n: (n, builder(n))


SPECS = [
    AlgorithmSpec("aug", "Aug. Paths (wbchristerson)", "O(V·E)", "O(V+E)",
                  EXATO, PYTHON, lambda inst: _aug(inst[0], inst[0], inst[1]),
                  source_url="https://github.com/wbchristerson/perfect-matchings"),
    AlgorithmSpec("hk", "Hopcroft-Karp (sofiat)", "O(E·√V)", "O(V+E)",
                  EXATO, PYTHON, lambda inst: _hk(inst[0], inst[0], inst[1]),
                  source_url="https://github.com/sofiat-olaosebikan/hopcroftkarp"),
    # O wrapper Edmonds-Karp monta uma matriz de capacidade (V+2)x(V+2):
    # espaco O(V^2), diferente dos demais.
    AlgorithmSpec("ek", "Edmonds-Karp (Maxflow-Algs)", "O(V·E²)", "O(V²)",
                  EXATO, PYTHON, lambda inst: _ek(inst[0], inst[0], inst[1])),
    # NetworkX e Python puro (D8): kind=baseline, language=python.
    AlgorithmSpec("nx", "Hopcroft-Karp (NetworkX)", "O(E·√V)", "O(V+E)",
                  BASELINE, PYTHON, lambda inst: _nx(inst[0], inst[0], inst[1]),
                  source_url="https://networkx.org/"),
    AlgorithmSpec("ig", "Bipartite Match. (igraph)", "O(E·√V)", "O(V+E)",
                  BASELINE, C, lambda inst: _ig(inst[0], inst[0], inst[1]),
                  source_url="https://igraph.org/python/"),
]

GRAPHS = [
    ("Grafo 1 — Esparso | SEM perfeito | MCM = 80% de n", build_graph_1),
    ("Grafo 2 — Esparso | COM perfeito | MCM = n", build_graph_2),
    ("Grafo 3 — Denso   | COM perfeito | MCM = n", build_graph_3),
]


def run_benchmark():
    instancias = [(rotulo, _inst(builder)) for rotulo, builder in GRAPHS]

    registros = executar_suite(
        "mcm", SPECS, instancias, SIZES,
        runs=RUNS, qualidade_fn=lambda r: r[0],
        chave_referencia="hk", seed=42,
    )

    report.imprimir_tabelas(registros, "mcm")
    report.gravar_csv(registros, _RESULTS / "mcm.csv")
    report.gravar_qualidade_canonica(registros, _RESULTS / "mcm-qualidade.csv")
    report.gravar_tabelas_latex(registros, _RESULTS / "tex", "mcm")
    growth.gravar_crescimento_csv(registros, _RESULTS / "mcm-crescimento.csv")
    return registros


if __name__ == "__main__":
    print("=" * 78)
    print("  BENCHMARK — MCM EM GRAFOS BIPARTIDOS")
    print("=" * 78)
    run_benchmark()
