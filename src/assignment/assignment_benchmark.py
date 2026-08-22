"""
Benchmark — Problema de Atribuicao Linear. Migrado para o harness compartilhado.

Duas secoes, como na versao anterior, por viabilidade de execucao:
  - Secao 1: todos os algoritmos, tamanhos pequenos (o SSP e O(n^4) no pior caso).
  - Secao 2: so os hungaros + SciPy, tamanhos grandes.
A selecao dos algoritmos da Secao 2 e por CHAVE (D2), nao por fatia posicional
como antes -- inserir um algoritmo nao altera mais a Secao 2 em silencio.

Escalonamento de timeout DESLIGADO: o wrapper `benchaplin` viola a
monotonicidade -- trava na matriz densa em n=100 mas lanca AttributeError
(rapido) em n=150+. Com escalonamento, os tamanhos maiores seriam pulados e o
defeito `BugAttr` ficaria escondido. Cada celula corre com seu proprio orcamento.

Bugs conhecidos preservados (AC-03): `benchaplin` -> BugAttr (AttributeError),
`hunalgorithm` -> BugPerc (OSError).

O `benchaplin` e NAO-DETERMINISTICO entre processos (a mesma matriz ora retorna
o custo correto, ora lanca AttributeError, conforme a ordem de iteracao de um
conjunto de objetos, randomizada por PYTHONHASHSEED). Para resultados
reproduziveis, fixe PYTHONHASHSEED (ver results/ambiente.md).
"""

import io
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.algorithms import AlgorithmSpec, EXATO, BASELINE, PYTHON, C  # noqa: E402
from common.harness import executar_suite  # noqa: E402
from common import report, growth  # noqa: E402
from common.loader import carregar_funcao  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_RESULTS = Path(__file__).resolve().parent.parent.parent / "results"


# =============================================================================
# Wrappers
# =============================================================================

_munkres = carregar_funcao("src/assignment/hungarian/assignment_hungarian_munkres.py",
                           "hungarian_munkres")
_benchaplin = carregar_funcao("src/assignment/hungarian/assignment_hungarian_benchaplin.py",
                              "hungarian_benchaplin")
_hunalg = carregar_funcao("src/assignment/hungarian/assignment_hungarian_hunalgorithm.py",
                          "hungarian_hunalgorithm")
_mayorx = carregar_funcao("src/assignment/hungarian/assignment_hungarian_mayorx.py",
                          "hungarian_mayorx")
_ssp = carregar_funcao("src/assignment/ssp/assignment_ssp_flows.py",
                       "assignment_ssp_flows")
_scipy = carregar_funcao("src/assignment/scipy/assignment_scipy_linear_sum.py",
                         "assignment_scipy_linear_sum")


# =============================================================================
# Construtores de matriz de custo (identicos a versao anterior)
# =============================================================================

def build_cost_1(n, seed=42):
    rng = random.Random(seed)
    return [[rng.randint(1, 100) for _ in range(n)] for _ in range(n)]


def build_cost_2(n, seed=42):
    rng = random.Random(seed)
    perm = list(range(n))
    rng.shuffle(perm)
    m = [[rng.randint(50, 100) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        m[i][perm[i]] = 1
    return m


def build_cost_3(n, seed=42):
    return [[abs(i - j) + 1 for j in range(n)] for i in range(n)]


# =============================================================================
# Configuracao
# =============================================================================

SIZES = [10, 20, 30, 50, 75, 100]        # Secao 1: todos (limitado pelo SSP)
SIZES_HUN = [50, 100, 150, 200, 250]     # Secao 2: hungaros + SciPy
RUNS = 5
TIMEOUT_MS = 120_000                     # orcamento por celula (igual ao baseline)

_AttributeError = AttributeError
_OSError = OSError

SPECS = [
    AlgorithmSpec("munkres", "Húngaro (munkres)", "O(n^3)", "O(n²)",
                  EXATO, PYTHON, lambda m: _munkres(m),
                  source_url="https://github.com/bmc/munkres"),
    AlgorithmSpec("benchaplin", "Húngaro (benchaplin)", "O(n^3)", "O(n²)",
                  EXATO, PYTHON, lambda m: _benchaplin(m),
                  known_bugs=((_AttributeError, "BugAttr"),)),
    AlgorithmSpec("hunalg", "Húngaro (hunalgorithm)", "O(n^3)", "O(n²)",
                  EXATO, PYTHON, lambda m: _hunalg(m),
                  notes="laços Python sobre arrays NumPy",
                  known_bugs=((_OSError, "BugPerc"),)),
    AlgorithmSpec("mayorx", "Húngaro (mayorx/KM)", "O(n^3)", "O(n²)",
                  EXATO, PYTHON, lambda m: _mayorx(m),
                  notes="laços Python sobre arrays NumPy"),
    AlgorithmSpec("ssp", "SSP (flows)", "O(n^4)*", "O(n²)",
                  EXATO, PYTHON, lambda m: _ssp(m)),
    AlgorithmSpec("scipy", "SciPy (linear_sum_assg)", "O(n^3)", "O(n²)",
                  BASELINE, C, lambda m: _scipy(m),
                  source_url="https://scipy.org/"),
]

COSTS = [
    ("Matriz 1 — Densa uniforme  | custo in [1,100]", build_cost_1),
    ("Matriz 2 — Permutação barata | ótimo = n", build_cost_2),
    ("Matriz 3 — Estruturada     | custo = |i-j|+1", build_cost_3),
]

_CHAVES_SECAO_2 = ("munkres", "benchaplin", "hunalg", "mayorx", "scipy")  # sem SSP


def run_benchmark():
    from common.algorithms import selecionar
    instancias = [(rotulo, builder) for rotulo, builder in COSTS]

    # Custo total (minimizacao); referencia = munkres.
    comum = dict(runs=RUNS, timeout_ms=TIMEOUT_MS, qualidade_fn=lambda r: r[0],
                 chave_referencia="munkres", seed=42, escalonar_timeout=False)

    registros = executar_suite("assignment", SPECS, instancias, SIZES, **comum)
    registros += executar_suite("assignment", selecionar(SPECS, _CHAVES_SECAO_2),
                                instancias, SIZES_HUN, **comum)

    report.imprimir_tabelas(registros, "assignment")
    report.gravar_csv(registros, _RESULTS / "assignment.csv")
    report.gravar_qualidade_canonica(registros, _RESULTS / "assignment-qualidade.csv")
    report.gravar_tabelas_latex(registros, _RESULTS / "tex", "assignment")
    growth.gravar_crescimento_csv(registros, _RESULTS / "assignment-crescimento.csv")
    return registros


if __name__ == "__main__":
    print("=" * 82)
    print("  BENCHMARK — PROBLEMA DE ATRIBUIÇÃO LINEAR")
    print("=" * 82)
    run_benchmark()
