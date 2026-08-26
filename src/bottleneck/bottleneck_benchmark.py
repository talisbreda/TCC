"""
Benchmark — Problema de Atribuicao Gargalo (LBAP). Harness compartilhado.

Compara os dois algoritmos exatos descritos no capitulo de atribuicao gargalo:
  - Threshold (busca binaria sobre o limiar + verificacao por emparelhamento);
  - Caminhos aumentantes (Dijkstra de gargalo, construtivo).

Ambos sao exatos: o custo gargalo e sempre o mesmo (verificado em 500 matrizes
aleatorias). A comparacao de interesse e tempo e crescimento empirico.
"""

import io
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.algorithms import AlgorithmSpec, EXATO, PYTHON  # noqa: E402
from common.harness import executar_suite  # noqa: E402
from common import report, growth  # noqa: E402
from common.loader import carregar_funcao  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_RESULTS = Path(__file__).resolve().parent.parent.parent / "results"

_threshold = carregar_funcao(
    "src/bottleneck/threshold/assignment_bottleneck_lbap.py",
    "assignment_bottleneck_lbap")
_augmenting = carregar_funcao(
    "src/bottleneck/augmenting/assignment_bottleneck_augmenting.py",
    "assignment_bottleneck_augmenting")


def build_cost_1(n, seed=42):
    """Densa uniforme: custo[i][j] in [1, 100] aleatorio."""
    rng = random.Random(seed)
    return [[rng.randint(1, 100) for _ in range(n)] for _ in range(n)]


def build_cost_2(n, seed=42):
    """Estruturada: custo[i][j] = |i - j| + 1 (gargalo otimo pequeno)."""
    return [[abs(i - j) + 1 for j in range(n)] for i in range(n)]


def build_cost_3(n, seed=42):
    """Poucos valores distintos (muitos empates no limiar)."""
    rng = random.Random(seed)
    return [[rng.choice([1, 5, 10, 50]) for _ in range(n)] for _ in range(n)]


SIZES = [10, 20, 30, 50, 75, 100, 150, 200]
RUNS = 5

SPECS = [
    AlgorithmSpec("threshold", "Threshold (busca binária)", "O(n³ log n)", "O(n²)",
                  EXATO, PYTHON, lambda m: _threshold(m),
                  source_url="https://github.com/djohnson2718/Linear-Bottleneck-Assignment-Problem"),
    AlgorithmSpec("augmenting", "Caminhos aumentantes", "O(n³)", "O(n²)",
                  EXATO, PYTHON, lambda m: _augmenting(m)),
]

COSTS = [
    ("Matriz 1 — Densa uniforme  | custo in [1,100]", build_cost_1),
    ("Matriz 2 — Estruturada     | custo = |i-j|+1", build_cost_2),
    ("Matriz 3 — Poucos valores  | muitos empates", build_cost_3),
]


def run_benchmark():
    instancias = [(rotulo, builder) for rotulo, builder in COSTS]
    registros = executar_suite(
        "bottleneck", SPECS, instancias, SIZES,
        runs=RUNS, qualidade_fn=lambda r, _inst: r[0],
        chave_referencia="threshold", seed=42,
    )
    report.imprimir_tabelas(registros, "bottleneck")
    report.gravar_csv(registros, _RESULTS / "bottleneck.csv")
    report.gravar_qualidade_canonica(registros, _RESULTS / "bottleneck-qualidade.csv")
    report.gravar_tabelas_latex(registros, _RESULTS / "tex", "bottleneck")
    growth.gravar_crescimento_csv(registros, _RESULTS / "bottleneck-crescimento.csv")
    return registros


if __name__ == "__main__":
    print("=" * 82)
    print("  BENCHMARK — PROBLEMA DE ATRIBUIÇÃO GARGALO (LBAP)")
    print("=" * 82)
    run_benchmark()
