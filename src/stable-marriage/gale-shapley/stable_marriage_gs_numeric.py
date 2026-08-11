"""
Problema do Casamento Estavel (Stable Marriage Problem)
Algoritmo: Gale-Shapley (Aceitacao Diferida) - implementacao numerica (NumPy)

Complexidade de tempo: O(n^2)
Tipo: Exato (sempre encontra um emparelhamento estavel)

Descricao:
    Wrapper para o subpacote `numeric` do pacote `gale-shapley-algorithm`.
    Esta variante opera sobre MATRIZES DE RANK em NumPy: a entrada e a posicao
    (1-indexada) de cada par na lista de preferencias do outro, em vez de
    listas de objetos. O laco principal (McVitie-Wilson sequencial sobre o
    conjunto de pretendentes livres) e o mesmo do algoritmo OOP, mas com
    acesso vetorizado as preferencias, resultando em melhor desempenho em n
    grande. O resultado e o emparelhamento OTIMO PARA OS PRETENDENTES.

    Diferenca em relacao ao wrapper OOP: nao usa objetos Proposer/Responder
    nem nomes; trabalha diretamente com arrays de inteiros.

Fonte original:
    https://github.com/.../gale-shapley-algorithm  (pacote pip, MIT-style)
    repository/stable-marriage/gale-shapley/gale-shapley-algorithm/
    Modulo: gale_shapley_algorithm.numeric.gs (men_optimal_gs)
    Adaptado para a interface padrao do benchmark (men_pref, women_pref).

Requer: numpy.

Interface padrao (definida em stable_marriage_benchmark.py):
    Entrada:
        men_pref[m]   : lista de indices de mulheres, em ordem de preferencia.
        women_pref[w] : lista de indices de homens, em ordem de preferencia.
    Saida:
        match : lista onde match[m] = w (homem m casado com a mulher w).
"""

import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).parent.parent.parent.parent   # TCC/
_PKG_SRC = (_ROOT / "repository" / "stable-marriage" / "gale-shapley"
            / "gale-shapley-algorithm" / "src")

if str(_PKG_SRC) not in sys.path:
    sys.path.insert(0, str(_PKG_SRC))

from gale_shapley_algorithm.numeric.gs import men_optimal_gs   # noqa: E402


def _pref_order_to_rank_matrix(pref):
    """
    Converte listas de ordem de preferencia em matriz de rank (1-indexada).

    pref[i] = [j0, j1, ...] (j0 = mais preferido)  ->
    rank[i][j] = posicao (1..n) de j na lista de i.
    """
    n = len(pref)
    rank = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for pos, j in enumerate(pref[i]):
            rank[i][j] = pos + 1
    return rank


def stable_marriage_gs_numeric(men_pref, women_pref):
    """
    Resolve o Problema do Casamento Estavel (men-optimal) via Gale-Shapley NumPy.

    Parametros:
        men_pref   : lista de listas de indices (preferencias dos homens).
        women_pref : lista de listas de indices (preferencias das mulheres).

    Retorno:
        match : lista onde match[m] = w (homem m -> mulher w).
    """
    men_rank = _pref_order_to_rank_matrix(men_pref)
    women_rank = _pref_order_to_rank_matrix(women_pref)

    result = men_optimal_gs(men_rank, women_rank)   # array: match[m] = w
    return [int(w) for w in result]


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    men_pref = [
        [0, 2, 1, 3],
        [1, 2, 0, 3],
        [3, 1, 2, 0],
        [0, 2, 1, 3],
    ]
    women_pref = [
        [0, 3, 1, 2],
        [1, 2, 0, 3],
        [0, 1, 2, 3],
        [2, 3, 1, 0],
    ]

    match = stable_marriage_gs_numeric(men_pref, women_pref)
    print("=== Casamento Estavel — Gale-Shapley (numerico / NumPy) ===")
    print(f"Emparelhamento (men-optimal): {match}")
    for m, w in enumerate(match):
        print(f"  Homem {m} <-> Mulher {w}")
