"""
Benchmark Comparativo — Problema do Casamento Estavel (Stable Marriage)
Algoritmos Externos — Gale-Shapley (Aceitacao Diferida)

Executa os wrappers nos MESMOS perfis de preferencia, permitindo comparacao
direta de tempo e de corretude (estabilidade) da solucao.

=============================================================================
INTERFACE PADRAO
=============================================================================

  Entrada:
    men_pref[m]   : lista de indices de mulheres em ordem de preferencia do
                    homem m (mais preferida primeiro).
    women_pref[w] : lista de indices de homens em ordem de preferencia da
                    mulher w.
  Saida:
    match : lista onde match[m] = w (homem m casado com a mulher w).

  Todos os algoritmos sao men-optimal (os homens propoem). Pelo teorema de
  unicidade do emparelhamento otimo para os pretendentes, os tres devem
  produzir EXATAMENTE o mesmo emparelhamento.

=============================================================================
ALGORITMOS
=============================================================================

  Gale-Shapley (OOP / pip)       O(n^2)†  Exato   Objetos Proposer/Responder
  Gale-Shapley (numerico / pip)  O(n^2)   Exato   Matrizes de rank (NumPy)
  Gale-Shapley (Lattas / dict)   O(n^3)*  Exato   Dicionarios por nome
                                          * .index() em lista a cada rejeicao
                                          † O(n^2) em teoria, mas o sobrecusto
                                            por objeto (reconstrucao de listas
                                            de livres a cada rodada) a torna
                                            inviavel na pratica acima de n≈100;
                                            por isso so aparece na Secao 1.

=============================================================================
PERFIS DE PREFERENCIA
=============================================================================

  Perfil 1 — Aleatorio      permutacoes uniformes independentes
  Perfil 2 — Correlacionado todos compartilham um ranking de "popularidade"
                            (alta contencao: muitos propoem as mesmas)
  Perfil 3 — Ciclico        deslocamento ciclico estruturado (muitas rejeicoes)
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
# Importacao dos wrappers via importlib (diretorios com hifens)
# =============================================================================

def _load(rel_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, _ROOT / rel_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_oop = _load("src/stable-marriage/gale-shapley/stable_marriage_gs_oop.py",
             "sm_gs_oop")
_num = _load("src/stable-marriage/gale-shapley/stable_marriage_gs_numeric.py",
             "sm_gs_numeric")
_lat = _load("src/stable-marriage/gale-shapley/stable_marriage_gs_lattas.py",
             "sm_gs_lattas")


# =============================================================================
# Construtores de perfis de preferencia
# =============================================================================

def build_profile_1(n, seed=42):
    """Aleatorio: cada participante recebe uma permutacao uniforme."""
    rng = random.Random(seed)
    men_pref = []
    women_pref = []
    for _ in range(n):
        p = list(range(n))
        rng.shuffle(p)
        men_pref.append(p)
    for _ in range(n):
        p = list(range(n))
        rng.shuffle(p)
        women_pref.append(p)
    return men_pref, women_pref


def build_profile_2(n, seed=42):
    """Correlacionado: existe um ranking global de popularidade que todos
    seguem (com pequena perturbacao). Gera alta contencao."""
    rng = random.Random(seed)
    pop_women = list(range(n))
    rng.shuffle(pop_women)
    pop_men = list(range(n))
    rng.shuffle(pop_men)
    # Todos os homens preferem as mesmas mulheres (na ordem de popularidade);
    # todas as mulheres preferem os mesmos homens.
    men_pref = [list(pop_women) for _ in range(n)]
    women_pref = [list(pop_men) for _ in range(n)]
    return men_pref, women_pref


def build_profile_3(n, seed=42):
    """Ciclico: homem i prefere a partir da mulher i (deslocamento ciclico);
    mulheres preferem em ordem ciclica oposta. Estrutura que provoca muitas
    rejeicoes em cadeia."""
    men_pref = [[(i + k) % n for k in range(n)] for i in range(n)]
    women_pref = [[(j - k) % n for k in range(n)] for j in range(n)]
    return men_pref, women_pref


# =============================================================================
# Verificacao de estabilidade
# =============================================================================

def count_blocking_pairs(men_pref, women_pref, match):
    """
    Conta pares bloqueantes (m, w): homem m e mulher w que se prefeririam
    mutuamente aos seus pares atuais. match estavel => 0 pares bloqueantes.
    """
    n = len(men_pref)
    # match[m] = w  -> inverso  woman_match[w] = m
    woman_match = [-1] * n
    for m in range(n):
        if match[m] != -1:
            woman_match[match[m]] = m

    # rank[i][j] = posicao de j na lista de i (menor = mais preferido)
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
            # m prefere w ao seu par atual?
            if men_rank[m][w] < men_rank[m][w_cur]:
                m_cur = woman_match[w]
                # w prefere m ao seu par atual?
                if women_rank[w][m] < women_rank[w][m_cur]:
                    blocking += 1
    return blocking


# =============================================================================
# Benchmark
# =============================================================================

# A versão OOP, apesar de O(n²) em teoria, tem alto sobrecusto por objeto
# (reconstrói listas de livres a cada rodada) e na prática fica inviável
# acima de n ≈ 100. Por isso o benchmark tem duas seções, como o de
# assignment: Seção 1 com os três algoritmos em n pequeno, Seção 2 apenas
# com os rápidos (numérico e Lattas) em n maior.
SIZES_ALL  = [25, 50, 75, 100]        # os três algoritmos (limitado pela OOP)
SIZES_FAST = [100, 200, 300, 400]     # numérico + Lattas
RUNS = 5

ALGORITHMS_ALL = [
    ("Gale-Shapley (OOP/pip)",       "O(n²)†", "exato",
     lambda mp, wp: _oop.stable_marriage_gs_oop(mp, wp)),
    ("Gale-Shapley (numérico/pip)",  "O(n²)",  "exato",
     lambda mp, wp: _num.stable_marriage_gs_numeric(mp, wp)),
    ("Gale-Shapley (Lattas/dict)",   "O(n³)*", "exato",
     lambda mp, wp: _lat.stable_marriage_gs_lattas(mp, wp)),
]

# Seção 2: sem a OOP (índices 1 e 2 = numérico e Lattas).
ALGORITHMS_FAST = ALGORITHMS_ALL[1:]

PROFILES = [
    ("Perfil 1 — Aleatório       | permutações uniformes",     build_profile_1),
    ("Perfil 2 — Correlacionado  | ranking de popularidade",   build_profile_2),
    ("Perfil 3 — Cíclico         | deslocamento estruturado",  build_profile_3),
]


def _run_section(algorithms, sizes):
    for p_name, p_builder in PROFILES:
        sep = "=" * 82
        print(f"\n{sep}")
        print(f"  {p_name}")
        print(sep)

        col_w = 12
        header = "".join(f"{'n='+str(n):>{col_w}}" for n in sizes)

        # Tabela de tempos
        print(f"\n  Tempos médios ({RUNS} execuções por célula) em milissegundos:\n")
        print(f"  {'Algoritmo':<28} {'Complexidade':<12} {'Tipo':<8}{header}")
        print(f"  {'-'*80}")

        for alg_name, complexity, alg_type, alg_fn in algorithms:
            row = f"  {alg_name:<28} {complexity:<12} {alg_type:<8}"
            for n in sizes:
                mp, wp = p_builder(n)
                try:
                    t0 = time.perf_counter()
                    for _ in range(RUNS):
                        alg_fn(mp, wp)
                    elapsed = (time.perf_counter() - t0) / RUNS * 1000
                    cell = f"{elapsed:.2f}ms"
                except Exception:
                    cell = "Erro"
                row += f"{cell:>{col_w}}"
            print(row)

        # Tabela de estabilidade (pares bloqueantes — deve ser 0) e acordo
        # com a referencia (wrapper numerico).
        print(f"\n  Pares bloqueantes (0 = estável) | =ref se concorda com numérico:\n")
        print(f"  {'Algoritmo':<28} {'Complexidade':<12} {'Tipo':<8}{header}")
        print(f"  {'-'*80}")

        for alg_name, complexity, alg_type, alg_fn in algorithms:
            row = f"  {alg_name:<28} {complexity:<12} {alg_type:<8}"
            for n in sizes:
                mp, wp = p_builder(n)
                try:
                    ref = _num.stable_marriage_gs_numeric(mp, wp)
                    match = alg_fn(mp, wp)
                    bp = count_blocking_pairs(mp, wp, match)
                    agree = (match == ref)
                    if bp == 0 and agree:
                        cell = "0 =ref"
                    elif bp == 0:
                        cell = "0 ≠ref"
                    else:
                        cell = f"{bp}!"
                except Exception:
                    cell = "Erro"
                row += f"{cell:>{col_w}}"
            print(row)


def run_benchmark():
    hsep = "#" * 82
    print(f"\n{hsep}")
    print(f"  SEÇÃO 1 — Todos os algoritmos  |  n = {SIZES_ALL}")
    print(f"  (OOP tem alto sobrecusto por objeto — tamanhos reduzidos)")
    print(hsep)
    _run_section(ALGORITHMS_ALL, SIZES_ALL)

    print(f"\n{hsep}")
    print(f"  SEÇÃO 2 — Apenas rápidos (numérico + Lattas)  |  n = {SIZES_FAST}")
    print(hsep)
    _run_section(ALGORITHMS_FAST, SIZES_FAST)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 82)
    print("  BENCHMARK — PROBLEMA DO CASAMENTO ESTÁVEL (STABLE MARRIAGE)")
    print("  Gale-Shapley men-optimal | Todos os algoritmos | Todos os perfis")
    print("=" * 82)
    run_benchmark()
