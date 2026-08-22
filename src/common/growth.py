"""
Expoente empirico de crescimento (AC-12).

O tempo absoluto de um algoritmo depende da linguagem e da maquina; a
**inclinacao** de log(tempo) x log(n) nao. Se o tempo cresce como C * n^k, entao

    log(tempo) = log(C) + k * log(n),

uma reta de inclinacao k no plano log-log. Ajustar essa reta (regressao linear,
`numpy.polyfit`) estima k empiricamente e permite confrontar o medido com a
complexidade teorica -- "o O(n^3) previsto aparece nos dados?".

Como a inclinacao independe de linguagem (muda a constante C, nao k), este e o
unico eixo de comparacao que sobrevive a diferenca Python x compilado sem
ressalva. Alimenta a discussao do capitulo de Resultados e os graficos log-log
do `pgfplots`.
"""

import csv
import math
from pathlib import Path

import numpy as np

from .algorithms import PYTHON
from .result import OK

# Series com menos pontos que isto nao rende ajuste confiavel.
MINIMO_DE_PONTOS = 3


def expoente_empirico(tamanhos, tempos_ms):
    """
    Inclinacao do ajuste linear de log(tempo) x log(n).

    Considera apenas pontos com tamanho e tempo estritamente positivos (log
    exige isso, e tempo zero e ruido de medicao, nao dado). Retorna
    (expoente, r2, n_pontos), ou None quando ha pontos de menos.

    O r2 acompanha o expoente porque uma inclinacao so significa algo se a
    nuvem realmente segue uma reta em log-log; r2 baixo avisa que o regime
    assintotico ainda nao apareceu nos tamanhos medidos.
    """
    pares = [(n, t) for n, t in zip(tamanhos, tempos_ms)
             if n and n > 0 and t and t > 0]
    if len(pares) < MINIMO_DE_PONTOS:
        return None

    log_n = np.array([math.log(n) for n, _ in pares])
    log_t = np.array([math.log(t) for _, t in pares])

    inclinacao, intercepto = np.polyfit(log_n, log_t, 1)

    previsto = inclinacao * log_n + intercepto
    ss_res = float(np.sum((log_t - previsto) ** 2))
    ss_tot = float(np.sum((log_t - log_t.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return float(inclinacao), r2, len(pares)


def _series_por_algoritmo(registros):
    """
    Agrupa os tempos medianos por (instancia, algoritmo), em ordem de n.

    So entram celulas com status OK e tempo medido: timeout, erro e bug nao tem
    tempo comparavel. Preserva o primeiro registro do grupo para os metadados
    (tipo, linguagem, complexidade teorica).
    """
    series = {}
    for r in registros:
        if r.status != OK or r.time_median_ms is None:
            continue
        chave = (r.instance, r.algorithm_key)
        series.setdefault(chave, []).append(r)
    for grupo in series.values():
        grupo.sort(key=lambda r: r.n)
    return series


def resumo_crescimento(registros):
    """
    Uma linha por (instancia, algoritmo) com o expoente empirico ajustado.

    Retorna dicionarios com os metadados do algoritmo, a complexidade teorica
    de tempo (para confronto direto na tabela) e o (expoente, r2, n_pontos).
    Series curtas demais entram com expoente None -- registrar a ausencia e
    melhor que omitir silenciosamente a serie.
    """
    linhas = []
    for (instancia, _), grupo in _series_por_algoritmo(registros).items():
        ref = grupo[0]
        ajuste = expoente_empirico([r.n for r in grupo],
                                   [r.time_median_ms for r in grupo])
        exp, r2, n_pontos = ajuste if ajuste else (None, None, len(grupo))
        linhas.append({
            "problem": ref.problem,
            "instance": instancia,
            "algorithm": ref.algorithm,
            "algorithm_key": ref.algorithm_key,
            "kind": ref.kind,
            "language": ref.language,
            "complexity_time": ref.complexity_time,
            "expoente_empirico": exp,
            "r2": r2,
            "n_pontos": n_pontos,
        })
    return linhas


def gravar_crescimento_csv(registros, caminho):
    """
    Grava o resumo de crescimento em CSV, para a discussao e o `pgfplots`.

    A coluna `complexity_time` fica ao lado de `expoente_empirico` de proposito:
    e a confrontacao "previsto x medido" que o AC-12 pede.
    """
    linhas = resumo_crescimento(registros)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    colunas = ("problem", "instance", "algorithm", "kind", "language",
               "complexity_time", "expoente_empirico", "r2", "n_pontos")
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(colunas)
        for l in linhas:
            escritor.writerow([
                l["problem"], l["instance"], l["algorithm"], l["kind"],
                l["language"], l["complexity_time"],
                "" if l["expoente_empirico"] is None else f"{l['expoente_empirico']:.4f}",
                "" if l["r2"] is None else f"{l['r2']:.4f}",
                l["n_pontos"],
            ])
    return caminho
