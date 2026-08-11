"""
Problema de Atribuicao Linear (Assignment Problem)
Algoritmo: linear_sum_assignment (baseline de biblioteca — SciPy)

Complexidade de tempo: O(n^3)  (Jonker-Volgenant / shortest augmenting path)
Tipo: Exato

Descricao:
    Baseline de biblioteca madura. Usa scipy.optimize.linear_sum_assignment,
    que implementa uma variante do algoritmo de Jonker-Volgenant (caminhos
    aumentantes mais curtos), como ponto de comparacao para os wrappers
    obtidos de repositorios externos. E a referencia padrao da industria para
    o problema de atribuicao linear.

    Diferente dos demais wrappers do projeto, este NAO adapta codigo de
    repository/: encapsula uma biblioteca instalada via pip.

Fonte:
    SciPy — https://scipy.org/
    scipy.optimize.linear_sum_assignment
    Adaptado para a interface padrao do benchmark (cost_matrix).

Requer: scipy, numpy.

Entrada:
    Matriz de custos n x n (lista de listas). Minimizacao.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment


def assignment_scipy_linear_sum(cost_matrix):
    """
    Resolve o problema de atribuicao linear (minimizacao) via SciPy.

    Parametros:
        cost_matrix : matriz de custos n x n (lista de listas).

    Retorno:
        total_cost  : custo total da atribuicao otima
        assignment  : lista onde assignment[i] = j (trabalhador i -> tarefa j)
    """
    matrix = np.asarray(cost_matrix)
    row_ind, col_ind = linear_sum_assignment(matrix)

    n = len(cost_matrix)
    assignment = [-1] * n
    for i, j in zip(row_ind.tolist(), col_ind.tolist()):
        assignment[i] = j

    total_cost = int(matrix[row_ind, col_ind].sum())
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

    total, assignment = assignment_scipy_linear_sum(cost)

    print("=== Atribuicao Linear (baseline SciPy / linear_sum_assignment) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuicao otima: {assignment}")
    print(f"Custo total minimo: {total}")
    for i, j in enumerate(assignment):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")
