# Ambiente de medicao

Especificacao da maquina onde os resultados publicados na monografia sao
obtidos. Insumo do capitulo de Metodologia (AC-01).

**Todos os resultados finais saem desta maquina.** Numeros obtidos em outro
ambiente nao sao comparaveis e nao devem ser misturados aos publicados.

Registrado em 2026-08-11 (TASK-04).

## Hardware

| Item | Valor |
|---|---|
| Processador | Intel Core 7 150U |
| Arquitetura | x86_64 |
| Nucleos | 10 fisicos / 12 threads |
| Topologia | **Hibrida**: 2 P-cores com hyperthreading (CPUs 0-3) + 8 E-cores (CPUs 4-11) |
| Frequencia | 400 MHz - 1800 MHz |
| Memoria | 33 GB |

## Software

| Item | Versao |
|---|---|
| Sistema | Ubuntu 24.04.2 LTS |
| Kernel | 7.0.0-28-generic |
| Python | 3.12.3 |
| numpy | 2.5.2 |
| scipy | 1.18.0 |
| networkx | 3.6.1 |
| igraph | 1.0.0 |
| texttable | 1.7.0 |

## Ameacas a validade das medicoes

Duas caracteristicas desta maquina afetam a reprodutibilidade dos tempos e
precisam ser declaradas na Metodologia.

### 1. CPU hibrida (P-core / E-core)

Os nucleos **nao sao equivalentes**. O escalonador do sistema pode migrar o
processo entre um P-core e um E-core durante a execucao, fazendo o mesmo
algoritmo, sobre a mesma instancia, levar tempos substancialmente diferentes sem
qualquer mudanca no codigo.

**Mitigacao:** fixar a execucao num P-core especifico.

```bash
taskset -c 0 .venv/bin/python src/mcm/mcm_benchmark.py
```

### 2. Governador de frequencia em `powersave`

A frequencia varia dinamicamente (observados 1065-1502 MHz durante medicao),
o que introduz variacao entre repeticoes da mesma celula.

**Mitigacao:** fixar o governador em `performance` durante a rodada definitiva.
Exige privilegio administrativo:

```bash
sudo cpupower frequency-set -g performance   # antes da rodada
sudo cpupower frequency-set -g powersave     # depois
```

Se o governador nao for alterado, a variacao deve ser declarada como limitacao,
e o uso da **mediana** de varias repeticoes (AC-16) ja a atenua parcialmente.

### 3. Suspensao da maquina durante a rodada

Nao suspender a maquina durante uma execucao que gere numeros para a monografia.

O relogio nao e o problema: o `time.perf_counter` usa `CLOCK_MONOTONIC`, que
congela junto com a maquina, entao o tempo suspenso **nao** e contabilizado. O
problema e o estado apos retomar -- caches frios e governador de frequencia
reajustando afetam a celula que estava em execucao.

### 4. Aleatoriedade de hash entre processos (`PYTHONHASHSEED`)

Descoberto na migração do benchmark de atribuição: o wrapper `benchaplin` é
**não-determinístico entre processos** — sobre a mesma matriz, ora retorna o
custo correto, ora falha com `AttributeError`, conforme a ordem de iteração de
um conjunto de objetos, que o Python randomiza por processo.

**Mitigação:** fixar `PYTHONHASHSEED` na rodada definitiva, para que os
resultados sejam reproduzíveis. O valor escolhido determina o desfecho do
benchaplin nas células de fronteira; a Metodologia deve reportar o desfecho sob
o seed fixado **e** a observação de que ele varia com o seed.

```bash
PYTHONHASHSEED=0 taskset -c 0 .venv/bin/python src/assignment/assignment_benchmark.py
```

## Procedimento da rodada definitiva

1. Fechar aplicacoes pesadas (navegador, IDE)
2. Fixar o governador em `performance`
3. Executar cada benchmark com `PYTHONHASHSEED=0 taskset -c 0`
4. Nao suspender a maquina
5. Restaurar o governador
