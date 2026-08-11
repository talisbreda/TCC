"""
Problema de Atribuicao (Assignment Problem)
Algoritmo: Caminho Mais Curto Sucessivo (Successive Shortest Path - SSP)

Complexidade de tempo: O(n * SPFA)  onde SPFA = O(V * E) no pior caso
    Para grafo de atribuicao denso (E = n^2, V = 2n+2): O(n^4)
Tipo: Exato

Descricao:
    Reduz o problema de atribuicao a fluxo de custo minimo de capacidade
    unitaria: uma fonte S, n trabalhadores, n tarefas e um sumidouro T.
    A cada iteracao, o SPFA (Shortest Path Faster Algorithm, variante de
    Bellman-Ford com fila FIFO) encontra o caminho de menor custo de S a T
    no grafo residual e envia uma unidade de fluxo por ele. O processo
    repete n vezes, cada iteracao atribuindo um trabalhador a uma tarefa.

    Por manter arcos residuais de custo negativo, o algoritmo pode
    "desfazer" atribuicoes anteriores se necessario, garantindo otimalidade.

    A logica e abordagem (FIFO label-correcting = SPFA sobre grafo residual)
    sao as mesmas de:
        repository/assignment/ssp/flows/mcf_algorithms.py
        repository/assignment/ssp/flows/spp_algorithms.py
    mas reimplementadas diretamente para o caso especifico de atribuicao
    linear, evitando o overhead de deepcopy em grafos com referencias
    circulares.

Fonte original (abordagem):
    Autor desconhecido -- repository/assignment/ssp/flows/
    Arquivos: graph.py, mcf_algorithms.py, spp_algorithms.py
    Adaptado para a interface padrao do benchmark (cost_matrix).

Entrada:
    Matriz de custos n x n (lista de listas). Minimizacao.
    Valores nao-negativos (SPFA com Dijkstra seria mais eficiente, mas
    SPFA e correto mesmo com custos negativos no grafo residual).
"""

from collections import deque


# ---------------------------------------------------------------------------
# Implementacao SSP com SPFA sobre grafo residual
# ---------------------------------------------------------------------------

def _build_assignment_graph(cost_matrix):
    """
    Constroi o grafo de fluxo de custo minimo para o problema de atribuicao.

    Layout de nos (inteiros):
        0          - fonte S
        1 .. n     - trabalhadores W_0 .. W_{n-1}
        n+1 .. 2n  - tarefas T_0 .. T_{n-1}
        2n+1       - sumidouro T

    Retorna adj: lista de listas de [v, capacidade, custo, idx_reverso]
    """
    n = len(cost_matrix)
    total = 2 * n + 2
    S = 0
    T_sink = 2 * n + 1

    adj = [[] for _ in range(total)]

    def add_arc(u, v, cap, cost):
        adj[u].append([v, cap, cost, len(adj[v])])
        adj[v].append([u, 0, -cost, len(adj[u]) - 1])

    # S -> trabalhadores (cap=1, custo=0)
    for i in range(n):
        add_arc(S, i + 1, 1, 0)

    # Trabalhadores -> tarefas (cap=1, custo=matrix[i][j])
    for i in range(n):
        for j in range(n):
            add_arc(i + 1, n + 1 + j, 1, int(cost_matrix[i][j]))

    # Tarefas -> T_sink (cap=1, custo=0)
    for j in range(n):
        add_arc(n + 1 + j, T_sink, 1, 0)

    return adj, S, T_sink


def _spfa_shortest_path(adj, source, sink):
    """
    SPFA (Shortest Path Faster Algorithm) - Bellman-Ford com fila FIFO.
    Encontra o caminho de menor custo de source a sink no grafo residual.

    Retorna (dist, prev_node, prev_edge) ou None se sink inacessivel.
    """
    n = len(adj)
    dist = [float('inf')] * n
    prev_node = [-1] * n
    prev_edge = [-1] * n

    dist[source] = 0
    in_queue = [False] * n
    queue = deque([source])
    in_queue[source] = True

    while queue:
        u = queue.popleft()
        in_queue[u] = False
        for idx, (v, cap, cost, _) in enumerate(adj[u]):
            if cap > 0 and dist[u] + cost < dist[v]:
                dist[v] = dist[u] + cost
                prev_node[v] = u
                prev_edge[v] = idx
                if not in_queue[v]:
                    queue.append(v)
                    in_queue[v] = True

    if dist[sink] == float('inf'):
        return None
    return dist, prev_node, prev_edge


def _augment(adj, prev_node, prev_edge, sink):
    """Envia uma unidade de fluxo pelo caminho encontrado pelo SPFA."""
    v = sink
    while prev_node[v] != -1:
        u = prev_node[v]
        ei = prev_edge[v]
        adj[u][ei][1] -= 1                    # reduz capacidade do arco direto
        adj[v][adj[u][ei][3]][1] += 1         # aumenta capacidade do arco reverso
        v = u


# ---------------------------------------------------------------------------
# Interface padrao do benchmark
# ---------------------------------------------------------------------------

def assignment_ssp_flows(cost_matrix):
    """
    Resolve o problema de atribuicao linear (minimizacao) via SSP.

    Parametros:
        cost_matrix : matriz de custos n x n (lista de listas de int/float).
                      Valores nao-negativos.

    Retorno:
        total_cost  : custo total da atribuicao otima
        assignment  : lista onde assignment[i] = j (trabalhador i -> tarefa j)
    """
    n = len(cost_matrix)
    adj, S, T_sink = _build_assignment_graph(cost_matrix)

    total_cost = 0

    for _ in range(n):
        result = _spfa_shortest_path(adj, S, T_sink)
        if result is None:
            break
        dist, prev_node, prev_edge = result
        total_cost += dist[T_sink]
        _augment(adj, prev_node, prev_edge, T_sink)

    # Extrai atribuicao: arcos W_i -> T_j saturados (cap==0, era 1)
    # Trabalhador i esta no no i+1; tarefa j esta no no n+1+j.
    assignment = [-1] * n
    for i in range(n):
        worker_node = i + 1
        # Pula o primeiro arco (arco reverso de S->W_i) e ve os arcos diretos
        for v, cap, cost, _ in adj[worker_node]:
            if n + 1 <= v <= 2 * n and cap == 0:
                assignment[i] = v - (n + 1)
                break

    return total_cost, assignment


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cost = [
        [9, 2, 7],
        [3, 6, 4],
        [1, 8, 5],
    ]

    total, asgn = assignment_ssp_flows(cost)

    print("=== SSP - Caminho Mais Curto Sucessivo (flows/SPFA) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuicao otima: {asgn}")
    print(f"Custo total minimo: {total}")
    for i, j in enumerate(asgn):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")

    print()

    # Caso que exige arcos residuais para ser resolvido corretamente:
    #   otimo = W0->T1 (1) + W1->T0 (0) = 1
    #   greedy sem residuais poderia escolher W0->T0 (0) primeiro e
    #   depois forcar W1->T1 (2), totalizando 2.
    cost2 = [
        [0, 1],
        [0, 2],
    ]
    total2, asgn2 = assignment_ssp_flows(cost2)
    print(f"Exemplo 2 - custo: {total2}  (otimo = 1)")
    for i, j in enumerate(asgn2):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost2[i][j]})")
