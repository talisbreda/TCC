"""
Emparelhamento de Cardinalidade Máxima em Grafos Gerais (não bipartidos)
Algoritmo: Blossom de Edmonds (contração de flores / "blossom shrinking")

Complexidade de tempo:  O(V^3) — cota clássica do algoritmo de Edmonds.
                        (Esta implementação de referência usa cópias profundas
                        e reconstrói a floreta de busca a cada aumento, portanto
                        não é a variante mais otimizada, mas respeita o mesmo
                        limite polinomial.)
Complexidade de espaço: O(V^2) para as estruturas auxiliares (grafo contraído,
                        florestas de busca e listas de arestas copiadas).
Tipo: Exato

Descrição:
    O algoritmo de Edmonds resolve o emparelhamento de cardinalidade máxima em
    grafos GERAIS, onde a estratégia bipartida de caminhos aumentantes falha por
    causa dos ciclos de comprimento ímpar. A ideia central é a "flor" (blossom):
    um ciclo ímpar alcançado durante a busca por um caminho aumentante.

        1. A partir de cada vértice livre, cresce-se uma floresta alternante
           (arestas fora/dentro do emparelhamento em camadas alternadas) via BFS.
        2. Se dois vértices em nível par de árvores DIFERENTES são adjacentes,
           encontrou-se um caminho aumentante — inverte-se o emparelhamento ao
           longo dele, aumentando a cardinalidade em 1.
        3. Se esses vértices estão na MESMA árvore, o ciclo ímpar formado é uma
           flor. A flor é contraída em um único super-vértice e a busca continua
           no grafo contraído. Ao encontrar um caminho aumentante no grafo
           contraído, a flor é "expandida" (lifting), reconstruindo o trecho
           interno correto do caminho no grafo original.

    Repetindo enquanto houver caminho aumentante, obtém-se, pelo teorema de
    Berge, um emparelhamento de cardinalidade máxima (exato).

Fonte original:
    Adharsh Kamath e colaboradores — Implementação do algoritmo de Edmonds
    (projeto IT251). https://github.com/adharshkamath/Edmonds-Algorithm
    Arquivos: src/blossom.py e src/graph_utils.py (vendorizados intactos em
    repository/general/blossom/). Adaptado para a interface padrão do
    benchmark (n, edges).

Representação do grafo:
    - n     : número de vértices, rotulados 0..n-1
    - edges : lista de tuplas (u, v) — arestas NÃO direcionadas de grafo geral
"""

import importlib.util
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Carregamento do código vendorizado
#
# O arquivo blossom.py faz "from graph_utils import ...", portanto registramos
# graph_utils em sys.modules ANTES de carregar blossom, para que essa importação
# relativa seja resolvida sem alterar permanentemente o sys.path do processo.
# ---------------------------------------------------------------------------
_VENDOR = (Path(__file__).parent.parent.parent.parent
           / "repository" / "general" / "blossom")


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, _VENDOR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # deixa a importação "from graph_utils" enxergar
    spec.loader.exec_module(module)
    return module


_graph_utils = _load_module("graph_utils", "graph_utils.py")
_blossom = _load_module("blossom", "blossom.py")

Graph = _graph_utils.Graph
Matching = _graph_utils.Matching
find_maximum_matching = _blossom.find_maximum_matching


# ---------------------------------------------------------------------------
# Interface padrão do benchmark
# ---------------------------------------------------------------------------

def max_cardinality_matching_blossom(n, edges):
    """
    Encontra um emparelhamento de cardinalidade máxima em um grafo GERAL
    (não necessariamente bipartido) usando o algoritmo de Blossom de Edmonds.

    Parâmetros:
        n     : número de vértices do grafo, rotulados 0..n-1
        edges : lista de tuplas (u, v) representando arestas não direcionadas

    Retorno:
        matching_size : cardinalidade do emparelhamento encontrado (int)
        matching      : lista de tuplas (u, v) com u < v, uma por aresta
                        emparelhada
    """
    # Caso trivial: sem vértices ou sem arestas, não há o que emparelhar.
    if n <= 0 or not edges:
        return 0, []

    # A busca por caminhos aumentantes e a contração de flores são recursivas.
    # Garantimos um limite de recursão folgado para grafos maiores do benchmark.
    limite_desejado = 1000 + 20 * n
    if sys.getrecursionlimit() < limite_desejado:
        sys.setrecursionlimit(limite_desejado)

    # Monta o grafo no formato esperado pela implementação vendorizada.
    # Ela representa cada aresta não direcionada pelos dois sentidos [u, v] e
    # [v, u], exatamente como no seu código de demonstração.
    grafo = Graph()
    grafo.nodes = list(range(n))
    grafo.edges = []
    for u, v in edges:
        if u == v:
            continue  # laços não participam de emparelhamento
        grafo.edges.append([u, v])
        grafo.edges.append([v, u])

    # Executa o algoritmo a partir de um emparelhamento vazio.
    resultado = find_maximum_matching(grafo, Matching())

    # Normaliza a saída: cada aresta uma única vez, com u < v.
    vistos = set()
    matching = []
    for aresta in resultado.edges:
        u, v = aresta[0], aresta[1]
        if u > v:
            u, v = v, u
        if (u, v) not in vistos:
            vistos.add((u, v))
            matching.append((u, v))

    return len(matching), matching


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ciclo ímpar C5 (0-1-2-3-4-0): emparelhamento máximo tem tamanho 2,
    # pois um vértice sempre sobra em um ciclo de comprimento ímpar.
    c5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    size_c5, m_c5 = max_cardinality_matching_blossom(5, c5)
    print("=== Blossom de Edmonds (grafo geral) ===")
    print(f"C5  -> tamanho: {size_c5}  (ótimo = 2)   pares: {m_c5}")

    # Grafo completo K4: 4 vértices, emparelhamento perfeito de tamanho 2.
    k4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    size_k4, m_k4 = max_cardinality_matching_blossom(4, k4)
    print(f"K4  -> tamanho: {size_k4}  (ótimo = 2)   pares: {m_k4}")

    # Dois triângulos ligados por uma ponte: emparelhamento perfeito, tamanho 3.
    # Exemplo em que a contração de flores (ciclos ímpares) é essencial.
    dois_triangulos = [(0, 1), (1, 2), (2, 0),   # triângulo 0-1-2
                       (3, 4), (4, 5), (5, 3),   # triângulo 3-4-5
                       (2, 3)]                    # ponte
    size_dt, m_dt = max_cardinality_matching_blossom(6, dois_triangulos)
    print(f"2xC3 -> tamanho: {size_dt}  (ótimo = 3)   pares: {m_dt}")
