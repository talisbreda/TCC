"""
Benchmark — Problema do Casamento Estavel. Migrado para o harness compartilhado.

Duas secoes, por viabilidade: a versao OOP tem alto sobrecusto por objeto e so
roda na Secao 1 (n pequeno); numerico e Lattas vao ate n=400 na Secao 2.

Qualidade diferente dos outros problemas: nao e um numero a maximizar/minimizar,
e sim ESTABILIDADE (pares bloqueantes = 0) e CONCORDANCIA com o emparelhamento
men-optimal de referencia. A celula "0 =ref" significa: 0 pares bloqueantes e
concorda com a referencia (numerico). Como o emparelhamento men-optimal e unico
(teorema), os tres algoritmos devem concordar sempre.

Por isso `qualidade_fn` recebe (resultado, instancia): os pares bloqueantes
dependem da instancia, nao so do emparelhamento retornado.
"""

import io
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.algorithms import AlgorithmSpec, EXATO, PYTHON, selecionar  # noqa: E402
from common.harness import executar_suite  # noqa: E402
from common import report, growth  # noqa: E402
from common.loader import carregar_funcao  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_RESULTS = Path(__file__).resolve().parent.parent.parent / "results"


# =============================================================================
# Wrappers
# =============================================================================

_oop = carregar_funcao("src/stable-marriage/gale-shapley/stable_marriage_gs_oop.py",
                       "stable_marriage_gs_oop")
_num = carregar_funcao("src/stable-marriage/gale-shapley/stable_marriage_gs_numeric.py",
                       "stable_marriage_gs_numeric")
_lat = carregar_funcao("src/stable-marriage/gale-shapley/stable_marriage_gs_lattas.py",
                       "stable_marriage_gs_lattas")


# =============================================================================
# Construtores de perfil (identicos a versao anterior)
# =============================================================================

def build_profile_1(n, seed=42):
    rng = random.Random(seed)
    men, women = [], []
    for _ in range(n):
        p = list(range(n)); rng.shuffle(p); men.append(p)
    for _ in range(n):
        p = list(range(n)); rng.shuffle(p); women.append(p)
    return men, women


def build_profile_2(n, seed=42):
    rng = random.Random(seed)
    pw = list(range(n)); rng.shuffle(pw)
    pm = list(range(n)); rng.shuffle(pm)
    return [list(pw) for _ in range(n)], [list(pm) for _ in range(n)]


def build_profile_3(n, seed=42):
    men = [[(i + k) % n for k in range(n)] for i in range(n)]
    women = [[(j - k) % n for k in range(n)] for j in range(n)]
    return men, women


def count_blocking_pairs(men_pref, women_pref, match):
    """Pares (m, w) que se prefeririam aos pares atuais. 0 = estavel."""
    n = len(men_pref)
    woman_match = [-1] * n
    for m in range(n):
        if match[m] != -1:
            woman_match[match[m]] = m
    men_rank = [[0] * n for _ in range(n)]
    women_rank = [[0] * n for _ in range(n)]
    for i in range(n):
        for pos, j in enumerate(men_pref[i]):
            men_rank[i][j] = pos
        for pos, j in enumerate(women_pref[i]):
            women_rank[i][j] = pos
    blocking = 0
    for m in range(n):
        w_cur = match[m]
        for w in range(n):
            if men_rank[m][w] < men_rank[m][w_cur]:
                m_cur = woman_match[w]
                if women_rank[w][m] < women_rank[w][m_cur]:
                    blocking += 1
    return blocking


def _qualidade(match, instancia):
    """
    Reproduz a celula do benchmark: "0 =ref" / "0 ≠ref" / "N!".

    Recomputa a referencia (numerico) na propria instancia -- barato (O(n²)) e
    evita depender do mecanismo numerico de referencia do harness, que nao se
    aplica a uma qualidade textual.
    """
    mp, wp = instancia
    match = [int(x) for x in match]
    bp = count_blocking_pairs(mp, wp, match)
    ref = [int(x) for x in _num(mp, wp)]
    if bp == 0 and match == ref:
        return "0 =ref"
    if bp == 0:
        return "0 ≠ref"
    return f"{bp}!"


# =============================================================================
# Configuracao
# =============================================================================

SIZES_ALL = [25, 50, 75, 100]        # os tres (limitado pela OOP)
SIZES_FAST = [100, 200, 300, 400]    # numerico + Lattas
RUNS = 5

SPECS = [
    AlgorithmSpec("oop", "Gale-Shapley (OOP/pip)", "O(n²)†", "O(n²)",
                  EXATO, PYTHON, lambda inst: _oop(inst[0], inst[1])),
    AlgorithmSpec("num", "Gale-Shapley (numérico/pip)", "O(n²)", "O(n²)",
                  EXATO, PYTHON, lambda inst: _num(inst[0], inst[1]),
                  notes="laços Python sobre arrays NumPy"),
    AlgorithmSpec("lattas", "Gale-Shapley (Lattas/dict)", "O(n³)*", "O(n²)",
                  EXATO, PYTHON, lambda inst: _lat(inst[0], inst[1])),
]

PROFILES = [
    ("Perfil 1 — Aleatório       | permutações uniformes", build_profile_1),
    ("Perfil 2 — Correlacionado  | ranking de popularidade", build_profile_2),
    ("Perfil 3 — Cíclico         | deslocamento estruturado", build_profile_3),
]

_CHAVES_SECAO_2 = ("num", "lattas")   # sem OOP


def run_benchmark():
    instancias = [(rotulo, builder) for rotulo, builder in PROFILES]
    comum = dict(runs=RUNS, qualidade_fn=_qualidade, chave_referencia=None, seed=42)

    registros = executar_suite("stable-marriage", SPECS, instancias, SIZES_ALL, **comum)
    registros += executar_suite("stable-marriage", selecionar(SPECS, _CHAVES_SECAO_2),
                                instancias, SIZES_FAST, **comum)

    report.imprimir_tabelas(registros, "stable-marriage")
    report.gravar_csv(registros, _RESULTS / "stable-marriage.csv")
    report.gravar_qualidade_canonica(registros, _RESULTS / "stable-marriage-qualidade.csv")
    report.gravar_tabelas_latex(registros, _RESULTS / "tex", "stable-marriage")
    growth.gravar_crescimento_csv(registros, _RESULTS / "stable-marriage-crescimento.csv")
    return registros


if __name__ == "__main__":
    print("=" * 82)
    print("  BENCHMARK — PROBLEMA DO CASAMENTO ESTÁVEL")
    print("=" * 82)
    run_benchmark()
