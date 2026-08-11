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
python src/mcm/mcm_benchmark.py                          # ~45 s
python src/stable-marriage/stable_marriage_benchmark.py  # ~2 min
python src/assignment/assignment_benchmark.py            # dezenas de minutos (ver nota)
```

Os tempos sao de referencia, medidos no ambiente descrito abaixo. Cada benchmark
executa todos os algoritmos do seu problema sobre as **mesmas** instancias e
imprime duas tabelas: tempos de execucao e qualidade da solucao encontrada.

> **Nota sobre o benchmark de atribuicao.** O tempo total e dominado por um
> unico wrapper, o `benchaplin`, sobre as matrizes densas aleatorias: onde os
> demais algoritmos levam milissegundos, ele leva minutos por celula (em n=100,
> mais de 6 minutos para as 5 repeticoes). Nao ha timeout: uma celula lenta roda
> ate o fim. Se quiser uma execucao rapida, remova o `benchaplin` da lista
> `ALGORITHMS_ALL` no topo do arquivo.

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
