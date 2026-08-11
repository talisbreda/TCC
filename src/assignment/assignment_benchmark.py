"""
Benchmark Comparativo — Problema de Atribuição Linear (Assignment Problem)
Algoritmos Externos — Minimização de Custo

Executa os wrappers de algoritmos nos MESMOS grafos, permitindo comparação
direta de tempo e qualidade de solução.

=============================================================================
ALGORITMOS
=============================================================================

  Húngaro (munkres/Clapper)     O(n^3)   Exato   Python puro
  Húngaro (benchaplin)          O(n^3)   Exato   Baseado em grafo (dict)   [*]
  Húngaro (hunalgorithm)        O(n^3)   Exato   Reducao de matriz (NumPy) [**]
  Húngaro (mayorx / KM)         O(n^3)   Exato   Kuhn-Munkres (NumPy)
  SSP (flows)                   O(n^4)*  Exato   Fluxo de custo minimo
                                         * pior caso FIFO BF em grafo denso
  SciPy (linear_sum_assignment) O(n^3)   Baseline Jonker-Volgenant (biblioteca)

  [*]  benchaplin — bug no repositorio original: em matrizes densas aleatorias
       (n >= ~30) find_matching() insere True no conjunto de emparelhamento M
       onde esperava um objeto Edge, causando AttributeError. O bug e sensivel
       ao conteudo da matriz; matrizes estruturadas nao o acionam.

  [**] hunalgorithm — limitacao de projeto: usa percolacao (busca de zeros na
       matriz reduzida) com limite max_num_percolation=20. Para matrizes densas
       aleatorias com n >= ~20, o numero de percolacoes necessarias ultrapassa
       o limite e a funcao lanca OSError. Matrizes estruturadas funcionam porque
       a reducao de linha/coluna produz padroes de zeros mais simples.

=============================================================================
MATRIZES DE CUSTO
=============================================================================

  Matriz 1 — Densa uniforme   custo in [1, 100]   sem estrutura
  Matriz 2 — Permutação barata  ótimo = 1·n, resto caro   ótimo fácil
  Matriz 3 — Estruturada   custo = |i-j| + 1   ótimo é a diagonal
"""

import io
import sys
import time
import importlib.util
import random
from pathlib import Path

# Garante saida UTF-8 no Windows (evita UnicodeEncodeError em terminais CP1252)
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_ROOT = Path(__file__).parent.parent.parent   # TCC/


# =============================================================================
# Importação dos wrappers via importlib (caminhos com hífens)
# =============================================================================

def _load(rel_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, _ROOT / rel_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_munkres    = _load("src/assignment/hungarian/assignment_hungarian_munkres.py",
                    "hun_munkres")
_benchaplin = _load("src/assignment/hungarian/assignment_hungarian_benchaplin.py",
                    "hun_benchaplin")
_hunalg     = _load("src/assignment/hungarian/assignment_hungarian_hunalgorithm.py",
                    "hun_hunalgorithm")
_mayorx     = _load("src/assignment/hungarian/assignment_hungarian_mayorx.py",
                    "hun_mayorx")
_ssp        = _load("src/assignment/ssp/assignment_ssp_flows.py",
                    "ssp_flows")
_scipy      = _load("src/assignment/scipy/assignment_scipy_linear_sum.py",
                    "scipy_lsa")


# =============================================================================
# Construtores de matrizes de custo
# =============================================================================

def build_cost_1(n, seed=42):
    """Densa uniforme: custo[i][j] in [1, 100] aleatório."""
    rng = random.Random(seed)
    return [[rng.randint(1, 100) for _ in range(n)] for _ in range(n)]


def build_cost_2(n, seed=42):
    """Permutação barata: uma permutação aleatória tem custo 1, resto caro.
    Ótimo = n (soma de n entradas de custo 1)."""
    rng = random.Random(seed)
    perm = list(range(n))
    rng.shuffle(perm)
    matrix = [[rng.randint(50, 100) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        matrix[i][perm[i]] = 1
    return matrix


def build_cost_3(n, seed=42):
    """Estruturada: custo[i][j] = |i - j| + 1. Ótimo é a diagonal principal,
    com custo total = n (cada entrada diagonal vale 1)."""
    return [[abs(i - j) + 1 for j in range(n)] for i in range(n)]


# =============================================================================
# Estatísticas de custo
# =============================================================================

def cost_stats(matrix):
    n = len(matrix)
    flat = [matrix[i][j] for i in range(n) for j in range(n)]
    return {
        "min":  min(flat),
        "max":  max(flat),
        "mean": sum(flat) / len(flat),
    }


# =============================================================================
# Benchmark
# =============================================================================

SIZES = [10, 20, 30, 50, 75, 100]     # SSP: viavel ate n=100 em Python puro
SIZES_HUN = [50, 100, 150, 200, 250]  # Apenas hungaros (O(n^3) -- mais rapidos)
RUNS  = 5

ALGORITHMS_ALL = [
    ("Húngaro (munkres)",     "O(n^3)", "exato",
     lambda m: _munkres.hungarian_munkres(m)),
    ("Húngaro (benchaplin)",  "O(n^3)", "exato",
     lambda m: _benchaplin.hungarian_benchaplin(m)),
    ("Húngaro (hunalgorithm)","O(n^3)", "exato",
     lambda m: _hunalg.hungarian_hunalgorithm(m)),
    ("Húngaro (mayorx/KM)",   "O(n^3)", "exato",
     lambda m: _mayorx.hungarian_mayorx(m)),
    ("SSP (flows)",           "O(n^4)*","exato",
     lambda m: _ssp.assignment_ssp_flows(m)),
    ("SciPy (linear_sum_assg)","O(n^3)", "baseline",
     lambda m: _scipy.assignment_scipy_linear_sum(m)),
]

# Húngaros + baseline SciPy (sem SSP), para a seção de n maior.
ALGORITHMS_HUN = ALGORITHMS_ALL[:4] + [ALGORITHMS_ALL[5]]

COSTS = [
    ("Matriz 1 — Densa uniforme  | custo in [1,100]", build_cost_1),
    ("Matriz 2 — Permutação barata | ótimo = n",      build_cost_2),
    ("Matriz 3 — Estruturada     | custo = |i-j|+1",  build_cost_3),
]


def _run_section(title, algorithms, sizes, costs):
    for c_name, c_builder in costs:
        sep = "=" * 82
        print(f"\n{sep}")
        print(f"  {c_name}")
        print(sep)

        # Estatísticas das matrizes
        print(f"\n  {'n':>5}  {'min':>6}  {'max':>6}  {'média':>8}")
        print(f"  {'-'*32}")
        for n in sizes:
            matrix = c_builder(n)
            s = cost_stats(matrix)
            print(f"  {n:>5}  {s['min']:>6}  {s['max']:>6}  {s['mean']:>8.2f}")

        # Ótimo de referência (munkres)
        opts = {}
        for n in sizes:
            matrix = c_builder(n)
            opt_cost, _ = _munkres.hungarian_munkres(matrix)
            opts[n] = opt_cost

        # Tabela de tempos
        print(f"\n  Tempos médios ({RUNS} execuções por célula) em milissegundos:\n")
        col_w = 12
        header = "".join(f"{'n='+str(n):>{col_w}}" for n in sizes)
        print(f"  {'Algoritmo':<28} {'Complexidade':<12} {'Tipo':<10}{header}")
        print(f"  {'-'*80}")

        for alg_name, complexity, alg_type, alg_fn in algorithms:
            row = f"  {alg_name:<28} {complexity:<12} {alg_type:<10}"
            for n in sizes:
                matrix = c_builder(n)
                try:
                    t0 = time.perf_counter()
                    for _ in range(RUNS):
                        alg_fn(matrix)
                    elapsed = (time.perf_counter() - t0) / RUNS * 1000
                    cell = f"{elapsed:.2f}ms"
                except AttributeError as e:
                    cell = "BugAttr"   # benchaplin: bool no lugar de Edge
                except OSError:
                    cell = "BugPerc"   # hunalgorithm: max_num_percolation excedido
                except Exception:
                    cell = "Erro"
                row += f"{cell:>{col_w}}"
            print(row)

        # Tabela de custo encontrado
        print(f"\n  Custo encontrado por algoritmo:\n")
        print(f"  {'Algoritmo':<28} {'Complexidade':<12} {'Tipo':<10}{header}")
        print(f"  {'-'*80}")

        for alg_name, complexity, alg_type, alg_fn in algorithms:
            row = f"  {alg_name:<28} {complexity:<12} {alg_type:<10}"
            for n in sizes:
                matrix = c_builder(n)
                opt    = opts[n]
                try:
                    cost_found, _ = alg_fn(matrix)
                    gap  = cost_found - opt
                    cell = f"{cost_found}" if gap == 0 else f"{cost_found}(+{gap})"
                except AttributeError:
                    cell = "BugAttr"
                except OSError:
                    cell = "BugPerc"
                except Exception:
                    cell = "Erro"
                row += f"{cell:>{col_w}}"
            print(row)

        print(f"\n  Referência (ótimo munkres): " +
              "  ".join(f"n={n}: {opts[n]}" for n in sizes))


def run_benchmark():
    # -----------------------------------------------------------------------
    # Seção 1 — Todos os algoritmos (n pequeno, por causa do SSP)
    # -----------------------------------------------------------------------
    sep = "#" * 82
    print(f"\n{sep}")
    print(f"  SEÇÃO 1 — Todos os algoritmos  |  n = {SIZES}")
    print(f"  (SSP é O(n⁴) no pior caso — tamanhos reduzidos para viabilidade)")
    print(sep)
    _run_section("todos", ALGORITHMS_ALL, SIZES, COSTS)

    # -----------------------------------------------------------------------
    # Seção 2 — Apenas húngaros (n maior)
    # -----------------------------------------------------------------------
    print(f"\n{sep}")
    print(f"  SEÇÃO 2 — Apenas algoritmos Húngaros  |  n = {SIZES_HUN}")
    print(sep)
    _run_section("hungaro", ALGORITHMS_HUN, SIZES_HUN, COSTS)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 82)
    print("  BENCHMARK — PROBLEMA DE ATRIBUIÇÃO LINEAR (ASSIGNMENT PROBLEM)")
    print("  Minimização de custo | Todos os algoritmos | Todas as matrizes")
    print("=" * 82)
    run_benchmark()
