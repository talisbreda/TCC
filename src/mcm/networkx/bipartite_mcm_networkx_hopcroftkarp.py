"""
Emparelhamento de Cardinalidade Maxima em Grafos Bipartidos
Algoritmo: Hopcroft-Karp (baseline de biblioteca — NetworkX)

Complexidade de tempo: O(E·√V)
Tipo: Exato

Descricao:
    Baseline de biblioteca madura. Usa a implementacao de Hopcroft-Karp do
    NetworkX (networkx.algorithms.bipartite.hopcroft_karp_matching) como ponto
    de comparacao para os wrappers obtidos de repositorios externos.

    Diferente dos demais wrappers do projeto, este NAO adapta codigo de
    repository/: ele encapsula uma biblioteca instalada via pip. Serve como
    referencia de desempenho/corretude de uma implementacao consolidada.

Fonte:
    NetworkX — https://networkx.org/
    networkx.algorithms.bipartite.matching.hopcroft_karp_matching
    Adaptado para a interface padrao do benchmark (n_left, n_right, edges).

Requer: networkx.

Representacao do grafo:
    - edges: lista de tuplas (u, v)
    - Vertices esquerdo: 0..n_left-1   |  direito: 0..n_right-1
"""

import networkx as nx
from networkx.algorithms import bipartite


def max_cardinality_matching_networkx_hopcroftkarp(n_left, n_right, edges):
    """
    Encontra o emparelhamento maximo em um grafo bipartido via NetworkX.

    Parametros:
        n_left  : numero de vertices no lado esquerdo (U)
        n_right : numero de vertices no lado direito (V)
        edges   : lista de tuplas (u, v) com u in [0, n_left) e v in [0, n_right)

    Retorno:
        matching_size : cardinalidade do emparelhamento encontrado
        match_left    : match_left[u] = v, ou -1 se u esta livre
        match_right   : match_right[v] = u, ou -1 se v esta livre
    """
    # Rotula os lados distintamente (L_i / R_j) para evitar colisao.
    left_nodes = [f"L{u}" for u in range(n_left)]

    G = nx.Graph()
    G.add_nodes_from(left_nodes, bipartite=0)
    G.add_nodes_from([f"R{v}" for v in range(n_right)], bipartite=1)
    for u, v in edges:
        G.add_edge(f"L{u}", f"R{v}")

    # hopcroft_karp_matching retorna o emparelhamento nos DOIS sentidos
    # (L->R e R->L); top_nodes garante a orientacao em grafos desconexos.
    matching_dict = bipartite.hopcroft_karp_matching(G, top_nodes=left_nodes)

    match_left = [-1] * n_left
    match_right = [-1] * n_right
    for key, val in matching_dict.items():
        if key.startswith("L"):
            u = int(key[1:])
            v = int(val[1:])
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

    size, match_left, match_right = max_cardinality_matching_networkx_hopcroftkarp(
        n_left, n_right, edges
    )

    print("=== Hopcroft-Karp (baseline NetworkX) ===")
    print(f"Cardinalidade do emparelhamento encontrado: {size}")
    print(f"match_left  (esquerdo -> direito): {match_left}")
    print(f"match_right (direito  -> esquerdo): {match_right}")
