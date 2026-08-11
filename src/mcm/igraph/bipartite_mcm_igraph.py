"""
Emparelhamento de Cardinalidade Maxima em Grafos Bipartidos
Algoritmo: Emparelhamento bipartido maximo (baseline de biblioteca — igraph)

Complexidade de tempo: O(E·√V)  (push-relabel / caminhos aumentantes, nucleo em C)
Tipo: Exato

Descricao:
    Baseline de biblioteca madura com nucleo em C. Usa
    igraph.Graph.maximum_bipartite_matching() como ponto de comparacao para os
    wrappers obtidos de repositorios externos. Por ter o nucleo compilado,
    tende a ser o mais rapido em grafos grandes.

    Diferente dos demais wrappers do projeto, este NAO adapta codigo de
    repository/: encapsula uma biblioteca instalada via pip.

Fonte:
    igraph — https://igraph.org/python/
    igraph.Graph.maximum_bipartite_matching
    Adaptado para a interface padrao do benchmark (n_left, n_right, edges).

Requer: igraph.

Representacao do grafo:
    - edges: lista de tuplas (u, v)
    - Vertices esquerdo: 0..n_left-1   |  direito: 0..n_right-1
    Internamente, vertices direitos sao deslocados por n_left (igraph usa um
    unico espaco de ids de vertice com atributo booleano `types`).
"""

import igraph as ig


def max_cardinality_matching_igraph(n_left, n_right, edges):
    """
    Encontra o emparelhamento maximo em um grafo bipartido via igraph.

    Parametros:
        n_left  : numero de vertices no lado esquerdo (U)
        n_right : numero de vertices no lado direito (V)
        edges   : lista de tuplas (u, v) com u in [0, n_left) e v in [0, n_right)

    Retorno:
        matching_size : cardinalidade do emparelhamento encontrado
        match_left    : match_left[u] = v, ou -1 se u esta livre
        match_right   : match_right[v] = u, ou -1 se v esta livre
    """
    # types: False para os n_left vertices esquerdos, True para os n_right direitos.
    types = [False] * n_left + [True] * n_right
    ig_edges = [(u, n_left + v) for (u, v) in edges]

    g = ig.Graph.Bipartite(types, ig_edges)
    matching = g.maximum_bipartite_matching()

    match_left = [-1] * n_left
    match_right = [-1] * n_right
    for u in range(n_left):
        mate = matching.match_of(u)   # id do vertice direito, ou -1
        if mate is not None and mate != -1:
            v = mate - n_left
            match_left[u] = v
            match_right[v] = u

    matching_size = sum(1 for x in match_left if x != -1)
    return matching_size, match_left, match_right


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    n_left = 3
    n_right = 3
    edges = [(0, 0), (0, 1), (1, 0), (2, 1), (2, 2)]

    size, match_left, match_right = max_cardinality_matching_igraph(
        n_left, n_right, edges
    )

    print("=== Emparelhamento bipartido maximo (baseline igraph) ===")
    print(f"Cardinalidade do emparelhamento encontrado: {size}")
    print(f"match_left  (esquerdo -> direito): {match_left}")
    print(f"match_right (direito  -> esquerdo): {match_right}")
