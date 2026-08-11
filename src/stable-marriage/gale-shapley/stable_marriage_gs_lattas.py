"""
Problema do Casamento Estavel (Stable Marriage Problem)
Algoritmo: Gale-Shapley (Aceitacao Diferida) - implementacao baseada em dicionarios

Complexidade de tempo: O(n^2)  (com sobrecusto de .index() em listas)
Tipo: Exato (sempre encontra um emparelhamento estavel)

Descricao:
    Adaptacao da implementacao de Alexandros Lattas (StableMarriages). O
    algoritmo mantem dicionarios de noivado por NOME: cada homem livre propoe
    a primeira mulher restante na sua lista (que e consumida com pop(0)); a
    mulher aceita se preferir o novo pretendente ao atual, comparando posicoes
    via .index() na sua lista de preferencia. Produz o emparelhamento OTIMO
    PARA OS HOMENS (men-optimal).

Implementacao:
    Diferente dos wrappers do pacote pip, este NAO importa de repository/.
    O arquivo original (StableMarriages.py) faz parsing de sys.argv e le/escreve
    arquivos JSON no nivel de modulo, chamando sys.exit() durante o import — o
    que impede o carregamento por importlib. A funcao central GS() foi adaptada
    fielmente aqui (mesma logica de noivado por dicionario), seguindo o
    precedente dos wrappers SSP e bottleneck deste projeto.

Fonte original (algoritmo):
    Alexandros Lattas — StableMarriages
    repository/stable-marriage/gale-shapley/StableMarriages/src/StableMarriages.py
    Funcao GS(DATA, FIRST, SEC). Adaptada para a interface padrao do benchmark.

Interface padrao (definida em stable_marriage_benchmark.py):
    Entrada:
        men_pref[m]   : lista de indices de mulheres, em ordem de preferencia.
        women_pref[w] : lista de indices de homens, em ordem de preferencia.
    Saida:
        match : lista onde match[m] = w (homem m casado com a mulher w).
"""


def _get_husband(woman, couples):
    """Encontra o homem atualmente noivo da mulher dada (ou None)."""
    for man in couples:
        if couples[man] == woman:
            return man
    return None


def _gs(first_pref, second_pref):
    """
    Nucleo do GS de Lattas, adaptado para dicionarios por nome.

    first_pref  : {homem: [mulheres em ordem de preferencia]}  (lado que propoe)
    second_pref : {mulher: [homens em ordem de preferencia]}   (lado que dispoe)

    As listas de first_pref sao CONSUMIDAS (pop) — passe copias.
    Retorna couples: {homem: mulher}.
    """
    couples_count = len(first_pref)
    couples = {}
    engaged_first = {name: 0 for name in first_pref}
    engaged_second = {name: 0 for name in second_pref}

    stable = 1
    while len(couples) < couples_count or not stable:
        stable = 1
        for name in first_pref:
            if not engaged_first[name]:
                w = first_pref[name][0]
                first_pref[name].pop(0)
                if not engaged_second[w]:
                    couples[name] = w
                    engaged_second[w] = 1
                    engaged_first[name] = 1
                else:
                    mm = _get_husband(w, couples)
                    if second_pref[w].index(name) < second_pref[w].index(mm):
                        stable = 0
                        couples[name] = w
                        del couples[mm]
                        engaged_first[name] = 1
                        engaged_first[mm] = 0
    return couples


def stable_marriage_gs_lattas(men_pref, women_pref):
    """
    Resolve o Problema do Casamento Estavel (men-optimal) via GS de Lattas.

    Parametros:
        men_pref   : lista de listas de indices (preferencias dos homens).
        women_pref : lista de listas de indices (preferencias das mulheres).

    Retorno:
        match : lista onde match[m] = w (homem m -> mulher w).
    """
    n = len(men_pref)

    # Converte para dicionarios por nome; copia as listas dos homens pois GS as consome.
    first_pref = {f"m{m}": [f"w{w}" for w in men_pref[m]] for m in range(n)}
    second_pref = {f"w{w}": [f"m{m}" for m in women_pref[w]] for w in range(n)}

    couples = _gs(first_pref, second_pref)

    match = [-1] * n
    for man_name, woman_name in couples.items():
        m = int(man_name[1:])
        w = int(woman_name[1:])
        match[m] = w
    return match


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

    match = stable_marriage_gs_lattas(men_pref, women_pref)
    print("=== Casamento Estavel — Gale-Shapley (Lattas / dicionarios) ===")
    print(f"Emparelhamento (men-optimal): {match}")
    for m, w in enumerate(match):
        print(f"  Homem {m} <-> Mulher {w}")
