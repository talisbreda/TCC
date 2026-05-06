"""
Problema de Atribuição (Assignment Problem)
Algoritmo: Método Húngaro (Munkres)

Complexidade de tempo: O(n³)
Tipo: Exato

Descrição:
    Implementação do algoritmo de Munkres (também chamado de Húngaro ou
    Kuhn-Munkres) por Brian Clapper. Opera diretamente sobre lista de listas,
    sem dependências externas (Python puro).

    O método `compute` retorna os pares (linha, coluna) da atribuição ótima
    de custo mínimo.

Fonte original:
    Brian Clapper — https://github.com/bmc/munkres
    Arquivo: munkres.py
    Adaptado para a interface padrão do benchmark (cost_matrix).

Entrada:
    Matriz de custos n×n (lista de listas). Minimização.
    Para maximização, usar make_cost_matrix para negar antes de chamar.
"""

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
_src  = _ROOT / "repository" / "assignment" / "hungarian" / "munkres" / "munkres.py"
_spec = importlib.util.spec_from_file_location("munkres", _src)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def hungarian_munkres(cost_matrix):
    """
    Resolve o problema de atribuição linear (minimização).

    Parâmetros:
        cost_matrix : matriz de custos n×n (lista de listas).

    Retorno:
        total_cost  : custo total da atribuição ótima
        assignment  : lista onde assignment[i] = j (trabalhador i → tarefa j)
    """
    import copy
    indices = _mod.Munkres().compute(copy.deepcopy(cost_matrix))

    assignment = [-1] * len(cost_matrix)
    for i, j in indices:
        assignment[i] = j

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

    total, assignment = hungarian_munkres(cost)

    print("=== Método Húngaro (munkres / Brian Clapper) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuição ótima: {assignment}")
    print(f"Custo total mínimo: {total}")
    for i, j in enumerate(assignment):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")
