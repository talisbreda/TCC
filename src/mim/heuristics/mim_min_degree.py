"""
Emparelhamento Induzido Máximo (MIM) — Heurística Guloso de Grau Mínimo

Complexidade de tempo:  O(E^2)
Complexidade de espaço: O(E^2) para o grafo de conflitos
Tipo: Heurística (aproximada)

Descrição:
    Constrói o grafo de conflitos entre arestas (compartilham vértice ou têm
    aresta cruzada). A cada passo escolhe a aresta de MENOR GRAU no grafo de
    conflitos residual -- a que bloqueia menos opções futuras -- adiciona-a ao
    emparelhamento induzido e remove ela e seus conflitos. É a adaptação da
    heurística "minimum degree greedy" para Conjunto Independente Máximo, que
    tem melhor qualidade média que a escolha aleatória.

Fonte:
    Halldórsson & Radhakrishnan, "Greed is good: approximating independent sets
    in sparse and bounded-degree graphs" (1997); aplicado ao grafo de conflitos
    do MIM.
"""


def mim_min_degree(n, edges):
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
    m = len(E)
    if m == 0:
        return 0, []

    arestas_set = set(E)

    def cruza(e1, e2):
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) < 4:
            return True
        for x in (a, b):
            for y in (c, d):
                if (min(x, y), max(x, y)) in arestas_set:
                    return True
        return False

    conflito = [set() for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            if cruza(E[i], E[j]):
                conflito[i].add(j)
                conflito[j].add(i)

    ativo = [True] * m
    grau = [len(conflito[i]) for i in range(m)]
    escolhidas = []

    for _ in range(m):
        # menor grau entre os ativos
        cand = -1
        for i in range(m):
            if ativo[i] and (cand == -1 or grau[i] < grau[cand]):
                cand = i
        if cand == -1:
            break
        escolhidas.append(cand)
        # remove cand e seus conflitos
        remover = {cand} | {j for j in conflito[cand] if ativo[j]}
        for r in remover:
            if ativo[r]:
                ativo[r] = False
                for k in conflito[r]:
                    if ativo[k]:
                        grau[k] -= 1

    matching = sorted(E[i] for i in escolhidas)
    return len(escolhidas), matching


if __name__ == "__main__":
    print("P4:", mim_min_degree(4, [(0, 1), (1, 2), (2, 3)]))
