# Catálogo de revisão da monografia

Gerado por análise multiagente de todos os capítulos em 2026-08-12.
Alimenta as tarefas de documento (TASK-25 a TASK-33). Cada item traz arquivo e linha.
Achados estruturados por capítulo em `CATALOGO_DOCUMENTO.json`.

---

# Catálogo de Fechamento — Monografia sobre Emparelhamento em Grafos

Consolidação dos achados de revisão dos 11 capítulos, agrupada pelas tarefas do plano de fechamento. Caminhos abreviados a partir de `/home/talis.breda/ufsc/tcc-att/TCC/capitulos/`.

Mapa de arquivos:

| Sigla | Arquivo |
|---|---|
| Introdução | `1_introducao.tex` |
| Fundamentação | `2_fundamentacao.tex` |
| Taxonomia | `3_taxonomia.tex` |
| Bip/CardMax | `4_problemas_bipartido/1_emp_card_max.tex` |
| Bip/Atribuição | `4_problemas_bipartido/2_atribuicao.tex` |
| Bip/MinMax | `4_problemas_bipartido/3_min-max.tex` |
| Bip/Estável | `4_problemas_bipartido/4_casamento_estavel.tex` |
| Ger/CardMax | `5_problemas_gerais/1_emp-card-max.tex` |
| Ger/PondMax | `5_problemas_gerais/2_emp-pond-max.tex` |
| Ger/Induzido | `5_problemas_gerais/3_emp-induzido-max.tex` |
| Futuros | `6_trabalhos_futuros.tex` |

---

## TASK-25 — Reescrever os objetivos da Introdução

Arquivo: `1_introducao.tex`. Pedido do orientador registrado na linha 26.

**Objetivo geral (linha 26) — TEXTO ATUAL:**
> "Este trabalho tem como objetivo principal levantar, organizar, implementar e comparar problemas de emparelhamento em grafos para diversos casos de uso, além de comparar diferentes métodos computacionais presentes na literatura para a solução desses problemas."

Mistura a separar: o verbo composto "levantar, organizar, **implementar e comparar**" funde num só objetivo o ato de (a) implementar os algoritmos e (b) criar o ambiente de testes e testar/comparar. Reescrever separando claramente essas duas frentes.

**Objetivo específico (linha 33) — TEXTO ATUAL:**
> "Implementar os algoritmos descritos, a fim de comparar a complexidade de tempo e espaço, bem como a qualidade das soluções encontradas."

Mistura a separar: o objetivo de implementação já embute a comparação/teste ("a fim de comparar..."). Deve ficar restrito ao ato de **implementar os algoritmos**, movendo a comparação para o item do ambiente de testes.

**Objetivo específico (linha 34) — TEXTO ATUAL:**
> "Criar um ambiente de testes unificado para testar os algoritmos implementados, a fim de reduzir variabilidade nos resultados e proporcionar comparações consistentes"

Este item já isola parcialmente o ambiente de testes. Alinhar a redação com a linha 33 para que "implementar" (33) e "testar/comparar" (34) fiquem em objetivos distintos e não sobrepostos. Falta o ponto final (ver TASK-33).

**Nota correlata:** bloco de parágrafos antigos comentados (linhas 4–12) com versões anteriores da introdução (definição de emparelhamento, aplicações, QAP, GOAT). Decidir remover ou reaproveitar antes da entrega.

---

## TASK-26 — Completar a Taxonomia

Arquivo: `3_taxonomia.tex`. Capítulo curto (23 linhas), `tem_tabela_resumo: false`.

**O que já existe:**
- `\section{Taxonomia dos problemas}` (linha 7) e uma única subseção `\subsection{Classificação Baseada na Estrutura do Grafo e Tipo de Atribuição}` (linha 11).
- Classificação em um único eixo — a estrutura do grafo — via `itemize` com três categorias: Grafos Bipartidos (resolvíveis de forma exata via Húngaro e fluxo em redes, linhas 17–18), Grafos Gerais / não bipartidos (mais complexos, frequentemente por aproximação/heurística, linha 20) e Multigrafos (explicitamente fora do escopo, linha 22).

**O que falta:**
- O título promete classificar por "**Tipo de Atribuição**" (linha 11), mas o corpo só trata da estrutura do grafo. O eixo de atribuição não é desenvolvido.
- O texto introduz implicitamente o eixo **exato × aproximado × heurístico** (linhas 17–20) que a taxonomia deveria formalizar, mas ele não é estruturado.
- Não há tabela-resumo.
- Nomenclatura a padronizar: rótulo "Grafos Gerais" × "grafos não bipartidos" usados como sinônimos (linha 20).

---

## TASK-27 — Pontos didáticos do Maicon (localização de cada)

### 1. BFS em rotina separada
- **Fundamentação, linha 88:** a subseção "Busca em largura (BFS)" **não possui** bloco de pseudocódigo/`\begin{algorithm}`, ao contrário de Dijkstra, Bellman-Ford, Floyd-Warshall e Ford-Fulkerson. Falta o bloco correspondente.
- **Bip/CardMax, linha 142:** `% TODO: separar BFS` — pedido de extrair a BFS do Edmonds-Karp em rotina própria. **NÃO atendido:** a BFS ainda está embutida no laço principal (linhas 182–196).

### 2. Hopcroft-Karp detalhado (Maicon, p.20 — quase linha a linha)
- **Bip/CardMax, linha 225:** `% TODO: melhorar essa explicação`.
- **Bip/CardMax, linha 226:** `% Maicon sugeriu explicar mais a fundo`. **NÃO atendido:** o pseudo-código (linhas 230–308) é apresentado sem explicação linha a linha; há apenas descrição em prosa das duas fases (linhas 221–223).

### 3. Húngaro detalhado
- **Bip/Atribuição, linha 27:** `% TODO: detalhar melhor e explicar as linhas` (referente ao pseudo-código HUNGARIAN/AUGMENT) — atende ao pedido do orientador de detalhar o Húngaro. **Pendente.**

### 4. Referência cruzada de algoritmos (associar método ↔ explicação)
- **Ger/CardMax, linha 51:** `% TODO: (sugestão do Maicon) Associar cada método a parte da explicação`. **AINDA ABERTO** (Maicon p.36): os 4 procedimentos MAXMATCH, BLOSSOM, CONTRACT, AUGMENT (linhas 56–187) são apresentados em bloco, sem vincular cada um aos passos numerados de "O algoritmo de Edmonds" (linhas 40–47).

---

## TASK-28 — Micali-Vazirani

- **Já mencionado? SIM.** Em `5_problemas_gerais/1_emp-card-max.tex`: "Micali e Vazirani" consta na tabela-resumo (linha 246) com complexidade $O(E\sqrt{V})$, e a referência `\citeonline{vazirani}` é usada no texto corrido (linha 49). O feedback TASK-28 / p.39 está **ATENDIDO**.
- **Onde inserir/ajustar:** no texto corrido (linha 49) o algoritmo $O(E\sqrt{V})$ é atribuído apenas a `\citeonline{vazirani}`, enquanto a tabela o nomeia "Micali e Vazirani". Nomear **ambos os autores também no texto corrido** (linha 49), para casar com a tabela.

---

## TASK-29 — Trabalhos futuros (placeholders e ambiente descrito como futuro)

Arquivo: `6_trabalhos_futuros.tex`. Capítulo curto (dois parágrafos, sem subseções nem tabela).

**Placeholders literais N/M/X:**

| Linha | Texto | Placeholder |
|---|---|---|
| 5 | "aprofundamento teórico dos **N** problemas de emparelhamento" | N (quantidade) |
| 5 | "investigação de **M** abordagens heurísticas" | M (quantidade) |
| 7 | "conjunto de **X** instâncias de teste" | X (quantidade) |

**Ambiente descrito como futuro (reescrever para presente/passado — o harness já existe):**
- **Linha 7:** "**será desenvolvido** um ambiente computacional padronizado (framework de testes), onde os algoritmos **serão implementados**" — e "**serão submetidos**". Tempo futuro para um ambiente que já existe no projeto.
- **Linha 7 (nomenclatura):** o mesmo artefato é nomeado de duas formas na mesma frase — "ambiente computacional padronizado (framework de testes)". Fixar um termo único e usá-lo de forma consistente em Metodologia/Resultados.

---

## TASK-30 — Correções

### Complexidades erradas

| Arquivo | Linha | Complexidade atual | Correção |
|---|---|---|---|
| Bip/CardMax | 215 | Dinic $O(E\sqrt{V})$ dito "para grafos gerais" | $O(V^2E)$ em grafos gerais; $O(E\sqrt{V})$ só no caso de capacidade unitária (redução do emparelhamento bipartido). A tabela (linha 355) lista Dinic como $O(E\sqrt{V})$ sem a ressalva — deixar claro que é o caso de capacidade unitária. |
| Bip/Atribuição | 312 | Método Húngaro $O(VE)$ | $O(n^3)$ (ou $O(V^3)$). $O(VE)$ é ambíguo e inconsistente com o restante. |
| Bip/Atribuição | 316 | Jonker-Volgenant $O(VE^2)$ | $O(n^3)$ (ou $O(V^3)$) — complexidade clássica do LAP. |
| Bip/Atribuição | 320 | Custo mínimo (Bellman-Ford) $O(EV)$ | $O(V^2E)$. $O(EV)$ é uma única execução de Bellman-Ford; são necessárias até $V$ iterações/aumentos. Inconsistente com a linha do Dijkstra (324), que corretamente inclui o fator $V$ externo: $O(V(E+V\log V))$. |

**Relacionado (garantia de aproximação, não complexidade):** Ger/PondMax linha 84 — Path Growing (Drake-Hougardy) diz "pelo menos 1/2 da **cardinalidade** máxima"; no problema ponderado a garantia 1/2 é sobre o **peso** total (o próprio comentário da linha 60 registra isso). Corrigir para "peso pelo menos 1/2 do peso máximo (ótimo)".

### Nomenclatura do problema gargalo (todos os nomes usados)

Arquivo: `4_problemas_bipartido/3_min-max.tex`. Escolher UM nome principal, citar sinônimos uma única vez e expandir a sigla uma vez só.

| Nome usado | Linhas |
|---|---|
| "Emparelhamento Min-Max" | 2, 8 |
| "atribuição gargalo" | 4, 8, 17, 75, 83, 238 |
| "Bottleneck Assignment problem" | 8 |
| "problema de gargalo" | 218 |
| "bicos de garrafa" (para bottleneck) | 218 |
| "LBAP" (nunca expandida — Linear Bottleneck Assignment Problem) | 63, 113, 163, 210 |

Notações da mesma grandeza a padronizar no mesmo capítulo: eficiência $w_{ij}$ (max-min) × custo $c_{ij}$ (min-max) (linha 11); `$c\ast$` no texto × `$c^*$` no pseudocódigo (linhas 15+ / 28+); $N$ × $n$ (linha 11 vs pseudocódigos).

### Outras correções técnicas (não-complexidade, para não se perderem)

| Arquivo | Linha | Problema | Correção |
|---|---|---|---|
| Introdução | 14 | Colisão de notação: $G=(V,E)$ e depois $V$ reusado como parte da bipartição ($U$/$V$) | Usar símbolos distintos, ex. $V=A\cup B$, reservando $V$ para todos os vértices |
| Fundamentação | 339 | Balanço de fluxo escrito para o nó $i$, mas o caso do sorvedouro usa "se $j=t$" | Trocar `$-F$ se $j=t$` por `se $i=t$` |
| Fundamentação | 351 | Teorema dos ciclos negativos enunciado como condição de **viabilidade** | É condição de **otimalidade**: "Um fluxo viável $f$ é ótimo sse a rede residual $G(f)$ não contém ciclo de custo negativo" |
| Fundamentação | 330 | Somatório itera sobre $A$ enquanto a rede foi definida como $G=(V,E)$ (linha 325) | Uniformizar $E$ (ou $A$) em toda a subseção de fluxo de custo mínimo |
| Fundamentação | 82, 83, 115, 210 | $\theta$ minúsculo para cota assintótica justa | Usar $\Theta$ maiúsculo |
| Bip/CardMax | 79 | Lema de Berge diz "um **grafo** $G$ é máximo se e somente se não existe caminho aumentante" | Trata de um **emparelhamento** $M$ ser máximo: "$M$ é máximo sse não existe caminho aumentante em $G$ em relação a $M$" |
| Bip/MinMax | 72 | Fórmula de $c^*$ com índices quebrados (índice $k$ livre) | Usar a forma da linha 140: $c^*=\max\{\max_i\min_j c_{ij},\ \max_j\min_i c_{ij}\}$ |
| Bip/MinMax | 11 | Descrição define max-min (eficiência $w_{ij}$) mas todos os algoritmos operam min-max (custo $c_{ij}$) — formulações opostas | Alinhar descrição aos algoritmos (apresentar como min-max de custos desde o início, ou converter coerentemente) |
| Ger/CardMax | 79 | Condição de parada do Repeat usa `$CA(v)$`, mas o vértice processado é $x$ ($v$ indefinido no escopo do MAXMATCH) | Trocar `$CA(v)$` por `$CA(x)$` |
| Ger/PondMax | 84 | "A diferença... é o passo 5, onde os pesos são somados" — a comparação de pesos é o passo 6 (o passo 5 só define M1/M2) | Corrigir referência para "passo 6" (ou reestruturar a lista) |

---

## TASK-31 — Tabela-resumo do casamento estável

- **Ausência confirmada:** `4_problemas_bipartido/4_casamento_estavel.tex` tem `tem_tabela_resumo: false`. NÃO possui tabela-resumo de algoritmos, diferentemente dos outros problemas. Seções: Descrição, Propriedades, Algoritmo de Gale-Shapley — mas sem tabela.

- **Capítulos de problemas que JÁ têm tabela (modelo a seguir):** Bip/CardMax (`tab:emp_card_max_bip_algos`), Bip/Atribuição (`tab:...` linha 300), Bip/MinMax (`tab:atribuicao_gargalo_algos`), Ger/CardMax (`tab:emp_card_max_geral_algos`), Ger/PondMax (`tab:emp_pond_max_gerais`), Ger/Induzido (`tab:emp_induz_max_gerais`).

- **Formato-modelo (descrito em detalhe em Bip/CardMax, `tab:emp_card_max_bip_algos`, linhas 335–372):** `tabularx` de largura `\textwidth`, **4 colunas — Algoritmo | Complexidade de tempo | Tipo | Descrição**, `booktabs` (`\toprule`/`\midrule`/`\bottomrule`), `\arraystretch` 1.2, `\addlinespace` entre linhas, coluna "Tipo" classificada em Exato/Heurística. Este é o formato a replicar no casamento estável (algoritmo de Gale-Shapley, e eventuais variações se desenvolvidas).

- **Nota:** as variações (Stable Roommates, Hospitais/Residentes) estão apenas em comentário (linha 15), não desenvolvidas — se incluídas, entram na tabela.

---

## TASK-32 — Rastreabilidade texto ↔ código (observações úteis)

- **Ger/PondMax:** NÃO há qualquer menção a **van Rantwijk** nem à implementação concreta usada no projeto. O capítulo descreve o Edmonds ponderado apenas teoricamente. Se a Metodologia/Resultados usar `mwmatching.py` (van Rantwijk), networkx ou `lap`, essa origem precisa ser introduzida e justificada aqui. Linha 43/45: cita a implementação $O(V^3)$ de Lawler como "padrão em livros didáticos" — se for a implementada, alinhar.
- **Bip/CardMax, linha 217:** o texto declara explicitamente que "**Este trabalho não tem uma implementação do algoritmo de Dinic**" e que Hopcroft-Karp é apresentado em seu lugar. Metodologia/Resultados devem refletir Dinic fora, HK dentro.
- **Fundamentação, linha 362:** referência `\ref{p:reduction_to_minimal_flow}` anuncia uso de potenciais/custos reduzidos no algoritmo de caminhos sucessivos para o problema de atribuição — o label/seção deve existir adiante.
- **Bip/CardMax, linha 42:** extração de MVC citada como sub-rotina do "Método Dual para o problema de atribuição gargalo" — forward reference a honrar no capítulo do gargalo.
- **Bip/Atribuição:** vários blocos comentados de algoritmos que existem como rascunho e precisam de decisão (Leilão com ε-scaling, Out-of-kilter, Simplex, cost-scaling, Sinkhorn) — ver TASK sem número abaixo.
- **Chaves de citação a verificar no `.bib`:** `garey-jhonson` (Bip/CardMax linha 52 e Ger/Induzido linha 35) — sobrenome "Johnson" grafado errado; conferir para não quebrar a referência.

---

## TASK-33 — Revisão ortográfica (tabela consolidada de TODOS os typos)

| Arquivo | Linha | Erro | Correção |
|---|---|---|---|
| Introdução | 34 | comparações consistentes | falta o ponto final que encerra o item da lista |
| Fundamentação | 10 | uma uma estrutura | uma estrutura |
| Fundamentação | 122 | camino | caminho |
| Fundamentação | 246 | `$c(u,v) \geq o$` | `$c(u,v) \geq 0$` (o zero foi digitado como a letra 'o') |
| Fundamentação | 278 | corretudo | corretude |
| Fundamentação | 278 | caminhhos | caminhos |
| Fundamentação | 325 | rede direcionada one cada aresta | rede direcionada onde cada aresta |
| Fundamentação | 351 | rede resiual | rede residual |
| Fundamentação | 351 | ciclo e custo negativo | ciclo de custo negativo |
| Taxonomia | 18 | Hungaro | Húngaro |
| Bip/CardMax | 79 | maximo | máximo |
| Bip/CardMax | 144 | é p principal método | é o principal método |
| Bip/CardMax | 144 | camino aumentante | caminho aumentante |
| Bip/CardMax | 313 | foram propostas alguns métodos | foram propostos alguns métodos (concordância de gênero) |
| Bip/CardMax | 328 | ele também é única opção | ele também é a única opção (falta o artigo 'a') |
| Bip/CardMax | 333 | resolvia de maneira ótima | resolvida de maneira ótima |
| Bip/CardMax | 337 | cardinaliade máxima | cardinalidade máxima (legenda da tabela) |
| Bip/CardMax | 52 | garey-jhonson | garey-johnson (chave de citação; conferir no `.bib`) |
| Bip/Atribuição | 125 | Finalmente, As arestas | Finalmente, as arestas |
| Bip/MinMax | 15 | selecionar um valor limite, chamando de threshold | chamado de threshold |
| Bip/Estável | 15 | VariaçÕes | Variações (Õ maiúsculo no meio; está em comentário) |
| Bip/Estável | 39 | que continue livre | que continua livre (indicativo, não subjuntivo) |
| Ger/CardMax | 23 | cíclos | ciclos (sem acento) |
| Ger/CardMax | 213 | máxmia | máxima (dentro de bloco comentado) |
| Ger/Induzido | 3 | complexiade | complexidade |
| Ger/Induzido | 3 | pertence à classe os problemas NP-difíceis | pertence à classe dos problemas NP-difíceis |
| Ger/Induzido | 35 | garey-jhonson | garey-johnson (chave de citação; conferir no `.bib`) |

Sem typos: Ger/PondMax (`2_emp-pond-max.tex`), Trabalhos futuros (`6_trabalhos_futuros.tex`).

---

## Insumo para Metodologia / Resultados (o que o texto promete e onde)

**Introdução (`1_introducao.tex`):**
- Implementar os algoritmos descritos na literatura (linhas 26 e 33) — sustentar com implementações concretas.
- Comparar complexidade de tempo/espaço e qualidade das soluções (linha 33) — exige medições e critérios.
- Criar ambiente de testes unificado para reduzir variabilidade e dar comparações consistentes (linha 34) — descreve o harness a detalhar na Metodologia.
- Mapear/classificar variações de problemas e métodos por vantagens/limitações/casos de uso (linhas 31–32) — base da taxonomia/tabelas.
- "Comparação detalhada" entre aplicações e limitações (linha 20) — análise comparativa nos Resultados.
- Delimitação (linha 40): exclui multigrafos e hipergrafos — respeitar na seleção de problemas/algoritmos.

**Fundamentação (`2_fundamentacao.tex`):**
- Linha 242: promete os "teoremas centrais que sustentam os algoritmos utilizados" — a Metodologia precisa empregar/implementar esses algoritmos de fluxo.
- Linha 362: potenciais/custos reduzidos serão usados no algoritmo de caminhos sucessivos para atribuição — seção/label deve existir adiante.
- Linhas 395–396: liga matching ponderado bipartido ao problema de atribuição e ao Húngaro.
- Linhas 412–413: matching máximo bipartido via redução a fluxo — reforça que a abordagem por fluxo será a implementada/avaliada.
- Bloco comentado do Algoritmo de Johnson (linhas 232–238): decisão pendente de inclusão. Capítulo não descreve ambiente de testes (sem hardware/dataset).

**Taxonomia (`3_taxonomia.tex`):**
- Multigrafos NÃO serão abordados (linha 22) — delimitação a manter consistente.
- Bipartidos resolvíveis por Húngaro e fluxo (17–18); gerais frequentemente por aproximação/heurística (20) — introduz o eixo exato × aproximado × heurístico que Resultados devem sustentar por categoria.

**Bip/CardMax (`.../1_emp_card_max.tex`):**
- Linha 217: Dinic NÃO implementado; Hopcroft-Karp em seu lugar.
- Linha 137: Edmonds-Karp como via de solução via redução a fluxo (pseudo-código 146–211) — sustentar.
- Tabela (335–372): 6 algoritmos com complexidades (caminho aumentante $O(VE)$, Edmonds-Karp $O(VE^2)$, Dinic $O(E\sqrt{V})$, Hopcroft-Karp $O(E\sqrt{V})$, gulosa $O(E)$, Karp-Sipser $O(E)$) — os experimentos devem cobri-los ou justificar exclusões (ex. Dinic).
- Alegações quantitativas a verificar: gulosa simples garante ≥ 1/2 da cardinalidade máxima (318); Karp-Sipser resolve a maior parte de grafos esparsos de forma ótima (333).

**Bip/Atribuição (`.../2_atribuicao.tex`):**
- Linhas 111/117: JV "desenvolvido para superar o desempenho prático do Húngaro" e "escolha preferida" — promete comparação prática JV × Húngaro.
- Linha 230: soluções exatas polinomiais "inviáveis para instâncias muito grandes" — claim empírico a demonstrar; heurísticas visam tempo até linear $O(E)$.
- Linha 235: gulosa ordenada com garantia de 1/2 do peso ótimo — verificar/mencionar.
- Tabela (300–333) são os candidatos naturais a confronto empírico.

**Bip/MinMax (`.../3_min-max.tex`):**
- Tabela `tab:atribuicao_gargalo_algos` (236–265): Threshold $O(V^{2.5}/\sqrt{\log V})$, Dual $O(K\cdot E\sqrt{V})$, Caminhos aumentantes $O(EV)$, Gulosa construtiva $O(E\log E)$ — sustentar/verificar se implementados; confirmar fonte do custo do Threshold (fator log dos pesos na busca binária).
- Gulosa construtiva (216–222): critério de "arrependimento" sem garantia quantificada — avaliar em Resultados se implementada.
- Não descreve ambiente de testes nem promete explicitamente experimentos.

**Bip/Estável (`.../4_casamento_estavel.tex`):** sem notas de metodologia/resultados registradas.

**Ger/CardMax (`.../1_emp-card-max.tex`):**
- Linha 49: "maioria das implementações práticas usa variantes próximas de $O(V^3)$" e a versão $O(E\sqrt{V})$ é evitada por complexidade de implementação — usar para justificar escolha de algoritmos.
- Tabela (230): Edmonds $O(V^3)$, Micali-Vazirani $O(E\sqrt{V})$, Gulosa $O(E)$, Karp-Sipser $O(E)$, Path Growing $O(E)$.
- Gulosa/Karp-Sipser reaproveitadas da seção bipartida (201) e Path Growing (216–228) — candidatas a benchmark. Sem ambiente de testes no capítulo.

**Ger/PondMax (`.../2_emp-pond-max.tex`):**
- Sem menção a van Rantwijk nem à implementação concreta — introduzir a origem se usada (ver TASK-32).
- Tabela (98–111): Edmonds $O(V^3)$, Edmonds otimizado $O(EV\log V)$, Gulosa ordenada $O(E\log E)$, Path Growing $O(E)$ — exato × heurísticas a implementar/comparar.
- Linhas 65/69: reutiliza Gulosa Ordenada e Path Growing de outras seções — dependência de que foram de fato implementadas.
- Linha 51: otimizações $O(EV\log V)$, $O(E\sqrt{V\,\alpha(E,V)})$ como baseline teórico; se fora de escopo experimental, deixar claro.

**Ger/Induzido (`.../3_emp-induzido-max.tex`):**
- Linha 48: Guloso Aleatório como "baseline essencial para avaliação de métodos mais sofisticados" — implica comparação baseline × sofisticados.
- Tabela (60–81): Guloso Aleatório e Guloso de grau mínimo, ambos $O(E)$ (justificar quando descritos).
- Metaheurística de busca local (53–58) discutida no texto mas AUSENTE da tabela — decidir se implementada e incluí-la para consistência.

**Trabalhos futuros (`6_trabalhos_futuros.tex`):**
- Linha 5: análise comparativa rigorosa heurísticas × algoritmos exatos; investigar heurísticas e incluir novos problemas.
- Linha 7: ambiente padronizado com instâncias de topologias/dimensões variadas — protocolo experimental para a Metodologia (reescrever tempo futuro, ver TASK-29).
- Linha 7: classificar heurísticas pela relação eficiência (tempo) × qualidade (proximidade do ótimo), usando os exatos como referência — métrica prometida para os Resultados.

---

## Contagem

| Categoria | Total | Distribuição |
|---|---|---|
| Typos (TASK-33) | 27 | Intro 1, Fund 8, Tax 1, Bip/CardMax 8, Bip/Atrib 1, Bip/MinMax 1, Bip/Estável 2, Ger/CardMax 2, Ger/Induzido 3; sem typos: Ger/PondMax, Futuros |
| Erros técnicos (todos) | 16 | Intro 1, Fund 4, Bip/CardMax 2, Bip/Atrib 3, Bip/MinMax 2, Ger/CardMax 1, Ger/PondMax 2; zero: Tax, Bip/Estável, Ger/Induzido |
| — dos quais complexidades erradas (TASK-30) | 4 | Dinic (Bip/CardMax 215), Húngaro (Bip/Atrib 312), Jonker-Volgenant (Bip/Atrib 316), Custo mínimo/Bellman-Ford (Bip/Atrib 320); +1 garantia de aproximação (Ger/PondMax 84) |
| Itens de nomenclatura | 31 | Intro 2, Fund 3, Tax 2, Bip/CardMax 3, Bip/Atrib 3, Bip/MinMax 6, Bip/Estável 2, Ger/CardMax 3, Ger/PondMax 4, Ger/Induzido 3 |
| — nomes distintos do problema gargalo (TASK-30) | 6 | Min-Max, atribuição gargalo, Bottleneck Assignment problem, problema de gargalo, bicos de garrafa, LBAP |
| TODOs / feedback do orientador | 28 | Intro 4, Fund 5, Bip/CardMax 5, Bip/Atrib 7, Bip/MinMax 1, Bip/Estável 1, Ger/CardMax 3, Ger/PondMax 1, Ger/Induzido 1; zero: Tax, Futuros |
| Placeholders N/M/X (TASK-29) | 3 | Futuros linha 5 (N, M), linha 7 (X) |
| Pontos didáticos do Maicon (TASK-27) | 4 frentes / 5 locais | BFS (Fund 88; Bip/CardMax 142), Hopcroft-Karp (Bip/CardMax 225–226), Húngaro (Bip/Atrib 27), ref. cruzada (Ger/CardMax 51) |
| Capítulos SEM tabela-resumo | 5 | Introdução, Fundamentação, Taxonomia, Casamento estável (TASK-31), Trabalhos futuros |
| Capítulos COM tabela-resumo | 6 | Bip/CardMax, Bip/Atrib, Bip/MinMax, Ger/CardMax, Ger/PondMax, Ger/Induzido |

Status dos pedidos rastreados do orientador: TASK-28 (Micali-Vazirani) **ATENDIDO**; BFS separada, Hopcroft-Karp linha a linha, referência cruzada Edmonds e detalhamento do Húngaro **PENDENTES**.
