"""
Problema de Atribuição (Assignment Problem)
Algoritmo: Método Húngaro (KM — Kuhn-Munkres)

Complexidade de tempo: O(n³)
Tipo: Exato

Descrição:
    Implementação do algoritmo KM (Kuhn-Munkres) por mayorx, baseada no
    tutorial do TopCoder. Opera sobre matrizes numpy e faz MAXIMIZAÇÃO de
    peso. Para minimização, a matriz de custos é negada antes de ser passada.

    Nota de compatibilidade: o código original usa `np.int` e `np.bool`,
    removidos no NumPy ≥ 1.24. O wrapper aplica um patch de compatibilidade
    antes de instanciar a classe.

Fonte original:
    mayorx — https://github.com/mayorx/hungarian-algorithm
    Arquivo: km_matcher.py
    Adaptado para a interface padrão do benchmark (cost_matrix).

Entrada:
    Matriz de custos n×n (lista de listas). Minimização.
    Para maximização, negar a matriz antes de chamar.
"""

import importlib.util
from pathlib import Path
import numpy as np

# Patch de compatibilidade com NumPy ≥ 1.24 (np.int e np.bool foram removidos)
if not hasattr(np, "int"):
    np.int  = int
if not hasattr(np, "bool"):
    np.bool = bool

_ROOT = Path(__file__).parent.parent.parent.parent
_src  = (_ROOT / "repository" / "assignment" / "hungarian"
         / "hungarian-algorithm-mayorx" / "km_matcher.py")
_spec = importlib.util.spec_from_file_location("km_matcher", _src)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def hungarian_mayorx(cost_matrix):
    """
    Resolve o problema de atribuição linear (minimização).

    Parâmetros:
        cost_matrix : matriz de custos n×n (lista de listas).

    Retorno:
        total_cost  : custo total da atribuição ótima
        assignment  : lista onde assignment[i] = j (trabalhador i → tarefa j)
    """
    # KMMatcher maximiza; negamos para obter minimização
    weights = -np.array(cost_matrix, dtype=np.float32)
    matcher = _mod.KMMatcher(weights)
    matcher.solve()

    assignment = [int(j) for j in matcher.xy]
    total_cost = sum(cost_matrix[i][assignment[i]] for i in range(len(cost_matrix)))
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

    total, assignment = hungarian_mayorx(cost)

    print("=== Método Húngaro KM (mayorx) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuição ótima: {assignment}")
    print(f"Custo total mínimo: {total}")
    for i, j in enumerate(assignment):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")
