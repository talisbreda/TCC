"""
Problema de Atribuição (Assignment Problem)
Algoritmo: Método Húngaro

Complexidade de tempo: O(n³)
Tipo: Exato

Descrição:
    Resolve o problema de atribuição linear usando a implementação de Ben
    Chaplin. O grafo bipartido é representado como dicionário de adjacência
    ponderado; o algoritmo mantém um rótulo por vértice e busca caminhos
    aumentantes no subgrafo de igualdade, ajustando rótulos quando necessário.

    Por padrão o algoritmo MAXIMIZA; para minimização, internamente os pesos
    são negados e restaurados no retorno.

Fonte original:
    Ben Chaplin — https://github.com/benchaplin/hungarian-algorithm
    Arquivo: hungarian_algorithm/algorithm.py
    Adaptado para a interface padrão do benchmark (cost_matrix).

Entrada:
    Matriz de custos n×n (lista de listas). Minimização.
    Para maximização, negar a matriz antes de chamar.
"""

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent   # TCC/
_src  = (_ROOT / "repository" / "assignment" / "hungarian"
         / "hungarian-algorithm-benchaplin" / "hungarian_algorithm" / "algorithm.py")
_spec = importlib.util.spec_from_file_location("ha_benchaplin", _src)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def hungarian_benchaplin(cost_matrix):
    """
    Resolve o problema de atribuição linear (minimização).

    Parâmetros:
        cost_matrix : matriz de custos n×n (lista de listas).

    Retorno:
        total_cost  : custo total da atribuição ótima
        assignment  : lista onde assignment[i] = j (trabalhador i → tarefa j)
    """
    n = len(cost_matrix)

    # Converte para o formato de dict esperado pelo algoritmo.
    # Vértices esquerdos: 'w0'..'w(n-1)' | Direitos: 't0'..'t(n-1)'
    G = {}
    for i in range(n):
        G[f"w{i}"] = {f"t{j}": cost_matrix[i][j] for j in range(n)}

    edges = _mod.find_matching(G, matching_type="min", return_type="list")

    assignment = [-1] * n
    for (v1, v2), _ in edges:
        # find_matching pode retornar pares em qualquer ordem
        if v1.startswith("w"):
            i, j = int(v1[1:]), int(v2[1:])
        else:
            i, j = int(v2[1:]), int(v1[1:])
        assignment[i] = j

    total_cost = sum(cost_matrix[i][assignment[i]] for i in range(n))
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

    total, assignment = hungarian_benchaplin(cost)

    print("=== Método Húngaro (benchaplin) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuição ótima: {assignment}")
    print(f"Custo total mínimo: {total}")
    for i, j in enumerate(assignment):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")
