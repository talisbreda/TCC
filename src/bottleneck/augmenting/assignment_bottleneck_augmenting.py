"""
Problema de Atribuicao Gargalo (Bottleneck Assignment Problem - LBAP)
Algoritmo: Caminhos aumentantes com Dijkstra de gargalo

Complexidade de tempo:  O(n^3)  (n aumentos, cada Dijkstra de gargalo O(n^2))
Complexidade de espaco: O(n^2)  (matriz de custos densa)
Tipo: Exato

Descricao:
    Metodo construtivo (Burkard, Dell'Amico & Martello, "Assignment Problems").
    Diferente do metodo de threshold (que faz busca binaria sobre um limiar
    global), este constroi o emparelhamento aumentando a cardinalidade um par
    por vez. Para cada linha livre, procura um caminho aumentante ate uma coluna
    livre cuja CAPACIDADE -- a aresta de maior peso no caminho -- seja minima.

    A busca e uma adaptacao de Dijkstra em que o rotulo de um vertice nao e a
    soma dos pesos, mas o gargalo (maximo) ao longo do caminho:

        NovoCusto_v = max(d_u, c_{u,v})

    e a cada passo expande-se o vertice de menor rotulo. Ao alcancar uma coluna
    livre, inverte-se o caminho (aumento). Repetindo ate um emparelhamento
    perfeito, o custo gargalo otimo e o maximo peso presente no emparelhamento
    final.

    Implementacao fiel ao pseudo-codigo do capitulo de atribuicao gargalo
    (Algoritmo "LBAP usando caminhos aumentantes"). So conta as arestas
    "para frente" (linha -> coluna), que sao as que permanecem no
    emparelhamento; as arestas casadas percorridas de volta sao removidas no
    aumento.

Fonte:
    R. E. Burkard, M. Dell'Amico, S. Martello, "Assignment Problems", SIAM,
    2009 -- capitulo do Linear Bottleneck Assignment Problem.

Entrada:
    Matriz de custos n x n (lista de listas). Minimizacao do custo maximo.
"""

import heapq


def assignment_bottleneck_augmenting(cost_matrix):
    """
    Resolve o Problema de Atribuicao Gargalo por caminhos aumentantes.

    Parametros:
        cost_matrix : matriz de custos n x n (lista de listas).

    Retorno:
        bottleneck_cost : custo maximo na atribuicao otima
        assignment      : lista onde assignment[i] = j (trabalhador i -> tarefa j)
    """
    n = len(cost_matrix)
    if n == 0:
        return 0, []

    match_left = [-1] * n   # match_left[i]  = j
    match_right = [-1] * n  # match_right[j] = i

    INF = float("inf")

    for s in range(n):
        # Dijkstra de gargalo a partir da linha livre s.
        dist = [INF] * n     # dist[j] = menor gargalo para alcancar a coluna j
        prev = [-1] * n      # prev[j] = linha que alcanca j pela aresta "para frente"
        visited = [False] * n
        pq = []
        for j in range(n):
            d = cost_matrix[s][j]
            if d < dist[j]:
                dist[j] = d
                prev[j] = s
                heapq.heappush(pq, (d, j))

        alvo = -1
        while pq:
            d, j = heapq.heappop(pq)
            if visited[j]:
                continue
            visited[j] = True
            if match_right[j] == -1:
                alvo = j          # coluna livre: caminho aumentante encontrado
                break
            w = match_right[j]    # linha casada com j; segue por arestas w -> j2
            for j2 in range(n):
                if not visited[j2]:
                    nd = d if d > cost_matrix[w][j2] else cost_matrix[w][j2]  # max
                    if nd < dist[j2]:
                        dist[j2] = nd
                        prev[j2] = w
                        heapq.heappush(pq, (nd, j2))

        # Aumento: inverte o caminho alternante que termina na coluna livre alvo.
        j = alvo
        while j != -1:
            w = prev[j]
            proxima = match_left[w]   # coluna que w tinha antes (ou -1 se w == s)
            match_left[w] = j
            match_right[j] = w
            j = proxima

    bottleneck_cost = max(cost_matrix[i][match_left[i]] for i in range(n))
    return bottleneck_cost, match_left


if __name__ == "__main__":
    cost = [
        [9, 2, 7],
        [3, 6, 4],
        [1, 8, 5],
    ]
    bc, asgn = assignment_bottleneck_augmenting(cost)
    print("=== Atribuicao Gargalo (caminhos aumentantes) ===")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuicao: {asgn}")
    print(f"Custo gargalo (maximo na atribuicao): {bc}")

    # Exemplo 2: gargalo esperado = 3
    cost2 = [
        [9, 3, 3],
        [2, 8, 6],
        [5, 1, 7],
    ]
    bc2, asgn2 = assignment_bottleneck_augmenting(cost2)
    print(f"\nExemplo 2 -- custo gargalo: {bc2}  (esperado: 3)")
