"""
Emparelhamento de Peso Máximo em Grafos Gerais
Algoritmo: Path Growing (Drake & Hougardy)

Complexidade de tempo:  O(E)  (cada aresta e examinada um numero constante de vezes)
Complexidade de espaço: O(V + E)
Tipo: Heurística (aproximada; garante pelo menos 1/2 do peso ótimo)

Descrição:
    Heuristica linear para emparelhamento de peso maximo em grafos gerais.
    Cresce caminhos: a partir de um vertice, escolhe repetidamente a aresta
    incidente de maior peso, adiciona-a alternadamente a um de dois
    emparelhamentos M1 e M2, e remove o vertice ja processado, avancando para o
    outro extremo. Como arestas consecutivas do caminho vao para conjuntos
    diferentes, M1 e M2 sao ambos emparelhamentos validos. Ao final, retorna o
    de maior peso.

    A alternancia garante que cada M_i e um emparelhamento; a escolha gulosa da
    aresta mais pesada em cada passo garante a razao de aproximacao de 1/2: o
    peso do melhor entre M1 e M2 e sempre >= metade do peso otimo.

Fonte:
    D. E. Drake, S. Hougardy, "A simple approximation algorithm for the
    weighted matching problem", Information Processing Letters 85 (2003) 211-213.

Representação do grafo:
    - n: numero de vertices (0..n-1)
    - edges: lista de tuplas (u, v, w) com peso w
"""

from collections import defaultdict


def max_weight_matching_path_growing(n, edges):
    """
    Emparelhamento de peso (aproximadamente) maximo em grafo geral.

    Parametros:
        n     : numero de vertices (0..n-1)
        edges : lista de tuplas (u, v, w) com peso w

    Retorno:
        total_weight : soma dos pesos das arestas emparelhadas
        matching     : lista de tuplas (u, v) com u < v
    """
    # Adjacencia com pesos; ignora lacos. Mantem o maior peso para arestas
    # paralelas (u,v).
    peso = {}
    adj = defaultdict(set)
    for u, v, w in edges:
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in peso or w > peso[(a, b)]:
            peso[(a, b)] = w
        adj[a].add(b)
        adj[b].add(a)

    removido = [False] * n
    m = [{}, {}]   # M1, M2 como dict vertice->parceiro
    i = 0

    def w_aresta(a, b):
        return peso[(a, b) if a < b else (b, a)]

    for inicio in range(n):
        if removido[inicio] or not adj[inicio]:
            continue
        x = inicio
        # Cresce um caminho a partir de x enquanto houver aresta incidente.
        while True:
            # remove vizinhos ja processados
            viz = [y for y in adj[x] if not removido[y]]
            if not viz:
                removido[x] = True
                break
            # aresta incidente de maior peso
            y = max(viz, key=lambda z: w_aresta(x, z))
            m[i][x] = y
            m[i][y] = x
            i = 1 - i                 # alterna M1 <-> M2
            removido[x] = True        # remove x; o caminho segue por y
            x = y

    def monta(md):
        pares = set()
        total = 0
        for a, b in md.items():
            if a < b:
                pares.add((a, b))
                total += w_aresta(a, b)
        return total, sorted(pares)

    t0, p0 = monta(m[0])
    t1, p1 = monta(m[1])
    return (t0, p0) if t0 >= t1 else (t1, p1)


if __name__ == "__main__":
    # Caminho 0-1-2-3 com pesos 1,3,1: otimo = aresta (1,2) peso 3 -> peso 3.
    edges = [(0, 1, 1), (1, 2, 3), (2, 3, 1)]
    w, m = max_weight_matching_path_growing(4, edges)
    print("=== Path Growing (heurística de peso máximo) ===")
    print(f"emparelhamento: {m}  peso total: {w}")

    # Triangulo com pesos 1,1,10: otimo pega a aresta de peso 10.
    edges2 = [(0, 1, 1), (1, 2, 1), (0, 2, 10)]
    w2, m2 = max_weight_matching_path_growing(3, edges2)
    print(f"triângulo: {m2}  peso: {w2}  (ótimo = 10)")
