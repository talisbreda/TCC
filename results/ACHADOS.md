# Achados para o capítulo de Resultados

Registro corrido das observações que emergem da execução dos benchmarks —
matéria-prima da redação da Metodologia (AC-01) e de Resultados/Discussão
(AC-02, AC-03, AC-12). Cada achado indica o AC que alimenta.

Atualizado à medida que os benchmarks são migrados e executados. **Os números
aqui são da máquina de desenvolvimento, não da rodada definitiva** — servem como
observação qualitativa; os valores finais virão da máquina de medição com o
protocolo do `ambiente.md`.

---

## A. Metodologia (AC-01) — ameaças à validade descobertas na própria máquina

- **CPU híbrida (P-core / E-core).** Intel Core 7 150U: CPUs 0-3 são P-cores,
  4-11 são E-cores. O escalonador pode migrar o processo entre eles no meio de
  uma execução, alterando o tempo do mesmo algoritmo sem mudança de código.
  Mitigação: `taskset -c 0`.
- **Governador de frequência em `powersave`.** Frequência oscilou entre 1065 e
  1502 MHz durante medição. Mitigação: fixar `performance` na rodada definitiva.
- **Suspensão da máquina.** O `perf_counter` usa `CLOCK_MONOTONIC`, que congela
  na suspensão — o tempo suspenso não é contabilizado. Mas caches frios e o
  reajuste de frequência ao retomar afetam a célula em voo. Regra: não suspender
  durante a rodada definitiva.
- Consequência: a **mediana** e as repetições do protocolo (AC-16) não são
  preciosismo nesta máquina — são resposta direta a essas duas fontes de
  variação.

## B. Comparação justa por linguagem (AC-02, decisão D8)

- **NetworkX é Python puro**, não código compilado. A premissa inicial de que
  "baseline de biblioteca = C" estava errada. Só `igraph` (núcleo C), `scipy`
  (C/Cython) e o Jonker-Volgenant (`lap`, C++) são compilados.
- Efeito: comparar tempo contra o NetworkX é **legítimo** — todos os algoritmos
  em Python pagam o mesmo custo de interpretador. Vira um resultado mais forte
  que o previsto: implementações de repositório contra uma biblioteca madura, em
  pé de igualdade.
- Zona cinzenta a declarar: `gs_numeric`, `hunalgorithm`, `mayorx` são laços
  Python sobre arrays NumPy — algoritmo interpretado, operações de array
  compiladas. Classificados como `python`, com nota.

## C. Expoente empírico previsto × medido (AC-12)

Ajuste log-log (`numpy.polyfit`), com r² como medida de aderência à reta.

### MCM bipartido (máquina de desenvolvimento, SIZES 50–250)
| Algoritmo | Complexidade teórica | Expoente medido (Grafo 1 / 2 / 3) | r² |
|---|---|---|---|
| Aug. Paths (wbchristerson) | O(V·E) | 1.97 / 2.27 / 2.64 | ≥0.91 |
| Hopcroft-Karp (sofiat) | O(E·√V) | 0.79 / 1.11 / 1.16 | ≥0.98 |
| Edmonds-Karp (Maxflow-Algs) | O(V·E²) | 2.94 / 2.91 / 2.78 | ≥0.999 |
| Hopcroft-Karp (NetworkX) | O(E·√V) | 0.95 / 1.08 / 1.04 | ≥0.96 |
| Bipartite Match. (igraph) | O(E·√V) | 0.80 / 0.80 / 1.07 | ≥0.97 |

- **Edmonds-Karp confirma o cúbico** previsto (~2.9), destacando-se como o mais
  lento em crescimento — coerente com montar matriz de capacidade e refazer BFS.
- **Hopcroft-Karp fica sub-quadrático** (~0.8–1.2), o esperado para O(E√V) em
  grafos esparsos.
- Os expoentes crescem do Grafo 1 (esparso) ao Grafo 3 (denso), o que faz
  sentido: mais arestas, mais trabalho por caminho aumentante.

## D. Defeitos em repositórios públicos (AC-03)

### `benchaplin` (hungarian-algorithm-benchaplin) — problema de atribuição
Três achados distintos sobre o mesmo wrapper, todos só visíveis executando:
1. **Falha** com `AttributeError` (rótulo `BugAttr`) em matrizes densas
   aleatórias a partir de n≈30, de forma **sensível ao conteúdo** — n=50 quebra,
   n=75 e n=100 não. Insere um booleano onde esperava um objeto `Edge`.
2. **Quando não falha, é patologicamente lento.** Em matriz densa n=100, rodou
   **1h30 de CPU sem concluir**, contra 110 ms do munkres na mesma célula.
3. **A degradação não é assintótica suave**: n=75 em 23 s, n=100 sem concluir em
   90 min. Sugere degeneração de estrutura interna, não complexidade alta.
- O ponto 3 é o mais forte para a tese: **implementar e medir revela o que
  catalogar não revela** — não se deduz isso lendo a descrição do algoritmo.

### `hunalgorithm` (HungarianAlgorithm) — problema de atribuição
- Falha com `OSError` (rótulo `BugPerc`) em matrizes densas aleatórias a partir
  de n≈20: excede o limite interno de percolações (`max_num_percolation=20`).
  Também sensível ao conteúdo — matrizes estruturadas passam.
- No baseline: 10 células `BugPerc`, 6 células `BugAttr`.

## E. Notas de instrumentação (Metodologia)

- **Timeout por escalonamento (D5):** sem limite, um único wrapper defeituoso
  (o `benchaplin`) inviabilizou a suíte inteira — evidência empírica, não
  hipótese. O harness marca `timeout` e pula os tamanhos maiores do mesmo
  algoritmo na mesma família de instâncias.
- **Contadores de operação:** cortados do escopo (não compensava manter cópia
  instrumentada de cada repositório). A comparação justa se apoia nas outras
  três camadas: separação por linguagem, complexidade teórica, expoente
  empírico.
- **Reprodutibilidade:** `requirements.txt` fixado; `lap` instala de wheel, sem
  exigir toolchain.

---

## Pendências de observação (preencher ao migrar)
- [ ] Atribuição: expoentes previsto×medido dos húngaros e do SSP (TASK-11)
- [ ] Casamento estável: OOP × numérico × Lattas, efeito do perfil de
      preferência na contenção (TASK-12)
- [ ] Confirmar todos os números na **rodada definitiva** (máquina final)
