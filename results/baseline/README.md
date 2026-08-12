# Baseline pre-migracao

Saida dos benchmarks **antes** da migracao para o harness compartilhado
(`src/common/`). Artefato de referencia do **AC-17**: a qualidade produzida
depois da migracao deve ser identica a registrada aqui.

Capturado em 2026-08-11 (TASK-02), na maquina descrita em `results/ambiente.md`.

## Arquivos

| Arquivo | Conteudo |
|---|---|
| `<problema>.txt` | Saida bruta do benchmark, como impressa no terminal |
| `<problema>-qualidade.csv` | Baseline **canonico**: `(problema, secao, instancia, algoritmo, n) -> qualidade` |
| `assignment-celulas-cortadas.txt` | Chamadas interrompidas por orcamento de tempo (ver ressalva) |
| `assignment-captura.log` | Log da captura do benchmark de atribuicao |

O CSV canonico e gerado por `src/common/verify.py` e e o arquivo que importa
para a verificacao. O `.txt` fica como registro do formato original.

## Cobertura

| Problema | Registros | Chaves unicas | Execucao |
|---|---|---|---|
| MCM | 75 | 75 | `EXIT=0` em 44 s |
| Casamento estavel | 60 | 60 | `EXIT=0` em 1 min 46 s |
| Atribuicao | 183 | 183 | `EXIT=0` em 11 min (com orcamento) |

Bugs conhecidos preservados no baseline de atribuicao: **6 celulas `BugAttr`** e
**10 celulas `BugPerc`**. O AC-17 exige que continuem sendo capturados e
exibidos apos a migracao, nao mascarados nem corrigidos.

## Ressalva: duas celulas nao foram capturadas

Duas celulas do benchmark de atribuicao aparecem como `Erro` na tabela **sem
serem erro do algoritmo**:

    Matriz 1 (densa uniforme) | Hungaro (benchaplin) | n=100   -- Secao 1 e Secao 2

O `benchaplin` nessa celula **nao termina em tempo praticavel**. A primeira
tentativa de captura rodou **1 h 30 min de CPU numa unica celula** sem concluir,
e foi interrompida. A captura definitiva adotou um orcamento de 120 s por
chamada; essas duas celulas o excederam.

Para dimensionar: na mesma celula, o `munkres` leva **110 ms** para as cinco
repeticoes.

Nao e crescimento assintotico alto, e degeneracao: o mesmo algoritmo faz
`n=75` em 23 s e nao conclui `n=100` em 90 minutos.

### Consequencia para a verificacao do AC-17

Essas duas chaves nao tem valor de qualidade de referencia. Apos a migracao,
elas serao marcadas como `timeout` pelo harness (decisao D5), e **isso nao conta
como regressao** -- conta como cobertura reduzida, conforme a regra registrada
na decisao D10 da spec tecnica.

### Consequencia para o capitulo de Resultados

E insumo do **AC-03**. O `benchaplin` rende tres achados distintos sobre o mesmo
repositorio publico:

1. **Falha** com `AttributeError` em matrizes densas a partir de n ~ 30, de forma
   sensivel ao conteudo da matriz -- `n=50` quebra, `n=75` e `n=100` nao.
2. **Quando nao falha, e patologicamente lento** -- ordens de grandeza acima dos
   demais na mesma celula.
3. **A degradacao nao e suave** -- sugere que alguma estrutura interna degenera,
   e nao que a complexidade assintotica seja alta.

O terceiro so aparece executando o codigo: nao se deduz lendo a descricao do
algoritmo.

## Ressalva: os tempos deste baseline nao servem para a monografia

As colunas de tempo foram medidas sem `taskset`, com o governador de frequencia
em `powersave` e com outras aplicacoes ativas. Para o AC-17 isso e irrelevante
-- a comparacao e de **qualidade**, nao de tempo.

Os tempos publicados no capitulo de Resultados serao medidos na rodada
definitiva, com o protocolo do harness (AC-16) e o procedimento de
`results/ambiente.md`.

## Como regenerar o CSV canonico

```bash
python src/common/verify.py extrair results/baseline/mcm.txt mcm
python src/common/verify.py extrair results/baseline/stable-marriage.txt stable-marriage
python src/common/verify.py extrair results/baseline/assignment.txt assignment
```

## Como verificar ausencia de regressao (TASKs 10-12)

```bash
python src/common/verify.py comparar \
    results/baseline/<problema>-qualidade.csv \
    results/<problema>-qualidade.csv
```

Retorna `0` se as qualidades forem identicas e `1` listando as divergencias.
