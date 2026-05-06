"""
Emparelhamento de Cardinalidade Máxima em Grafos Bipartidos
Algoritmo: Caminhos Aumentantes (BFS)

Complexidade de tempo: O(V·E)
Tipo: Exato

Descrição:
    Encontra o emparelhamento máximo em um grafo bipartido por meio de
    caminhos aumentantes. Inicia com um emparelhamento guloso e itera
    chamando update_matching, que realiza uma BFS a partir de todos os
    vértices livres do lado esquerdo para encontrar um caminho aumentante.
    O processo repete até que não exista mais nenhum caminho aumentante.

    Cada chamada a update_matching percorre no máximo todas as arestas (O(E)),
    e o número de iterações é limitado pelo tamanho do emparelhamento ótimo
    (O(V)), resultando em complexidade total O(V·E).

Fonte original:
    wbchristerson — https://github.com/wbchristerson/perfect-matchings
    Arquivo: GraphAlgorithm.py
    Adaptado para a interface padrão do benchmark (n_left, n_right, edges).

Representação do grafo:
    - edges: lista de tuplas (u, v)
    - Vértices esquerdo: 0..n_left-1
    - Vértices direito:  0..n_right-1
"""

import importlib.util
from pathlib import Path

# Carrega GraphAlgorithm.py diretamente pelo caminho (diretório contém hífens)
_src = (Path(__file__).parent.parent.parent.parent
        / "repository" / "mcm" / "augmenting" / "perfect-matchings" / "GraphAlgorithm.py")
_spec = importlib.util.spec_from_file_location("GraphAlgorithm", _src)
_ga   = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ga)


# ---------------------------------------------------------------------------
# Interface padrão do benchmark
# ---------------------------------------------------------------------------

def max_cardinality_matching_augmenting_paths_wbchristerson(n_left, n_right, edges):
    """
    Encontra o emparelhamento máximo em um grafo bipartido.

    Parâmetros:
        n_left  : número de vértices no lado esquerdo (U)
        n_right : número de vértices no lado direito (V)
        edges   : lista de tuplas (u, v) com u in [0, n_left) e v in [0, n_right)

    Retorno:
        matching_size : cardinalidade do emparelhamento encontrado
        match_left    : vetor onde match_left[u] = v se (u,v) está no emparelhamento,
                        -1 se u está livre
        match_right   : vetor onde match_right[v] = u se (u,v) está no emparelhamento,
                        -1 se v está livre
    """
    left_neighbors = [[] for _ in range(n_left)]
    for u, v in edges:
        left_neighbors[u].append(v)

    matching_pairs = _ga.maximum_matching(n_left, n_right, left_neighbors)

    match_left  = [-1] * n_left
    match_right = [-1] * n_right
    for a, b in matching_pairs:
        match_left[a]  = b
        match_right[b] = a

    return len(matching_pairs), match_left, match_right


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Grafo bipartido:
    #   Esquerdo: 0, 1, 2
    #   Direito:  0, 1, 2
    #   Arestas:  (0,0), (0,1), (1,0), (2,1), (2,2)
    # Ótimo tem tamanho 3.

    n_left = 3
    n_right = 3
    edges = [(0, 0), (0, 1), (1, 0), (2, 1), (2, 2)]

    size, match_left, match_right = max_cardinality_matching_augmenting_paths_wbchristerson(
        n_left, n_right, edges
    )

    print("=== Caminhos Aumentantes (wbchristerson) ===")
    print(f"Cardinalidade do emparelhamento encontrado: {size}")
    print(f"match_left  (esquerdo -> direito): {match_left}")
    print(f"match_right (direito  -> esquerdo): {match_right}")
    print("Pares no emparelhamento:")
    for u in range(n_left):
        if match_left[u] != -1:
            print(f"  Esquerdo {u} <-> Direito {match_left[u]}")

    print()

    # Exemplo com grafo desconexo (alguns vértices livres)
    n_left2 = 4
    n_right2 = 4
    edges2 = [(0, 0), (1, 0), (1, 1), (2, 2), (3, 3)]

    size2, ml2, mr2 = max_cardinality_matching_augmenting_paths_wbchristerson(
        n_left2, n_right2, edges2
    )
    print(f"Exemplo 2 — tamanho: {size2}  (ótimo = 4)")
    for u in range(n_left2):
        if ml2[u] != -1:
            print(f"  Esquerdo {u} <-> Direito {ml2[u]}")
