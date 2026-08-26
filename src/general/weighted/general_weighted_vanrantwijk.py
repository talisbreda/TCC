"""
Emparelhamento de Peso Máximo em Grafos Gerais (não bipartidos)
Algoritmo: Blossom de Edmonds (método primal-dual de Galil), implementação
           de Joris van Rantwijk (mwmatching.py)

Complexidade de tempo:  O(n^3)  (n = número de vértices)
Complexidade de espaço: O(n + m) para os vetores de vértices, arestas,
                        endpoints, rótulos, flores (blossoms) e variáveis duais.
Tipo: Exato

Descrição:
    Resolve o problema do emparelhamento de PESO MÁXIMO em um grafo geral
    (arbitrário, não necessariamente bipartido) e com pesos nas arestas.
    O objetivo é escolher um conjunto de arestas sem vértices em comum
    (um emparelhamento) cuja soma de pesos seja a maior possível.

    A implementação usa o método das "flores" (blossoms) de Jack Edmonds
    para encontrar caminhos aumentantes em grafos gerais — em grafos não
    bipartidos podem existir ciclos ímpares que precisam ser contraídos em
    super-vértices (as flores) — combinado com o método primal-dual de Galil
    para garantir a otimalidade do peso. Cada estágio (fase) aumenta o
    emparelhamento em uma aresta e custa O(n^2); com no máximo O(n) estágios,
    o tempo total é O(n^3).

    Por padrão maximiza-se o peso total sem restrição de cardinalidade
    (arestas de peso negativo simplesmente não entram na solução). Este
    wrapper assume pesos das arestas presentes; arestas ausentes não são
    passadas (não existe "peso negativo para aresta ausente": ausência de
    aresta é modelada pela sua não inclusão na lista).

Fonte:
    Joris van Rantwijk, "Maximum Weighted Matching" (mwmatching.py).
    http://jorisvr.nl/article/maximum-matching
    Código de referência vendorizado em:
        repository/general/weighted/mwmatching.py
    O algoritmo segue Z. Galil, "Efficient Algorithms for Finding Maximum
    Matching in Graphs", ACM Computing Surveys, 1986, baseado no método
    de flores (blossom) de Jack Edmonds.

    NOTA sobre o NetworkX: a função `networkx.max_weight_matching` é um
    PORT deste mesmo código de van Rantwijk (mesma linhagem/algoritmo).
    Portanto, comparar este wrapper com o NetworkX confirma a fidelidade do
    port, não uma implementação independente.

Representação do grafo:
    - n     : número de vértices, rotulados 0..n-1
    - edges : lista de tuplas (u, v, w), aresta não direcionada entre u e v
              com peso w. No máximo uma aresta por par; sem laços (u != v).
"""

import os
import sys

# ---------------------------------------------------------------------------
# Importação do código vendorizado (repository/general/weighted/mwmatching.py)
#
# O arquivo original de van Rantwijk foi vendorizado INTACTO, sem portar de
# Python 2 para 3: ele já inclui `from __future__ import print_function` e um
# teste de versão em tempo de execução, funcionando diretamente no Python 3.
# ---------------------------------------------------------------------------
_REPO_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "repository", "general", "weighted",
)
if _REPO_DIR not in sys.path:
    sys.path.insert(0, _REPO_DIR)

from mwmatching import maxWeightMatching  # noqa: E402


# ---------------------------------------------------------------------------
# Interface padrão do benchmark
# ---------------------------------------------------------------------------

def max_weight_matching_vanrantwijk(n, edges):
    """
    Encontra um emparelhamento de PESO MÁXIMO em um grafo geral ponderado,
    usando o algoritmo blossom de Edmonds (implementação de van Rantwijk).

    Parâmetros:
        n     : número de vértices, rotulados 0..n-1
        edges : lista de tuplas (u, v, w) com 0 <= u, v < n, u != v e peso w

    Retorno:
        total_weight : soma dos pesos das arestas emparelhadas
        matching     : lista de tuplas (u, v) com u < v, uma por aresta
                       do emparelhamento (ordenada por u)
    """
    # Grafo sem arestas: emparelhamento vazio, peso zero.
    if not edges:
        return 0, []

    # `mate[v]` = parceiro de v, ou -1 se v está livre.
    # O comprimento de `mate` é o maior índice de vértice que aparece em
    # `edges` mais um; vértices sem arestas nunca são emparelhados.
    mate = maxWeightMatching(edges, maxcardinality=False)

    # Peso de cada aresta, indexado pelo par ordenado (menor, maior).
    peso = {}
    for u, v, w in edges:
        a, b = (u, v) if u < v else (v, u)
        peso[(a, b)] = w

    # Reconstrói o emparelhamento a partir do vetor `mate`, evitando
    # contar cada aresta duas vezes (mate[u] = v e mate[v] = u).
    matching = []
    total_weight = 0
    for u in range(len(mate)):
        v = mate[u]
        if v != -1 and u < v:
            matching.append((u, v))
            total_weight += peso[(u, v)]

    return total_weight, matching


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Grafo geral (um triângulo com pesos):
    #   Vértices: 0, 1, 2
    #   Arestas:  (0,1,w=5), (1,2,w=3), (0,2,w=4)
    # Em um triângulo só cabe UMA aresta no emparelhamento, então a solução
    # ótima é a aresta de maior peso: (0,1) com peso 5.
    n = 3
    edges = [(0, 1, 5), (1, 2, 3), (0, 2, 4)]

    total_weight, matching = max_weight_matching_vanrantwijk(n, edges)

    print("=== Emparelhamento de Peso Máximo (van Rantwijk / blossom) ===")
    print(f"Peso total do emparelhamento: {total_weight}  (ótimo = 5)")
    print(f"Arestas emparelhadas (u < v): {matching}")
