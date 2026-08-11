"""
Problema do Casamento Estavel (Stable Marriage Problem)
Algoritmo: Gale-Shapley (Aceitacao Diferida) - implementacao orientada a objetos

Complexidade de tempo: O(n^2)
Tipo: Exato (sempre encontra um emparelhamento estavel)

Descricao:
    Wrapper para o pacote `gale-shapley-algorithm` (versao OOP). O algoritmo
    modela cada participante como objeto Proposer/Responder com sua lista de
    preferencias; a cada rodada, cada pretendente livre propoe ao proximo da
    sua lista e cada respondente aceita/rejeita comparando com seu par atual.
    O resultado e o emparelhamento OTIMO PARA OS PRETENDENTES (men-optimal,
    pois os homens propoem).

    Esta variante usa preferencias por NOME (dicionarios) e a API publica
    create_matching(); e a interface de alto nivel do pacote.

Fonte original:
    https://github.com/.../gale-shapley-algorithm  (pacote pip, MIT-style)
    repository/stable-marriage/gale-shapley/gale-shapley-algorithm/
    Modulo: gale_shapley_algorithm (create_matching)
    Adaptado para a interface padrao do benchmark (men_pref, women_pref).

Interface padrao (definida em stable_marriage_benchmark.py):
    Entrada:
        men_pref[m]   : lista de indices de mulheres, em ordem de preferencia
                        do homem m (mais preferida primeiro).
        women_pref[w] : lista de indices de homens, em ordem de preferencia
                        da mulher w.
    Saida:
        match : lista onde match[m] = w (homem m casado com a mulher w).
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent   # TCC/
_PKG_SRC = (_ROOT / "repository" / "stable-marriage" / "gale-shapley"
            / "gale-shapley-algorithm" / "src")

# O pacote usa imports absolutos (from gale_shapley_algorithm...), entao
# precisa estar no sys.path como pacote — nao da para carregar por arquivo.
if str(_PKG_SRC) not in sys.path:
    sys.path.insert(0, str(_PKG_SRC))

from gale_shapley_algorithm import create_matching   # noqa: E402


def stable_marriage_gs_oop(men_pref, women_pref):
    """
    Resolve o Problema do Casamento Estavel (men-optimal) via Gale-Shapley OOP.

    Parametros:
        men_pref   : lista de listas de indices (preferencias dos homens).
        women_pref : lista de listas de indices (preferencias das mulheres).

    Retorno:
        match : lista onde match[m] = w (homem m -> mulher w).
    """
    n = len(men_pref)

    # Converte indices -> nomes (m0..m{n-1}, w0..w{n-1})
    proposer_prefs = {
        f"m{m}": [f"w{w}" for w in men_pref[m]] for m in range(n)
    }
    responder_prefs = {
        f"w{w}": [f"m{m}" for m in women_pref[w]] for w in range(n)
    }

    result = create_matching(proposer_prefs, responder_prefs)

    match = [-1] * n
    for man_name, woman_name in result.matches.items():
        m = int(man_name[1:])
        w = int(woman_name[1:])
        match[m] = w
    return match


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Exemplo classico (Mike/Harvey/...): 4 homens, 4 mulheres por indice
    men_pref = [
        [0, 2, 1, 3],   # m0
        [1, 2, 0, 3],   # m1
        [3, 1, 2, 0],   # m2
        [0, 2, 1, 3],   # m3
    ]
    women_pref = [
        [0, 3, 1, 2],   # w0
        [1, 2, 0, 3],   # w1
        [0, 1, 2, 3],   # w2
        [2, 3, 1, 0],   # w3
    ]

    match = stable_marriage_gs_oop(men_pref, women_pref)
    print("=== Casamento Estavel — Gale-Shapley (OOP / pacote pip) ===")
    print(f"Emparelhamento (men-optimal): {match}")
    for m, w in enumerate(match):
        print(f"  Homem {m} <-> Mulher {w}")
