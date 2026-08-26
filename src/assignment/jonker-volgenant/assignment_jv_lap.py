"""
Problema de Atribuicao Linear (Assignment Problem)
Algoritmo: Jonker-Volgenant (baseline de biblioteca — lap, nucleo C++)

Complexidade de tempo: O(n^3)  (caminhos aumentantes mais curtos)
Complexidade de espaco: O(n^2)  (matriz de custos densa n x n)
Tipo: Baseline (exato). Linguagem do nucleo: C++ (compilado).

Descricao:
    Baseline de biblioteca. Encapsula lap.lapjv, implementacao em C++ do
    algoritmo de Jonker-Volgenant (Shortest Augmenting Path para o problema
    de atribuicao linear denso). Serve como ponto de comparacao rapido para
    os demais wrappers do benchmark.

    Diferente dos wrappers implementados a mao, este apenas converte a matriz
    para numpy, chama lap.lapjv e monta a saida na interface padrao. A
    biblioteca lap retorna (custo, x, y), onde x[i] e a coluna (tarefa)
    atribuida a linha (trabalhador) i; y e o mapeamento inverso.

    O custo total e RECOMPUTADO somando cost_matrix[i][assignment[i]] como
    int, para casar exatamente com os demais wrappers do projeto (evitando
    diferencas de tipo/arredondamento do valor devolvido pela biblioteca).

Fonte:
    R. Jonker & A. Volgenant (1987), "A shortest augmenting path algorithm
    for dense and sparse linear assignment problems", Computing 38, 325-340.
    Implementacao: https://github.com/gatagat/lap

Requer: lap, numpy.

Entrada:
    Matriz de custos n x n (lista de listas de int/float). Minimizacao.
"""

import lap
import numpy as np


def assignment_jv_lap(cost_matrix):
    """
    Resolve o problema de atribuicao linear (minimizacao) via lap.lapjv.

    Parametros:
        cost_matrix : matriz de custos n x n (lista de listas de int/float).

    Retorno:
        total_cost  : custo total da atribuicao otima (int)
        assignment  : lista onde assignment[i] = j (trabalhador i -> tarefa j)
    """
    matrix = np.asarray(cost_matrix, dtype=float)

    # lap.lapjv devolve (custo, x, y); x[i] = coluna atribuida a linha i.
    _, x, _ = lap.lapjv(matrix)

    assignment = [int(j) for j in x]

    # Recomputa o custo total a partir da matriz original (int), para casar
    # com os demais wrappers do benchmark.
    total_cost = sum(cost_matrix[i][assignment[i]] for i in range(len(cost_matrix)))
    total_cost = int(total_cost)

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
    # Otimo conhecido: trabalhador 0->1 (2), 1->2 (4), 2->0 (1) => custo 7.

    total, assignment = assignment_jv_lap(cost)

    print("=== Atribuicao Linear (baseline Jonker-Volgenant / lap C++) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuicao otima: {assignment}")
    print(f"Custo total minimo: {total}  (otimo conhecido: 7)")
    for i, j in enumerate(assignment):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")
