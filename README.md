# Emparelhamento em Grafos — TCC

Levantamento comparativo de problemas e algoritmos de emparelhamento em grafos:
a monografia em LaTeX e o ambiente de testes que produz os resultados
apresentados nela.

## Estrutura

| Diretorio | Conteudo |
|---|---|
| `main.tex`, `capitulos/`, `pre_textual/`, `pos_textual/` | Monografia em LaTeX |
| `repository/` | Codigo-fonte **externo** dos algoritmos, um subdiretorio por problema. Nao e modificado |
| `src/` | *Wrappers* que adaptam o codigo de `repository/` a uma interface padrao por problema, e os benchmarks comparativos |
| `specs/` | Artefatos de especificacao do trabalho (contexto, discovery, specs e plano) |

Os algoritmos sao mantidos em `repository/` na forma em que foram obtidos, para
que o codigo que produziu os numeros publicados permaneca junto da monografia.
Cada wrapper em `src/` documenta no cabecalho a fonte original e a URL do
repositorio de onde veio.

## Requisitos

- Python 3.12 ou superior
- As dependencias de `requirements.txt`

## Instalacao

A partir da raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Execucao dos benchmarks

Cada problema tem um benchmark proprio, executavel de forma independente:

```bash
python src/mcm/mcm_benchmark.py                          # MCM bipartido (~1 min)
python src/stable-marriage/stable_marriage_benchmark.py  # casamento estável (~2 min)
python src/bottleneck/bottleneck_benchmark.py            # atribuição gargalo
python src/general/general_benchmark.py                  # grafos gerais (card. + peso)
python src/mim/mim_benchmark.py                          # emparelhamento induzido máximo
python src/assignment/assignment_benchmark.py            # atribuição (dezenas de min; ver nota)
```

Cada benchmark grava em `results/`: `<problema>.csv` (dados brutos),
`<problema>-qualidade.csv` (canônico, para a verificação de não-regressão),
`<problema>-crescimento.csv` (expoente empírico) e tabelas LaTeX em
`results/tex/` prontas para `\input` no documento.

Os tempos sao de referencia, medidos no ambiente descrito abaixo. Cada benchmark
executa todos os algoritmos do seu problema sobre as **mesmas** instancias e
imprime duas tabelas: tempos de execucao e qualidade da solucao encontrada.

> **Nota sobre o benchmark de atribuicao.** O tempo e dominado pelo wrapper
> `benchaplin` nas matrizes densas aleatorias: numa celula ele pode levar minutos
> onde os demais levam milissegundos. O harness aplica um timeout por celula
> (SIGALRM, em Linux), entao a suite conclui mesmo assim -- a celula estourada e
> marcada como `timeout`. O `benchaplin` tambem e NAO-DETERMINISTICO entre
> processos (ver `results/ambiente.md`); fixe `PYTHONHASHSEED` para reproduzir.

Como a saida e redirecionada para arquivo o Python usa buffer de bloco, e o
progresso so aparece em lotes. Use `python -u` para acompanhar em tempo real.

Nao e necessario ativar o venv se o interpretador for chamado diretamente:

```bash
.venv/bin/python src/mcm/mcm_benchmark.py
```

## Ambiente de referencia das medicoes

Os resultados publicados na monografia sao obtidos neste ambiente:

- Ubuntu 24.04.2 LTS
- Python 3.12.3
- Dependencias nas versoes fixadas em `requirements.txt`

Resultados obtidos em outra maquina nao sao comparaveis aos publicados e nao
devem ser misturados a eles.

## Notas sobre os benchmarks

**Comparacao entre linguagens.** Nem todos os algoritmos executam na mesma
linguagem. `networkx` e Python puro e compara de igual para igual com os
wrappers do projeto; `scipy` e `igraph` tem nucleo compilado em C e servem como
referencia de implementacao consolidada, nao como concorrentes diretos em tempo
de execucao.

**Bugs conhecidos.** Dois wrappers do problema de atribuicao falham em
condicoes especificas, por defeito dos repositorios de origem. As falhas sao
capturadas e exibidas na tabela em vez de interromper a execucao:

- `BugAttr` — `hungarian-algorithm-benchaplin`: em matrizes densas aleatorias
  (n >= ~30), insere um booleano onde esperava um objeto `Edge`. Quando **nao**
  falha nessas matrizes, e ordens de grandeza mais lento que os demais.
- `BugPerc` — `HungarianAlgorithm`: em matrizes densas aleatorias (n >= ~20),
  excede o limite interno de percolacoes e lanca `OSError`.

Ambos estao documentados no cabecalho dos respectivos wrappers em `src/`.

## Compilacao da monografia

```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
