"""
Emparelhamento em Grafos Gerais — baselines de biblioteca (NetworkX)

Tipo: Baseline (exato). Linguagem: Python puro.

Descrição:
    Baselines de biblioteca madura para emparelhamento em grafos gerais.
    Encapsulam `networkx.max_weight_matching`, que resolve emparelhamento de
    peso máximo (e, com `maxcardinality=True`, cardinalidade máxima) em grafos
    gerais pelo algoritmo de Edmonds.

    NOTA DE LINHAGEM (decisão D9): o `max_weight_matching` do NetworkX é um PORT
    do `mwmatching.py` de Joris van Rantwijk — a mesma base de código adaptada
    no wrapper `general_weighted_vanrantwijk`. Portanto, ao comparar os dois, NÃO
    se comparam duas abordagens independentes, e sim uma implementação contra seu
    próprio descendente empacotado. Isso mede endurecimento de engenharia de
    biblioteca a algoritmo e código de origem fixos, e deve ser declarado no
    capítulo de Resultados.

Fonte:
    NetworkX — networkx.algorithms.matching.max_weight_matching.
Requer: networkx.
"""

import networkx as nx


def _monta_grafo(n, edges, com_peso):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for e in edges:
        if com_peso:
            u, v, w = e
            if u != v:
                G.add_edge(u, v, weight=w)
        else:
            u, v = e
            if u != v:
                G.add_edge(u, v)
    return G


def max_cardinality_matching_networkx(n, edges):
    """Cardinalidade máxima em grafo geral. Retorno: (size, matching)."""
    G = _monta_grafo(n, edges, com_peso=False)
    mate = nx.max_weight_matching(G, maxcardinality=True)
    matching = sorted((min(a, b), max(a, b)) for a, b in mate)
    return len(matching), matching


def max_weight_matching_networkx(n, edges):
    """Peso máximo em grafo geral. Retorno: (total_weight, matching)."""
    G = _monta_grafo(n, edges, com_peso=True)
    mate = nx.max_weight_matching(G)
    matching = sorted((min(a, b), max(a, b)) for a, b in mate)
    total = sum(G[a][b]["weight"] for a, b in matching)
    return total, matching


if __name__ == "__main__":
    print("card C5:", max_cardinality_matching_networkx(5, [(0,1),(1,2),(2,3),(3,4),(4,0)]))
    print("peso:", max_weight_matching_networkx(4, [(0,1,1),(1,2,3),(2,3,1)]))
