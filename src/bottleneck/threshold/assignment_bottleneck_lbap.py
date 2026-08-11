"""
Problema de Atribuicao Gargalo (Bottleneck Assignment Problem - BAP / LBAP)
Algoritmo: Busca binaria sobre valores da matriz + verificacao por emparelhamento

Complexidade de tempo: O(n^3 log n)
    - O(n^2 log n) ordenar os n^2 valores distintos da matriz
    - O(log n) iteracoes de busca binaria (sobre valores distintos)
    - O(n^3) por verificacao de emparelhamento perfeito (DFS, pior caso)
Tipo: Exato

Descricao:
    O Problema de Atribuicao Gargalo (LBAP) encontra uma atribuicao perfeita
    que minimize o CUSTO MAXIMO entre todos os pares atribuidos. Diferente do
    Problema de Atribuicao Linear (que minimiza a SOMA dos custos), o gargalo
    minimiza o pior par individual da solucao.

    Abordagem (busca binaria sobre threshold):
    1. Coletar e ordenar todos os n^2 valores distintos da matriz.
    2. Busca binaria sobre esses valores: para cada candidato a threshold t,
       construir o grafo bipartido G_t com arestas (i,j) onde custo[i][j] <= t.
    3. Verificar se G_t possui emparelhamento perfeito usando DFS com
       caminhos aumentantes (algoritmo de Hopcroft-Karp simplificado).
    4. O menor t para o qual G_t tem emparelhamento perfeito e o custo
       gargalo otimo da solucao.

    Nota: pode existir multiplas atribuicoes otimas com o mesmo custo gargalo.
    Este wrapper retorna a primeira encontrada pela busca de caminhos aumentantes.

Implementacao:
    Diferente dos demais wrappers do projeto, este arquivo contem a
    implementacao do algoritmo diretamente, sem importar de repository/.
    O unico repositorio externo disponivel para este algoritmo e em
    JavaScript (Daniel Johnson, lbap.js, MIT License), que nao pode ser
    chamado a partir de Python. A abordagem (busca binaria + verificacao
    de emparelhamento por caminhos aumentantes) e a mesma do repositorio
    original; apenas a linguagem foi reimplementada.

    Repositorio de referencia:
    Daniel Johnson -- https://github.com/djohnson2718/Linear-Bottleneck-Assignment-Problem

Entrada:
    Matriz de custos n x n (lista de listas). Minimizacao do custo maximo.
"""


def _has_perfect_matching(cost_matrix, threshold):
    """
    Verifica se o grafo bipartido G_threshold tem emparelhamento perfeito.
    G_threshold: aresta (i,j) existe se cost_matrix[i][j] <= threshold.

    Usa DFS com caminhos aumentantes (Kuhn's algorithm).
    Retorna (True, match_left) se perfeito, (False, parcial) caso contrario.
    match_left[i] = j significa trabalhador i atribuido a tarefa j.
    """
    n = len(cost_matrix)
    match_right = [-1] * n

    def dfs(u, visited):
        for v in range(n):
            if cost_matrix[u][v] <= threshold and not visited[v]:
                visited[v] = True
                if match_right[v] == -1 or dfs(match_right[v], visited):
                    match_right[v] = u
                    return True
        return False

    matched = 0
    for u in range(n):
        if dfs(u, [False] * n):
            matched += 1

    if matched < n:
        return False, None

    match_left = [-1] * n
    for v in range(n):
        if match_right[v] != -1:
            match_left[match_right[v]] = v
    return True, match_left


def assignment_bottleneck_lbap(cost_matrix):
    """
    Resolve o Problema de Atribuicao Gargalo (minimizacao do custo maximo).

    Parametros:
        cost_matrix : matriz de custos n x n (lista de listas).

    Retorno:
        bottleneck_cost : custo maximo na atribuicao otima
        assignment      : lista onde assignment[i] = j (trabalhador i -> tarefa j)
    """
    n = len(cost_matrix)

    # Coleta e ordena todos os valores distintos — candidatos a threshold
    all_values = sorted(set(cost_matrix[i][j] for i in range(n) for j in range(n)))

    # Busca binaria: menor threshold com emparelhamento perfeito
    lo, hi = 0, len(all_values) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        feasible, _ = _has_perfect_matching(cost_matrix, all_values[mid])
        if feasible:
            hi = mid    # viavel: tenta threshold menor
        else:
            lo = mid + 1  # inviavel: precisa de threshold maior

    # Threshold otimo: all_values[lo]
    bottleneck_cost = all_values[lo]
    _, assignment = _has_perfect_matching(cost_matrix, bottleneck_cost)

    return bottleneck_cost, assignment


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cost = [
        [9, 2, 7],
        [3, 6, 4],
        [1, 8, 5],
    ]

    bc, asgn = assignment_bottleneck_lbap(cost)

    print("=== Atribuicao Gargalo (LBAP / busca binaria + emparelhamento) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuicao otima: {asgn}")
    print(f"Custo gargalo (maximo na atribuicao): {bc}")
    for i, j in enumerate(asgn):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")

    print()

    # Exemplo 2: W0->T2(3), W1->T0(2), W2->T1(1) -- gargalo=3
    # Threshold 2 e inviavel (W0 nao tem aresta com custo <= 2).
    cost2 = [
        [9, 3, 3],
        [2, 8, 6],
        [5, 1, 7],
    ]
    bc2, asgn2 = assignment_bottleneck_lbap(cost2)
    print(f"Exemplo 2 — custo gargalo: {bc2}  (esperado: 3)")
    for i, j in enumerate(asgn2):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost2[i][j]})")
