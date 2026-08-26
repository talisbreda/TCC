"""
Emparelhamento de Cardinalidade Máxima em Grafos Bipartidos
Algoritmo: Heurística de Karp-Sipser (regra dos vértices de grau 1)

Complexidade de tempo:  O(V·E) nesta implementação simples e legível
                        (~O(V+E) é possível com estruturas de dados adequadas)
Complexidade de espaço: O(V+E) para as listas de adjacência e os graus
Tipo: Heurística (aproximada; frequentemente ótima, sempre maximal)

Descrição:
    A heurística de Karp-Sipser constrói um emparelhamento aplicando
    repetidamente a "regra do grau 1":

        1. Enquanto existir uma aresta no grafo residual:
           a. Se existe algum vértice de grau 1 (em qualquer um dos lados),
              case-o com seu único vizinho e remova ambos os vértices (e todas
              as arestas incidentes). Essa escolha é provadamente ótima: sempre
              existe um emparelhamento máximo que contém essa aresta, então
              nunca perdemos qualidade ao fixá-la.
           b. Caso contrário (todos os vértices restantes têm grau >= 2),
              escolha uma aresta arbitrária, case seus dois extremos e remova-os.
              Este é o único passo "guloso/arbitrário" e a única fonte possível
              de sub-otimalidade.

    O resultado é sempre um emparelhamento maximal (nenhuma aresta pode ser
    adicionada), de qualidade tipicamente muito superior à heurística gulosa
    pura e, em grafos esparsos, frequentemente igual ao ótimo. Os autores
    provaram que em grafos aleatórios esparsos a fase de grau 1 sozinha já
    encontra emparelhamentos quase perfeitos com alta probabilidade.

    Enquanto a regra do grau 1 se aplica, o algoritmo é exato; apenas quando
    o núcleo residual só possui vértices de grau >= 2 é que a escolha
    arbitrária pode, ocasionalmente, não ser ótima.

Fonte:
    Karp, R. M.; Sipser, M. "Maximum matchings in sparse random graphs."
    Proceedings of the 22nd Annual Symposium on Foundations of Computer
    Science (FOCS), 1981, pp. 364-375.

Representação do grafo:
    - edges: lista de tuplas (u, v)
    - Vértices esquerdo: 0..n_left-1
    - Vértices direito:  0..n_right-1
"""


def max_cardinality_matching_karp_sipser(n_left, n_right, edges):
    """
    Encontra um emparelhamento de grande cardinalidade em um grafo bipartido
    usando a heurística de Karp-Sipser.

    Parâmetros:
        n_left  : número de vértices no lado esquerdo (U)
        n_right : número de vértices no lado direito (V)
        edges   : lista de tuplas (u, v) com u in [0, n_left) e v in [0, n_right)

    Retorno:
        matching_size : cardinalidade do emparelhamento encontrado
        match_left    : vetor onde match_left[u] = v se (u,v) está no
                        emparelhamento, -1 se u está livre
        match_right   : vetor onde match_right[v] = u se (u,v) está no
                        emparelhamento, -1 se v está livre
    """
    # Para tratar os dois lados de forma uniforme, usamos rótulos globais:
    # vértices esquerdos ocupam 0..n_left-1 e vértices direitos ocupam
    # n_left..n_left+n_right-1 (deslocados por n_left).
    offset = n_left
    total = n_left + n_right

    # Listas de adjacência com conjuntos, para remoção O(1) de arestas.
    adj = [set() for _ in range(total)]
    for u, v in edges:
        rv = offset + v
        # Ignora arestas duplicadas naturalmente (conjuntos).
        adj[u].add(rv)
        adj[rv].add(u)

    # Grau atual de cada vértice no grafo residual.
    degree = [len(adj[w]) for w in range(total)]
    # Vértice removido (casado ou isolado) não deve mais ser considerado.
    removed = [False] * total

    match_left = [-1] * n_left
    match_right = [-1] * n_right

    def remove_vertex(w):
        """Remove o vértice w do grafo residual, atualizando os graus dos
        vizinhos ainda presentes."""
        removed[w] = True
        for nb in adj[w]:
            if not removed[nb]:
                adj[nb].discard(w)
                degree[nb] -= 1
        adj[w] = set()
        degree[w] = 0

    def match_pair(a, b):
        """Registra o par (a, b) no emparelhamento (a e b são rótulos globais)
        e remove ambos os vértices do grafo residual."""
        if a < offset:
            left, right = a, b
        else:
            left, right = b, a
        match_left[left] = right - offset
        match_right[right - offset] = left
        remove_vertex(a)
        remove_vertex(b)

    # Número de arestas restantes no grafo residual (soma dos graus / 2).
    remaining_edges = sum(degree) // 2

    while remaining_edges > 0:
        # 1) Procura um vértice de grau 1 (regra ótima de Karp-Sipser).
        deg1 = -1
        for w in range(total):
            if not removed[w] and degree[w] == 1:
                deg1 = w
                break

        if deg1 != -1:
            # Único vizinho de deg1.
            nb = next(iter(adj[deg1]))
            match_pair(deg1, nb)
        else:
            # 2) Nenhum vértice de grau 1: escolhe uma aresta arbitrária.
            #    Pega o primeiro vértice ainda presente com grau >= 1.
            a = -1
            for w in range(total):
                if not removed[w] and degree[w] >= 1:
                    a = w
                    break
            # Deve existir, pois remaining_edges > 0.
            b = next(iter(adj[a]))
            match_pair(a, b)

        # Recalcula o número de arestas restantes.
        remaining_edges = sum(degree) // 2

    matching_size = sum(1 for v in match_left if v != -1)
    return matching_size, match_left, match_right


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Grafo bipartido:
    #   Esquerdo: 0, 1, 2
    #   Direito:  0, 1, 2
    #   Arestas:  (0,0), (0,1), (1,0), (2,1), (2,2)
    # Ótimo conhecido tem tamanho 3.

    n_left = 3
    n_right = 3
    edges = [(0, 0), (0, 1), (1, 0), (2, 1), (2, 2)]

    size, match_left, match_right = max_cardinality_matching_karp_sipser(
        n_left, n_right, edges
    )

    print("=== Karp-Sipser (heurística) ===")
    print(f"Cardinalidade do emparelhamento encontrado: {size}  (ótimo = 3)")
    print(f"match_left  (esquerdo -> direito): {match_left}")
    print(f"match_right (direito  -> esquerdo): {match_right}")
    print("Pares no emparelhamento:")
    for u in range(n_left):
        if match_left[u] != -1:
            print(f"  Esquerdo {u} <-> Direito {match_left[u]}")

    print()

    # Exemplo com grafo bipartido completo K(4,4) — ótimo = 4
    n2 = 4
    edges2 = [(u, v) for u in range(n2) for v in range(n2)]
    size2, ml2, _ = max_cardinality_matching_karp_sipser(n2, n2, edges2)
    print(f"K(4,4) — tamanho: {size2}  (ótimo = 4)")
