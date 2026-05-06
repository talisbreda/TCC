"""
Emparelhamento de Cardinalidade Máxima em Grafos Bipartidos
Algoritmo: Hopcroft-Karp

Complexidade de tempo: O(E·√V)
Tipo: Exato

Descrição:
    Encontra o emparelhamento máximo em um grafo bipartido por meio de fases
    alternadas de BFS e DFS. A BFS constrói uma estratificação em camadas a
    partir de todos os vértices livres do lado esquerdo; a DFS encontra um
    conjunto máximo de caminhos aumentantes vertex-disjuntos de comprimento
    mínimo. O processo repete até não existirem mais caminhos aumentantes.

    O número de fases é O(√V), e cada fase percorre O(E), resultando em
    complexidade total O(E·√V).

    A implementação original recebe o grafo como dicionário de adjacência
    {vértice_esquerdo: {vértice_direito, ...}}. Como exige que os rótulos
    dos lados esquerdo e direito sejam distintos, vértices do lado direito
    são deslocados por n_left internamente e restaurados na saída.

Fonte original:
    Sofiat Olaosebikan — https://github.com/sofiat-olaosebikan/hopcroftkarp
    Arquivo: hopcroftkarp/__init__.py
    Adaptado para a interface padrão do benchmark (n_left, n_right, edges).

Representação do grafo:
    - edges: lista de tuplas (u, v)
    - Vértices esquerdo: 0..n_left-1
    - Vértices direito:  0..n_right-1
"""

import importlib.util
from pathlib import Path

# Carrega hopcroftkarp/__init__.py diretamente pelo caminho (diretório pai
# contém hífens, impedindo import normal)
_src = (Path(__file__).parent.parent.parent.parent
        / "repository" / "mcm" / "hopcroft-karp"
        / "hopcroftkarp" / "hopcroftkarp" / "__init__.py")
_spec = importlib.util.spec_from_file_location("hopcroftkarp", _src)
_hk   = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hk)


# ---------------------------------------------------------------------------
# Interface padrão do benchmark
# ---------------------------------------------------------------------------

def max_cardinality_matching_hopcroft_karp_sofiat(n_left, n_right, edges):
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
    # A classe HopcroftKarp exige rótulos distintos entre os dois lados.
    # Desloca vértices direitos por n_left para evitar colisão de rótulos.
    offset = n_left
    graph = {u: set() for u in range(n_left)}
    for u, v in edges:
        graph[u].add(offset + v)

    matching_dict = _hk.HopcroftKarp(graph).maximum_matching(keys_only=True)
    # matching_dict: {u: (offset + v), ...} apenas para vértices esquerdo

    match_left  = [-1] * n_left
    match_right = [-1] * n_right
    for u, rv in matching_dict.items():
        v = rv - offset
        match_left[u]  = v
        match_right[v] = u

    return len(matching_dict), match_left, match_right


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

    size, match_left, match_right = max_cardinality_matching_hopcroft_karp_sofiat(
        n_left, n_right, edges
    )

    print("=== Hopcroft-Karp (sofiat-olaosebikan) ===")
    print(f"Cardinalidade do emparelhamento encontrado: {size}")
    print(f"match_left  (esquerdo -> direito): {match_left}")
    print(f"match_right (direito  -> esquerdo): {match_right}")
    print("Pares no emparelhamento:")
    for u in range(n_left):
        if match_left[u] != -1:
            print(f"  Esquerdo {u} <-> Direito {match_left[u]}")

    print()

    # Exemplo com grafo completo bipartido K(3,3) — ótimo = 3
    n2 = 3
    edges2 = [(u, v) for u in range(n2) for v in range(n2)]
    size2, ml2, _ = max_cardinality_matching_hopcroft_karp_sofiat(n2, n2, edges2)
    print(f"K(3,3) — tamanho: {size2}  (ótimo = 3)")
