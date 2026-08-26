"""
Emparelhamento Induzido Máximo (MIM) — Heurística Gulosa Aleatória

Complexidade de tempo:  O(E^2) no pior caso
Complexidade de espaço: O(V + E)
Tipo: Heurística (aproximada)

Descrição:
    Percorre as arestas em ordem aleatória fixa (semente). Para cada aresta
    ainda "livre", adiciona-a ao emparelhamento induzido e bloqueia todas as
    arestas em conflito (que compartilham vértice ou têm aresta cruzada com a
    escolhida). O resultado é sempre um emparelhamento induzido MAXIMAL.

Fonte:
    Heurística gulosa clássica para conjunto independente / emparelhamento
    induzido (ver Cameron, 1989, para a definição do problema).
"""

import random


def mim_greedy_random(n, edges, seed=42):
    """Retorno: (matching_size, matching) com matching = lista de (u,v), u<v."""
    E = []
    vistas = set()
    for u, v in edges:
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in vistas:
            vistas.add((a, b))
            E.append((a, b))
    if not E:
        return 0, []

    arestas_set = set(E)

    def cruza(e1, e2):
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) < 4:
            return True  # compartilha vértice
        for x in (a, b):
            for y in (c, d):
                if (min(x, y), max(x, y)) in arestas_set:
                    return True
        return False

    ordem = list(range(len(E)))
    random.Random(seed).shuffle(ordem)

    bloqueada = [False] * len(E)
    escolhidas = []
    for idx in ordem:
        if bloqueada[idx]:
            continue
        escolhidas.append(idx)
        bloqueada[idx] = True
        for j in range(len(E)):
            if not bloqueada[j] and cruza(E[idx], E[j]):
                bloqueada[j] = True

    matching = sorted(E[i] for i in escolhidas)
    return len(escolhidas), matching


if __name__ == "__main__":
    print("P4:", mim_greedy_random(4, [(0, 1), (1, 2), (2, 3)]))
