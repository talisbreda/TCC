"""
Benchmark Comparativo — Emparelhamento de Cardinalidade Máxima (MCM)
em Grafos Bipartidos — Algoritmos Externos

Executa os 3 wrappers de algoritmos obtidos de repositórios externos nos
MESMOS grafos, permitindo comparação direta de tempo e qualidade de solução.

=============================================================================
ALGORITMOS
=============================================================================

  Aug. Paths (wbchristerson)   O(V·E)    Exato    BFS por vértice livre
  Hopcroft-Karp (sofiat)       O(E·√V)   Exato    BFS em fases + DFS
  Edmonds-Karp (Maxflow-Algs)  O(V·E²)   Exato    Max-flow com BFS

=============================================================================
GRAFOS  (idênticos ao benchmark de src_claude/)
=============================================================================

  Grafo 1 — Esparso, SEM emparelhamento perfeito   grau~2.2  MCM=80%n
  Grafo 2 — Esparso, COM emparelhamento perfeito   grau=2    MCM=n
  Grafo 3 — Denso,   COM emparelhamento perfeito   grau~15   MCM=n
"""

import sys
import time
import importlib.util
from pathlib import Path
from collections import defaultdict

sys.setrecursionlimit(5000)

_ROOT = Path(__file__).parent.parent.parent   # TCC/


# =============================================================================
# Importação dos wrappers via importlib (diretórios com hífens)
# =============================================================================

def _load(rel_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, _ROOT / rel_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_aug = _load("src/mcm/augmenting/bipartite_mcm_augmenting_paths_wbchristerson.py",
             "aug_wbchristerson")
_hk  = _load("src/mcm/hopcroft-karp/bipartite_mcm_hopcroft_karp_sofiat.py",
             "hk_sofiat")
_ek  = _load("src/mcm/edmonds-karp/bipartite_mcm_edmonds_karp_maxflow.py",
             "ek_maxflow")


# =============================================================================
# Construtores de grafo  (idênticos ao src_claude/mcm_benchmark.py)
# =============================================================================

def build_graph_1(n, seed=42):
    a_left  = int(n * 0.8)
    a_right = int(n * 0.6)
    b_left  = n - a_left
    b_right = n - a_right
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
    import random
    rng = random.Random(seed)
    edges = set((i, i) for i in range(n))
    target = n * avg_degree
    while len(edges) < target:
        edges.add((rng.randint(0, n - 1), rng.randint(0, n - 1)))
    return list(edges)


# =============================================================================
# Estatísticas
# =============================================================================

def graph_stats(n, edges):
    dl = defaultdict(int)
    dr = defaultdict(int)
    for u, v in edges:
        dl[u] += 1
        dr[v] += 1
    degs_l = [dl[i] for i in range(n)]
    return {
        "edges":   len(edges),
        "deg_avg": sum(degs_l) / len(degs_l),
        "density": len(edges) / (n * n) * 100,
    }


# =============================================================================
# Benchmark
# =============================================================================

SIZES = [50, 100, 150, 200, 250]
RUNS  = 5

ALGORITHMS = [
    ("Aug. Paths (wbchristerson)", "O(V·E)",   "exato",
     lambda n, e: _aug.max_cardinality_matching_augmenting_paths_wbchristerson(n, n, e)),
    ("Hopcroft-Karp (sofiat)",     "O(E·√V)",  "exato",
     lambda n, e: _hk.max_cardinality_matching_hopcroft_karp_sofiat(n, n, e)),
    ("Edmonds-Karp (Maxflow-Algs)","O(V·E²)",  "exato",
     lambda n, e: _ek.max_cardinality_matching_edmonds_karp_maxflow(n, n, e)),
]

GRAPHS = [
    ("Grafo 1 — Esparso | SEM perfeito | MCM = 80% de n", build_graph_1),
    ("Grafo 2 — Esparso | COM perfeito | MCM = n",         build_graph_2),
    ("Grafo 3 — Denso   | COM perfeito | MCM = n",         build_graph_3),
]


def run_benchmark():
    for g_name, g_builder in GRAPHS:
        sep = "=" * 78
        print(f"\n{sep}")
        print(f"  {g_name}")
        print(sep)

        print(f"\n  {'n':>5}  {'|E|':>7}  {'grau médio':>11}  {'densidade':>10}")
        print(f"  {'-'*38}")
        for n in SIZES:
            edges = g_builder(n)
            s = graph_stats(n, edges)
            print(f"  {n:>5}  {s['edges']:>7,}  {s['deg_avg']:>11.2f}  {s['density']:>9.3f}%")

        # Ótimo de referência (Hopcroft-Karp sofiat)
        opts = {}
        for n in SIZES:
            edges = g_builder(n)
            opt, _, _ = _hk.max_cardinality_matching_hopcroft_karp_sofiat(n, n, edges)
            opts[n] = opt

        # Tabela de tempos
        print(f"\n  Tempos médios ({RUNS} execuções por célula) em milissegundos:\n")
        col_w = 13
        header = "".join(f"{'n='+str(n):>{col_w}}" for n in SIZES)
        print(f"  {'Algoritmo':<30} {'Complexidade':<12} {'Tipo':<10}{header}")
        print(f"  {'-'*80}")

        for alg_name, complexity, alg_type, alg_fn in ALGORITHMS:
            row = f"  {alg_name:<30} {complexity:<12} {alg_type:<10}"
            for n in SIZES:
                edges = g_builder(n)
                try:
                    t0 = time.perf_counter()
                    for _ in range(RUNS):
                        result = alg_fn(n, edges)
                    elapsed = (time.perf_counter() - t0) / RUNS * 1000
                    cell = f"{elapsed:.2f}ms"
                except RecursionError:
                    cell = "RecErr"
                row += f"{cell:>{col_w}}"
            print(row)

        # Tabela de MCM encontrado
        print(f"\n  MCM encontrado por algoritmo:\n")
        print(f"  {'Algoritmo':<30} {'Complexidade':<12} {'Tipo':<10}{header}")
        print(f"  {'-'*80}")

        for alg_name, complexity, alg_type, alg_fn in ALGORITHMS:
            row = f"  {alg_name:<30} {complexity:<12} {alg_type:<10}"
            for n in SIZES:
                edges = g_builder(n)
                opt   = opts[n]
                try:
                    result = alg_fn(n, edges)
                    mcm    = result[0]
                    gap    = opt - mcm
                    cell   = f"{mcm}" if gap == 0 else f"{mcm}(-{gap})"
                except RecursionError:
                    cell = "RecErr"
                row += f"{cell:>{col_w}}"
            print(row)

        print(f"\n  Referência (ótimo): " +
              "  ".join(f"n={n}: {opts[n]}" for n in SIZES))


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 78)
    print("  BENCHMARK — MCM EM GRAFOS BIPARTIDOS (ALGORITMOS EXTERNOS)")
    print("  Todos os algoritmos | Todos os grafos | Tamanhos n = 50..250")
    print("=" * 78)
    run_benchmark()
