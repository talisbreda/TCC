"""
Problema de Atribuicao Gargalo (Bottleneck Assignment Problem - LBAP)
Algoritmos: Heuristica gulosa simples e heuristica gulosa por arrependimento

Complexidade de tempo:  O(n^2 log n)  (ambas; dominada pela ordenacao)
Complexidade de espaco: O(n^2)
Tipo: Heuristica (sem garantia de aproximacao)

Descricao:
    Guloso simples: percorre as n^2 posicoes da matriz em ordem crescente de
    custo e atribui a linha i a coluna j sempre que ambas estao livres. Em uma
    matriz completa o resultado e sempre uma atribuicao perfeita, mas as
    ultimas linhas ficam com as colunas que sobraram, que podem ser caras: o
    gargalo tende a aparecer no final do processo.

    Guloso por arrependimento: a cada passo, calcula para cada linha livre o
    menor e o segundo menor custo entre as colunas livres. O arrependimento
    (regret) da linha e a diferenca entre os dois: o quanto ela perde se a sua
    melhor coluna for tomada por outra. Atende-se primeiro a linha de maior
    arrependimento, atribuindo-a a sua melhor coluna livre. Empates sao
    desfeitos pelo menor custo e, depois, pelo menor indice de linha. Com uma
    unica coluna livre, o arrependimento e infinito (a linha so tem uma opcao).

    E a adaptacao ao LBAP do criterio da heuristica HGAP de Martello e Toth
    para o problema de atribuicao generalizada, que escolhe a cada passo a
    tarefa com a maior diferenca entre a melhor e a segunda melhor atribuicao.

    Implementacao: cada linha guarda suas colunas ordenadas por custo e um
    ponteiro para a primeira ainda livre. Como uma coluna ocupada nunca volta a
    ficar livre, cada ponteiro so avanca, e o total de avancos e O(n^2). Cada
    passo examina as linhas livres em O(n) (mais os avancos), e a ordenacao
    inicial custa O(n^2 log n), que domina.

Fonte:
    S. Martello, P. Toth, "Linear Assignment Problems", em Surveys in
    Combinatorial Optimization, North-Holland, 1987, secao 5.4 (HGAP).

Entrada:
    Matriz de custos n x n (lista de listas). Minimizacao do custo maximo.
"""

import math


def assignment_bottleneck_greedy(cost_matrix):
    """
    Guloso simples para o LBAP.

    Retorno:
        bottleneck_cost : maior custo na atribuicao encontrada
        assignment      : lista onde assignment[i] = j
    """
    n = len(cost_matrix)
    if n == 0:
        return 0, []

    posicoes = sorted((cost_matrix[i][j], i, j) for i in range(n) for j in range(n))
    assignment = [-1] * n
    coluna_livre = [True] * n
    atribuidas = 0
    gargalo = 0
    for custo, i, j in posicoes:
        if assignment[i] == -1 and coluna_livre[j]:
            assignment[i] = j
            coluna_livre[j] = False
            gargalo = max(gargalo, custo)
            atribuidas += 1
            if atribuidas == n:
                break
    return gargalo, assignment


def assignment_bottleneck_regret(cost_matrix):
    """
    Guloso por arrependimento para o LBAP.

    Retorno:
        bottleneck_cost : maior custo na atribuicao encontrada
        assignment      : lista onde assignment[i] = j
    """
    n = len(cost_matrix)
    if n == 0:
        return 0, []

    ordem = [sorted(range(n), key=lambda j, i=i: cost_matrix[i][j]) for i in range(n)]
    ponteiro = [0] * n
    coluna_livre = [True] * n
    linhas_livres = set(range(n))
    assignment = [-1] * n
    gargalo = 0

    def duas_melhores(i):
        """Primeira e segunda colunas livres de menor custo da linha i."""
        while not coluna_livre[ordem[i][ponteiro[i]]]:
            ponteiro[i] += 1
        primeira = ordem[i][ponteiro[i]]
        k = ponteiro[i] + 1
        while k < n and not coluna_livre[ordem[i][k]]:
            k += 1
        segunda = ordem[i][k] if k < n else None
        return primeira, segunda

    while linhas_livres:
        melhor = None  # (arrependimento, -custo, -linha, linha, coluna)
        for i in linhas_livres:
            j1, j2 = duas_melhores(i)
            c1 = cost_matrix[i][j1]
            arrependimento = math.inf if j2 is None else cost_matrix[i][j2] - c1
            chave = (arrependimento, -c1, -i)
            if melhor is None or chave > melhor[0]:
                melhor = (chave, i, j1)
        _, i, j = melhor
        assignment[i] = j
        coluna_livre[j] = False
        linhas_livres.remove(i)
        gargalo = max(gargalo, cost_matrix[i][j])
    return gargalo, assignment
