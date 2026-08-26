"""
Emparelhamento de Cardinalidade Máxima em Grafos Bipartidos
Algoritmo: Heurística Gulosa Simples

Complexidade de tempo:  O(E)
Complexidade de espaço: O(V) para os vetores match_left / match_right
Tipo: Heurística (aproximada)

Descrição:
    Percorre as arestas em uma única passada, na ordem em que aparecem na
    lista de entrada. Para cada aresta (u, v), se ambos os vértices ainda
    estão livres, o par é adicionado ao emparelhamento e os dois vértices
    são marcados como ocupados.

    O resultado é sempre um emparelhamento MAXIMAL (nenhuma aresta pode ser
    adicionada sem violar a restrição de emparelhamento), porém não
    necessariamente MÁXIMO: sua cardinalidade pode ser menor que a ótima.
    É bem conhecido que qualquer emparelhamento maximal tem pelo menos
    metade da cardinalidade do máximo, ou seja, esta heurística é uma
    2-aproximação.

    Como cada aresta é examinada uma única vez e cada teste/atualização é
    O(1), o tempo total é O(E).

Fonte:
    Heurística gulosa clássica para emparelhamento maximal. Ver:
    T. H. Cormen, C. E. Leiserson, R. L. Rivest, C. Stein,
    "Introduction to Algorithms", 3ª ed., MIT Press, 2009 — noção de
    emparelhamento maximal e sua relação com o emparelhamento máximo.

Representação do grafo:
    - edges: lista de tuplas (u, v)
    - Vértices esquerdo: 0..n_left-1
    - Vértices direito:  0..n_right-1
"""


# ---------------------------------------------------------------------------
# Interface padrão do benchmark
# ---------------------------------------------------------------------------

def max_cardinality_matching_greedy(n_left, n_right, edges):
    """
    Encontra um emparelhamento MAXIMAL em um grafo bipartido pela heurística
    gulosa simples (uma passada sobre as arestas).

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
    match_left  = [-1] * n_left
    match_right = [-1] * n_right
    matching_size = 0

    # Uma única passada: adiciona (u, v) sempre que ambos estiverem livres.
    for u, v in edges:
        if match_left[u] == -1 and match_right[v] == -1:
            match_left[u]  = v
            match_right[v] = u
            matching_size += 1

    return matching_size, match_left, match_right


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Grafo bipartido:
    #   Esquerdo: 0, 1, 2
    #   Direito:  0, 1, 2
    #   Arestas:  (0,0), (0,1), (1,0), (2,1), (2,2)
    # O emparelhamento MÁXIMO tem tamanho 3.
    # A gulosa, nesta ordem, casa (0,0) e (2,1) e para com tamanho 2,
    # pois o vértice esquerdo 1 só alcança o direito 0 (já ocupado).

    n_left = 3
    n_right = 3
    edges = [(0, 0), (0, 1), (1, 0), (2, 1), (2, 2)]

    size, match_left, match_right = max_cardinality_matching_greedy(
        n_left, n_right, edges
    )

    print("=== Heurística Gulosa Simples ===")
    print(f"Cardinalidade do emparelhamento encontrado: {size}  (ótimo = 3)")
    print(f"match_left  (esquerdo -> direito): {match_left}")
    print(f"match_right (direito  -> esquerdo): {match_right}")
    print("Pares no emparelhamento:")
    for u in range(n_left):
        if match_left[u] != -1:
            print(f"  Esquerdo {u} <-> Direito {match_left[u]}")
