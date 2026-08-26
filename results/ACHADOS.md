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


- [x] Atribuição: expoentes registrados (seção G); benchaplin não-determinístico (seção F)
- [x] Casamento estável: expoentes registrados (seção I); OOP confirma super-quadrático prático
      preferência na contenção (TASK-12)
- [ ] Confirmar todos os números na **rodada definitiva** (máquina final)

---

## F. ACHADO PRINCIPAL — não-determinismo do `benchaplin` (AC-03)

Descoberto ao migrar o benchmark de atribuição para o harness (TASK-11). É o
achado mais forte do trabalho até aqui.

**O `benchaplin`, sobre a MESMA matriz, produz resultados diferentes em processos
diferentes.** Em `build_cost_1(75)` (matriz densa, seed fixa): retornou o custo
correto **238 em 4 de 6 processos** e falhou com `AttributeError` (`BugAttr`) nos
outros 2. Com `PYTHONHASHSEED=0` fixo, falha consistentemente (3/3).

**Causa:** o bug depende da **ordem de iteração de um conjunto/dicionário de
objetos**, que o Python randomiza por processo (hash de objetos = `id()`, que
varia com o endereço de memória). Não é aleatoriedade do algoritmo — é o próprio
defeito sendo disparado ou não conforme a ordem em que as arestas são visitadas.

**Três desfechos possíveis para a mesma entrada**, todos observados:
1. retorna o custo correto (238);
2. falha rápido com `AttributeError`;
3. entra num caminho lento e não conclui (a célula n=100 densa que rodou 1h30).

**Por que isso é forte para a tese:** ilustra de forma vívida que *implementar e
medir revela o que catalogar não revela*. Um levantamento bibliográfico jamais
apontaria que esta implementação pública do método Húngaro é não-determinística
— o comportamento só emerge executando o código repetidamente. Reforça
diretamente o objetivo (c)/(d) do trabalho.

**Consequências metodológicas:**
- A verificação de não-regressão (AC-17) **exclui o benchaplin** da comparação
  estrita, tratando-o como não-determinístico conhecido (`verify.py` ganhou esse
  suporte). Os 5 algoritmos determinísticos batem exatos entre baseline e
  harness — a migração não introduziu regressão.
- **Reprodutibilidade:** a rodada definitiva deve fixar `PYTHONHASHSEED` (ver
  `ambiente.md`). O valor escolhido determina o desfecho do benchaplin nas
  células de fronteira; reportar o desfecho sob o seed fixado E a observação de
  que ele varia com o seed.

## G. Expoente empírico — atribuição (matriz densa, TASK-11)

| Algoritmo | Teórico | Medido | r² |
|---|---|---|---|
| Húngaro (munkres) | O(n³) | 2.30 | 0.998 |
| Húngaro (mayorx/KM) | O(n³) | 1.39 | 0.979 |
| SSP (flows) | O(n⁴)* | 2.75 | 0.997 |
| SciPy (linear_sum_assg) | O(n³) | 1.84 | 0.974 |

- **munkres ≈2.3** fica abaixo do cúbico teórico na faixa medida — o termo n³ só
  domina em n maior; nos tamanhos testados o comportamento ainda é sub-cúbico.
- **mayorx e SciPy crescem devagar (~1.4–1.8)** — implementações vetorizadas
  (NumPy) e compilada (C) escondem constante, mas o expoente também sai baixo na
  faixa, indicando que não atingiram o regime assintótico.
- **SSP ≈2.75**: o pior caso O(n⁴) não se materializa nas matrizes densas
  testadas (o número de aumentos fica bem abaixo do pior caso).
- Leitura para a discussão: nos tamanhos práticos, o expoente medido costuma
  ficar **abaixo** do teórico — a complexidade de pior caso é conservadora.

## H. Refinamento do harness na migração da atribuição (Metodologia)

- **Timeout duro por SIGALRM.** O timeout "mole" original (medir o aquecimento e
  só então checar) fazia a célula patológica do benchaplin rodar 90 min antes de
  ser marcada. Como a máquina de medição é Linux, o aquecimento passou a rodar
  sob `SIGALRM`, cortando em tempo real. Refina D5 sem revogá-la.
- **Escalonamento desligável.** O escalonamento (pular tamanhos maiores após um
  timeout) pressupõe monotonicidade, que o benchaplin viola (trava em n=100,
  falha rápido em n=150+). Desligado no benchmark de atribuição para não
  esconder as células `BugAttr` dos tamanhos maiores.

## I. Expoente empírico — casamento estável (Perfil 1, TASK-12)

| Algoritmo | Teórico | Medido | r² |
|---|---|---|---|
| Gale-Shapley (OOP/pip) | O(n²)† | 3.29 | 0.996 |
| Gale-Shapley (numérico/pip) | O(n²) | 1.91 | 0.997 |
| Gale-Shapley (Lattas/dict) | O(n³)* | 2.10 | 0.999 |

- **OOP mede ~3.3, muito acima do O(n²) teórico** — e isto CONFIRMA a ressalva
  já anotada no código: o sobrecusto por objeto (reconstrução das listas de
  livres a cada rodada) a torna praticamente super-quadrática, "inviável acima
  de n≈100". O medido valida a teoria da anotação, não a contradiz.
- **numérico ≈1.9 bate com O(n²)** — a implementação vetorizada (NumPy) realiza
  a complexidade teórica.
- **Lattas ≈2.1, abaixo do O(n³)\* de pior caso** — o `.index()` em lista a cada
  rejeição não domina nos perfis testados.
- Reforço da leitura geral: o expoente medido tende a ficar ABAIXO do teórico
  (pior caso conservador), EXCETO quando há sobrecusto de implementação (OOP),
  em que fica ACIMA — dois modos de divergência previsto×medido, ambos
  interpretáveis.

Nota: os três algoritmos produzem "0 =ref" em todas as células (emparelhamento
men-optimal único por teorema) — a qualidade não distingue; só tempo e expoente.

## J. Eixo exato × heurística — MCM (AC-18, TASK-13)

Heurísticas implementadas à mão (gulosa simples e Karp-Sipser), verificadas
independentemente: 800 checagens de força bruta sem falha, KS ótimo em todas as
florestas testadas, e contra Hopcroft-Karp a pior razão foi gulosa 0.756 / KS
0.971 em grafos aleatórios grandes.

Razão de qualidade (heurística / ótimo) nos grafos do benchmark:

| Heurística | Grafo 1 (esparso) | Grafo 2 (c/ perfeito) | Grafo 3 (denso) |
|---|---|---|---|
| Gulosa | 0.925–0.958 | **0.850–0.860** | 0.930–0.942 |
| Karp-Sipser | **1.000** | **1.000** | 0.996–0.999 |

- **Karp-Sipser encontra o ótimo exato** nos grafos esparsos e fica a <0.5% no
  denso — confirma empiricamente a força da regra do grau 1 (a fase determinística
  do algoritmo já casa quase tudo em grafos esparsos).
- **A gulosa perde de forma visível**, sobretudo no Grafo 2 (~15% abaixo do
  ótimo): a ordem de varredura das arestas a prende em emparelhamentos maximais
  pequenos.
- É o **trade-off qualidade × custo** central do objetivo (d): a gulosa é O(E)
  mas sacrifica qualidade; KS é O(V·E) e entrega qualidade ~ótima. Ambas muito
  mais baratas que os exatos.

Nota metodológica: a razão de qualidade sai automaticamente do harness
(`quality_ratio`), com Hopcroft-Karp (sofiat) como referência de ótimo.

## K. Jonker-Volgenant nominal (AC-24, TASK-14)

Wrapper da biblioteca `lap` (`lap.lapjv`, núcleo C++) adicionado ao benchmark de
atribuição. Antes, o JV só aparecia implícito dentro do SciPy; agora tem linha
própria na tabela de compilados.

- Verificado contra SciPy em 120 matrizes adversariais (negativos, empates,
  estruturadas): custo idêntico em todos os casos. No benchmark, 27/27 células
  batem com o SciPy — o esperado, já que ambos resolvem o LAP de forma exata.
- Valor para o trabalho: permite comparar **duas implementações compiladas
  independentes do mesmo problema** (SciPy usa uma variante de shortest
  augmenting path; `lap` implementa Jonker-Volgenant clássico) — comparação de
  qualidade de implementação a algoritmo fixo, sem a ressalva Python×C.

## Reprodutibilidade confirmada

Com `PYTHONHASHSEED=0`, os algoritmos determinísticos reproduzem o baseline
exatamente. As únicas divergências restantes são as células de fronteira do
`benchaplin` (não-determinístico), corretamente classificadas como ruído
conhecido pela verificação, não como regressão.
