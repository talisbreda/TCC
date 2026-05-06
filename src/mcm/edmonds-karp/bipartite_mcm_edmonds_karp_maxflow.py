"""
Emparelhamento de Cardinalidade Máxima em Grafos Bipartidos
Algoritmo: Edmonds-Karp (Ford-Fulkerson com BFS)

Complexidade de tempo: O(V·E²)
Tipo: Exato

Descrição:
    Reduz o problema de emparelhamento máximo a um problema de fluxo máximo:
    conecta uma fonte (s) a todos os vértices esquerdos com capacidade 1,
    adiciona as arestas do grafo bipartido com capacidade 1, e conecta todos
    os vértices direitos a um sumidouro (t) com capacidade 1. O fluxo máximo
    de s a t equivale ao emparelhamento máximo.

    O algoritmo de Edmonds-Karp implementa Ford-Fulkerson usando BFS para
    encontrar o caminho aumentante de comprimento mínimo a cada iteração,
    garantindo O(V·E) iterações e complexidade total O(V·E²).

Fonte original:
    Autor desconhecido — Maxflow-Algorithms/Edmonds-Karp Algorithm.py
    (código Python 2; portado para Python 3 neste wrapper)
    Adaptado para a interface padrão do benchmark (n_left, n_right, edges).

Representação do grafo:
    - edges: lista de tuplas (u, v)
    - Vértices esquerdo: 0..n_left-1
    - Vértices direito:  0..n_right-1
"""


# ---------------------------------------------------------------------------
# Algoritmo original (Python 2 → 3): max_flow + bfs
# Alterações em relação ao original:
#   - xrange substituído por range
#   - instrução print removida (era saída de depuração)
# ---------------------------------------------------------------------------

def _bfs(C, F, s, t):
    queue = [s]
    paths = {s: []}
    if s == t:
        return paths[s]
    while queue:
        u = queue.pop(0)
        for v in range(len(C)):
            if (C[u][v] - F[u][v] > 0) and v not in paths:
                paths[v] = paths[u] + [(u, v)]
                if v == t:
                    return paths[v]
                queue.append(v)
    return None


def _max_flow(C, s, t):
    n = len(C)
    F = [[0] * n for _ in range(n)]
    path = _bfs(C, F, s, t)
    while path is not None:
        flow = min(C[u][v] - F[u][v] for u, v in path)
        for u, v in path:
            F[u][v] += flow
            F[v][u] -= flow
        path = _bfs(C, F, s, t)
    return F


# ---------------------------------------------------------------------------
# Interface padrão do benchmark
# ---------------------------------------------------------------------------

def max_cardinality_matching_edmonds_karp_maxflow(n_left, n_right, edges):
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
    # Layout de nós na matriz de capacidade:
    #   0..n_left-1          → vértices esquerdos
    #   n_left..n_left+n_right-1 → vértices direitos
    #   n_left + n_right     → fonte (s)
    #   n_left + n_right + 1 → sumidouro (t)
    total = n_left + n_right + 2
    s     = n_left + n_right
    t     = n_left + n_right + 1

    C = [[0] * total for _ in range(total)]

    for u in range(n_left):
        C[s][u] = 1

    for u, v in edges:
        C[u][n_left + v] = 1

    for v in range(n_right):
        C[n_left + v][t] = 1

    F = _max_flow(C, s, t)

    match_left  = [-1] * n_left
    match_right = [-1] * n_right
    for u in range(n_left):
        for v in range(n_right):
            if F[u][n_left + v] == 1:
                match_left[u]  = v
                match_right[v] = u

    matching_size = sum(1 for u in range(n_left) if match_left[u] != -1)
    return matching_size, match_left, match_right


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

    size, match_left, match_right = max_cardinality_matching_edmonds_karp_maxflow(
        n_left, n_right, edges
    )

    print("=== Edmonds-Karp / Max-Flow (Maxflow-Algorithms) ===")
    print(f"Cardinalidade do emparelhamento encontrado: {size}")
    print(f"match_left  (esquerdo -> direito): {match_left}")
    print(f"match_right (direito  -> esquerdo): {match_right}")
    print("Pares no emparelhamento:")
    for u in range(n_left):
        if match_left[u] != -1:
            print(f"  Esquerdo {u} <-> Direito {match_left[u]}")

    print()

    # Grafo com vértices livres (sem emparelhamento perfeito)
    n_left2, n_right2 = 4, 4
    edges2 = [(0, 0), (1, 0), (1, 1), (2, 2), (3, 3)]
    size2, ml2, _ = max_cardinality_matching_edmonds_karp_maxflow(n_left2, n_right2, edges2)
    print(f"Exemplo 2 — tamanho: {size2}  (ótimo = 4)")
    for u in range(n_left2):
        if ml2[u] != -1:
            print(f"  Esquerdo {u} <-> Direito {ml2[u]}")
