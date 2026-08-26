"""
Emparelhamento Induzido Máximo (Maximum Induced Matching - MIM) em Grafos Gerais
Algoritmo: Exato via redução a Conjunto Independente Máximo (branch-and-bound)

Complexidade de tempo:  exponencial no pior caso (o problema é NP-difícil)
Complexidade de espaço: O(E^2) para o grafo de conflitos
Tipo: Exato (viável apenas para instâncias pequenas)

Descrição:
    Um emparelhamento M é INDUZIDO se o subgrafo induzido pelos vértices
    cobertos por M contém exatamente as arestas de M -- ou seja, nenhuma aresta
    de G liga duas arestas distintas de M. Equivalentemente, duas arestas
    e1=(a,b) e e2=(c,d) podem coexistir em M se, e somente se, não compartilham
    vértice E nenhum dos pares cruzados (a,c),(a,d),(b,c),(b,d) é aresta de G.

    Construímos o GRAFO DE CONFLITOS H: um vértice por aresta de G; duas arestas
    são ligadas em H se conflitam (compartilham vértice ou há aresta cruzada).
    Um emparelhamento induzido de G é exatamente um CONJUNTO INDEPENDENTE em H,
    e o MIM é o Conjunto Independente Máximo (MIS) de H. Resolvemos o MIS por
    branch-and-bound simples, viável para as instâncias pequenas usadas na
    comparação exato × heurística.

Fonte:
    Cameron, K. "Induced matchings", Discrete Applied Mathematics 24 (1989).
    A equivalência MIM = MIS no grafo de conflitos é padrão na literatura.

Representação do grafo:
    - n: número de vértices (0..n-1)
    - edges: lista de tuplas (u, v)
"""

import sys


def _normaliza(edges):
    E = []
    vistas = set()
    for u, v in edges:
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in vistas:
            vistas.add((a, b))
            E.append((a, b))
    return E


def _grafo_de_conflitos(n, E):
    """Retorna conflito[i] = conjunto de índices de arestas que conflitam com E[i]."""
    incidentes = [[] for _ in range(n)]
    for idx, (a, b) in enumerate(E):
        incidentes[a].append(idx)
        incidentes[b].append(idx)
    arestas_set = set(E)

    def existe(x, y):
        return (x, y) if x < y else (y, x)

    m = len(E)
    conflito = [set() for _ in range(m)]
    for i in range(m):
        a, b = E[i]
        # compartilha vértice
        for j in incidentes[a] + incidentes[b]:
            if j != i:
                conflito[i].add(j)
        # aresta cruzada
        for j in range(m):
            if j == i:
                continue
            c, d = E[j]
            if (existe(a, c) in arestas_set or existe(a, d) in arestas_set
                    or existe(b, c) in arestas_set or existe(b, d) in arestas_set):
                conflito[i].add(j)
                conflito[j].add(i)
    return conflito


def mim_exact(n, edges):
    """
    Emparelhamento induzido máximo (exato).

    Retorno:
        (matching_size, matching) com matching = lista de tuplas (u,v), u<v.
    """
    E = _normaliza(edges)
    m = len(E)
    if m == 0:
        return 0, []

    conflito = _grafo_de_conflitos(n, E)
    livres_iniciais = frozenset(range(m))
    melhor = [0]
    melhor_conj = [set()]

    limite_rec = sys.getrecursionlimit()
    if m + 100 > limite_rec:
        sys.setrecursionlimit(m + 100)

    def bnb(disponiveis, atual):
        # Poda: mesmo pegando todos os disponíveis não supera o melhor.
        if len(atual) + len(disponiveis) <= melhor[0]:
            return
        if not disponiveis:
            if len(atual) > melhor[0]:
                melhor[0] = len(atual)
                melhor_conj[0] = set(atual)
            return
        # escolhe um vértice de H (aresta de G) para ramificar
        v = next(iter(disponiveis))
        # ramo 1: inclui v
        novos = disponiveis - conflito[v] - {v}
        atual.add(v)
        bnb(novos, atual)
        atual.discard(v)
        # ramo 2: exclui v
        bnb(disponiveis - {v}, atual)

    bnb(set(livres_iniciais), set())
    matching = sorted(E[i] for i in melhor_conj[0])
    return melhor[0], matching


if __name__ == "__main__":
    # Caminho P4: 0-1-2-3. MIM = {(0,1),(2,3)} tamanho 2.
    print("P4:", mim_exact(4, [(0, 1), (1, 2), (2, 3)]))
    # Estrela: MIM = 1 (todas as arestas compartilham o centro).
    print("Estrela K1,4:", mim_exact(5, [(0, 1), (0, 2), (0, 3), (0, 4)]))
    # C5: MIM = 1 (num ciclo de 5, quaisquer 2 arestas não-adjacentes têm
    # aresta cruzada? nao — em C5 duas arestas a distancia 2 sao induzidas). = 1? na verdade 1.
    print("C5:", mim_exact(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]))
