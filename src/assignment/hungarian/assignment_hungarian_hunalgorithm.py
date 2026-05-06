"""
Problema de Atribuição (Assignment Problem)
Algoritmo: Método Húngaro (HungarianAlgorithm)

Complexidade de tempo: O(n³)
Tipo: Exato

Descrição:
    Implementação do algoritmo húngaro baseada em redução de linha/coluna
    e busca de 0-percolações (atribuições completas com custo zero na
    matriz reduzida). Quando a percolação com menor índice de redundância
    não é perfeita, aplica o operador "shaker" para criar novos zeros.

    Requer numpy. A função retorna a lista de percolações ótimas; o wrapper
    extrai a primeira como atribuição.

    Limitação: o parâmetro max_num_percolation (padrão=10) limita o número
    de percolações exploradas. Matrizes com muitos zeros podem exigir um
    valor maior; neste wrapper usamos 20 como margem de segurança.

Fonte original:
    Autor desconhecido — https://github.com/pbertoni/HungarianAlgorithm
    Arquivo: HungarianAlgorithm/model.py
    Adaptado para a interface padrão do benchmark (cost_matrix).

Entrada:
    Matriz de custos n×n (lista de listas). Minimização.
"""

import importlib.util
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).parent.parent.parent.parent
_src  = (_ROOT / "repository" / "assignment" / "hungarian"
         / "HungarianAlgorithm" / "HungarianAlgorithm" / "model.py")
_spec = importlib.util.spec_from_file_location("ha_hunalgorithm", _src)
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def hungarian_hunalgorithm(cost_matrix):
    """
    Resolve o problema de atribuição linear (minimização).

    Parâmetros:
        cost_matrix : matriz de custos n×n (lista de listas).

    Retorno:
        total_cost  : custo total da atribuição ótima
        assignment  : lista onde assignment[i] = j (trabalhador i → tarefa j)
    """
    m = np.matrix(cost_matrix, dtype=float)
    filtered_walks = _mod.hungarian(m, max_num_percolation=20)

    # filtered_walks[0] é a percolação ótima: lista onde índice = linha, valor = coluna
    assignment = list(filtered_walks[0])
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

    total, assignment = hungarian_hunalgorithm(cost)

    print("=== Método Húngaro (HungarianAlgorithm / pbertoni) ===")
    print("Matriz de custos:")
    for row in cost:
        print(" ", row)
    print(f"\nAtribuição ótima: {assignment}")
    print(f"Custo total mínimo: {total}")
    for i, j in enumerate(assignment):
        print(f"  Trabalhador {i} -> Tarefa {j}  (custo {cost[i][j]})")
