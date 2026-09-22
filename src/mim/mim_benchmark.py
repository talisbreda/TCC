"""
Benchmark — Emparelhamento Induzido Máximo (MIM). Harness compartilhado.

MIM é NP-difícil, o que quebra a premissa dos outros problemas: aqui a QUALIDADE
é o eixo interessante, não só o tempo. Dois regimes:

  REGIME PEQUENO (n <= 40, grafos esparsos): o ótimo é obtido pelo exato
    (branch-and-bound sobre o grafo de conflitos). As heurísticas reportam a
    razão heurística/ótimo.

  REGIME GRANDE (n até 400): o ótimo é inatingível. As heurísticas são comparadas
    contra a MELHOR solução encontrada por qualquer uma delas (gap relativo ao
    melhor conhecido) — que NÃO é o ótimo, e isso é declarado.
"""

import io
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.algorithms import AlgorithmSpec, EXATO, HEURISTICA, PYTHON  # noqa: E402
from common.harness import executar_suite  # noqa: E402
from common.result import OK  # noqa: E402
from common import report, growth  # noqa: E402
from common.loader import carregar_funcao  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_RESULTS = Path(__file__).resolve().parent.parent.parent / "results"

_exact = carregar_funcao("src/mim/exact/mim_exact.py", "mim_exact")
_greedy = carregar_funcao("src/mim/heuristics/mim_greedy_random.py", "mim_greedy_random")
_mindeg = carregar_funcao("src/mim/heuristics/mim_min_degree.py", "mim_min_degree")


def _grafo(n, grau_medio, seed):
    p = grau_medio / max(n - 1, 1)
    rng = random.Random(seed)
    return [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]


def build_esparso(n, seed=42):
    return _grafo(n, 3.0, seed)


def build_medio(n, seed=42):
    return _grafo(n, 6.0, seed)


def build_denso(n, seed=42):
    return _grafo(n, 12.0, seed)


SIZES_PEQ = [10, 15, 20, 25, 30, 40]      # com exato
SIZES_GRA = [50, 100, 200, 400]           # heurísticas só
RUNS = 5

SPECS_PEQ = [
    AlgorithmSpec("exact", "Exato (MIS conflitos)", "exp.", "O(E²)",
                  EXATO, PYTHON, lambda inst: _exact(inst[0], inst[1])),
    AlgorithmSpec("greedy", "Guloso aleatório", "O(E²)", "O(V+E)",
                  HEURISTICA, PYTHON, lambda inst: _greedy(inst[0], inst[1])),
    AlgorithmSpec("mindeg", "Guloso grau mínimo", "O(E²)", "O(E²)",
                  HEURISTICA, PYTHON, lambda inst: _mindeg(inst[0], inst[1])),
]
SPECS_GRA = SPECS_PEQ[1:]   # só as heurísticas

INST = [
    ("Grafo esparso (grau ~3)", build_esparso),
    ("Grafo médio (grau ~6)", build_medio),
    ("Grafo denso (grau ~12)", build_denso),
]


def _inst(builder):
    return lambda n: (n, builder(n))


def _referencia_melhor_conhecido(registros):
    """
    No regime grande não há ótimo: define reference_optimum como a MELHOR
    qualidade encontrada por qualquer heurística na mesma célula, e recalcula
    quality_ratio. Declaradamente NÃO é o ótimo.
    """
    from collections import defaultdict
    melhor = defaultdict(float)
    for r in registros:
        if r.status == OK and r.quality is not None:
            k = (r.instance, r.n)
            melhor[k] = max(melhor[k], r.quality)
    for r in registros:
        k = (r.instance, r.n)
        if k in melhor and melhor[k] > 0:
            r.reference_optimum = melhor[k]
            if r.quality is not None:
                r.quality_ratio = r.quality / melhor[k]


def run_benchmark():
    # Regime pequeno: razão vs ótimo (exato como referência).
    peq = executar_suite(
        "mim-pequeno", SPECS_PEQ, [(r, _inst(b)) for r, b in INST], SIZES_PEQ,
        runs=RUNS, qualidade_fn=lambda r, _i: r[0], chave_referencia="exact", seed=42)

    # Regime grande: heurísticas só, gap vs melhor conhecido (pós-processado).
    gra = executar_suite(
        "mim-grande", SPECS_GRA, [(r, _inst(b)) for r, b in INST], SIZES_GRA,
        runs=RUNS, qualidade_fn=lambda r, _i: r[0], chave_referencia=None, seed=42)
    _referencia_melhor_conhecido(gra)

    registros = peq + gra
    report.imprimir_tabelas(registros, "mim")
    report.gravar_csv(registros, _RESULTS / "mim.csv")
    report.gravar_qualidade_canonica(registros, _RESULTS / "mim-qualidade.csv")
    report.gravar_tabelas_latex(registros, _RESULTS / "tex", "mim")
    growth.gravar_crescimento_csv(registros, _RESULTS / "mim-crescimento.csv")
    return registros


if __name__ == "__main__":
    print("=" * 82)
    print("  BENCHMARK — EMPARELHAMENTO INDUZIDO MÁXIMO (MIM)")
    print("=" * 82)
    run_benchmark()
