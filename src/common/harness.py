"""
Protocolo de medicao dos benchmarks (AC-16).

Centraliza o laco de cronometragem que ate aqui existia em tres copias
divergentes. As garantias que este modulo oferece, e que o codigo anterior nao
tinha:

**Aquecimento descartado.** A primeira execucao paga importacoes tardias,
alocacao inicial e caches frios. Ela nao entra na estatistica -- serve como
sonda do orcamento de tempo e fornece o resultado usado para a qualidade.

**Coletor de lixo desligado durante a medicao.** Uma coleta disparada no meio de
uma repeticao aparece como lentidao do algoritmo. Entre celulas o coletor volta
a rodar, com coleta explicita, para que a memoria nao cresca sem limite.

**Mediana em vez de media.** A media absorve o valor extremo de uma unica
repeticao azarada; a mediana nao. Importa nesta maquina em particular, onde a
CPU e hibrida e o governador de frequencia esta em `powersave` (ver
`results/ambiente.md`).

**Orcamento de tempo por escalonamento (decisao D5).** Se o aquecimento ja
excede o limite, a celula e marcada como `timeout` e **todos os tamanhos
maiores daquele algoritmo, naquela instancia, sao pulados** -- se n=200
estourou, n=250 estouraria tambem. A alternativa, interromper Python puro
ligado a CPU de forma portatil, custaria sobrecusto de processo na propria
regiao medida.

O caso que motivou o orcamento: um wrapper do problema de atribuicao consumiu
1 h 30 min de CPU numa unica celula sem concluir, enquanto outro resolvia a
mesma celula em 110 ms. Sem limite, um unico wrapper defeituoso inviabiliza a
suite inteira.

**Nunca levanta excecao.** Falha de um algoritmo vira `status` no registro e a
suite continua. Defeitos documentados do repositorio sao distinguidos de erros
inesperados: os primeiros sao resultado do trabalho (AC-03), nao falha da
medicao.
"""

import gc
import signal
import statistics
import sys
import time
from contextlib import contextmanager

from .result import ResultRecord, OK, TIMEOUT, ERRO, BUG_CONHECIDO

# Aplicado por `executar_suite`. Varios algoritmos do projeto usam DFS
# recursiva; antes so o benchmark de MCM elevava o limite, e apenas para si.
# Registrar o valor na Metodologia, por ser parametro de execucao.
LIMITE_RECURSAO = 5000

# Interrupcao dura do aquecimento por SIGALRM, disponivel em Unix.
#
# Refinamento da decisao D5: o escalonamento continua valendo (pular tamanhos
# maiores apos um timeout), mas o aquecimento de uma celula patologica nao pode
# rodar ate o fim -- um wrapper do problema de atribuicao consumia 90 min numa
# unica celula. D5 evitava a interrupcao por questao de PORTABILIDADE; como a
# maquina de medicao e Linux (decisao registrada), o alarme e aplicavel. Fora de
# Unix, cai no comportamento mole: mede o aquecimento e so entao verifica.
_TEM_ALARME = hasattr(signal, "setitimer")


class _Interrompido(Exception):
    pass


@contextmanager
def _alarme(timeout_ms):
    if not _TEM_ALARME:
        yield
        return

    def _disparar(signum, frame):
        raise _Interrompido()

    anterior = signal.signal(signal.SIGALRM, _disparar)
    signal.setitimer(signal.ITIMER_REAL, timeout_ms / 1000.0)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, anterior)


def _mediana_ms(amostras):
    return statistics.median(amostras) if amostras else None


def medir(spec, instancia, *, runs, timeout_ms):
    """
    Cronometra um algoritmo sobre uma instancia.

    Retorno:
        (amostras_ms, resultado, status, detalhe)

    `resultado` e o valor devolvido pelo algoritmo na execucao de aquecimento,
    ou None se ela nao concluiu. Reaproveita-lo para extrair a qualidade evita
    a passada extra que o codigo anterior fazia -- ali, cada celula executava o
    algoritmo uma vez a mais so para preencher a tabela de qualidade.
    """
    funcao = spec.fn
    gc.disable()
    try:
        # Aquecimento: descartado da estatistica, serve de sonda do orcamento.
        # Rodado sob alarme duro para que uma celula patologica nao consuma
        # minutos aqui. O alarme envolve SO o aquecimento -- as repeticoes
        # cronometradas rodam limpas, sem o custo de syscall do setitimer, que
        # poluiria medidas de sub-milissegundo.
        inicio = time.perf_counter()
        try:
            with _alarme(timeout_ms):
                resultado = funcao(instancia)
        except _Interrompido:
            return ([], None, TIMEOUT,
                    f"aquecimento interrompido em {timeout_ms:.0f} ms")
        except Exception as e:            # noqa: BLE001 - classificado abaixo
            rotulo = spec.rotulo_de_bug(e)
            if rotulo:
                return [], None, BUG_CONHECIDO, rotulo
            return [], None, ERRO, f"{type(e).__name__}: {e}"[:120]
        aquecimento_ms = (time.perf_counter() - inicio) * 1000

        # Fallback para plataformas sem SIGALRM: o aquecimento rodou ate o fim,
        # so entao verificamos o orcamento.
        if aquecimento_ms > timeout_ms:
            return ([], resultado, TIMEOUT,
                    f"aquecimento levou {aquecimento_ms:.0f} ms, "
                    f"limite {timeout_ms:.0f} ms")

        amostras = []
        for _ in range(runs):
            inicio = time.perf_counter()
            try:
                funcao(instancia)
            except Exception as e:        # noqa: BLE001
                rotulo = spec.rotulo_de_bug(e)
                if rotulo:
                    return amostras, resultado, BUG_CONHECIDO, rotulo
                return amostras, resultado, ERRO, f"{type(e).__name__}: {e}"[:120]
            amostras.append((time.perf_counter() - inicio) * 1000)

        return amostras, resultado, OK, ""
    finally:
        gc.enable()
        gc.collect()


def _aplicar_referencia(registros, chave_referencia):
    """
    Preenche o otimo de referencia e a razao de qualidade de uma celula.

    A referencia sai do proprio conjunto medido, e nao de uma execucao extra:
    o algoritmo eleito como referencia ja participa da suite.

    A razao e `qualidade / referencia` em ambos os sentidos de otimizacao. Cabe
    a cada problema interpreta-la: em maximizacao (cardinalidade) uma heuristica
    fica <= 1; em minimizacao (custo), >= 1.
    """
    if not chave_referencia:
        return

    referencia = next(
        (r.quality for r in registros
         if r.algorithm_key == chave_referencia and r.status == OK
         and r.quality is not None),
        None,
    )
    if referencia is None:
        return

    for r in registros:
        r.reference_optimum = referencia
        if r.quality is not None and referencia != 0:
            r.quality_ratio = r.quality / referencia


def executar_suite(problema, specs, instancias, tamanhos, *,
                   runs=5, timeout_ms=120_000, qualidade_fn,
                   chave_referencia=None, seed=None, escalonar_timeout=True):
    """
    Executa a matriz algoritmos x instancias x tamanhos.

    Parametros:
        problema        : rotulo do problema, ex. "mcm"
        specs           : lista de AlgorithmSpec
        instancias      : lista de (rotulo, construtor), com construtor(n)
                          devolvendo a instancia
        tamanhos        : tamanhos a medir; percorridos em ordem crescente,
                          o que e o que faz o escalonamento do orcamento valer
        runs            : repeticoes cronometradas por celula, alem do
                          aquecimento
        timeout_ms      : orcamento por execucao
        qualidade_fn    : recebe (resultado, instancia) e devolve o valor
                          comparavel -- numero (MCM, atribuicao) ou string
                          (casamento estavel, cuja "qualidade" e estabilidade +
                          concordancia com a referencia). Recebe a instancia
                          porque alguns criterios (pares bloqueantes) dependem
                          dela, nao so da saida do algoritmo.
        chave_referencia: `key` do algoritmo tomado como otimo de referencia
        seed            : semente usada pelos construtores, apenas registrada
        escalonar_timeout: se True (D5), um timeout num tamanho pula os maiores
                          daquele algoritmo na mesma instancia. Desligar quando a
                          monotonicidade nao vale -- um wrapper bugado pode
                          travar num tamanho e falhar rapido em outro maior (caso
                          do `benchaplin`: trava em n=100, lanca AttributeError
                          em n=150+). Ai o escalonamento esconderia o defeito.

    Retorno:
        lista de ResultRecord, uma por celula.

    Todo algoritmo recebe a MESMA instancia -- e o que torna a comparacao
    valida.
    """
    sys.setrecursionlimit(LIMITE_RECURSAO)
    registros = []

    for rotulo_instancia, construtor in instancias:
        # O escalonamento e por instancia: um algoritmo pode degenerar numa
        # familia de instancias e ir bem em outra. Foi o caso observado no
        # benchmark de atribuicao, em que um wrapper nao termina em matrizes
        # densas aleatorias mas resolve as estruturadas em segundos.
        estourados = set()

        for n in sorted(tamanhos):
            instancia = construtor(n)
            da_celula = []

            for spec in specs:
                if spec.key in estourados:
                    da_celula.append(ResultRecord(
                        problem=problema, algorithm=spec.name,
                        algorithm_key=spec.key, kind=spec.kind,
                        language=spec.language, instance=rotulo_instancia,
                        n=n, seed=seed, runs=0,
                        complexity_time=spec.complexity_time,
                        complexity_space=spec.complexity_space,
                        status=TIMEOUT,
                        detail="pulado: excedeu o orcamento num tamanho menor",
                    ))
                    continue

                amostras, resultado, status, detalhe = medir(
                    spec, instancia, runs=runs, timeout_ms=timeout_ms)

                if status == TIMEOUT and escalonar_timeout:
                    estourados.add(spec.key)

                qualidade = None
                if resultado is not None and status in (OK, TIMEOUT):
                    qualidade = qualidade_fn(resultado, instancia)

                da_celula.append(ResultRecord(
                    problem=problema, algorithm=spec.name,
                    algorithm_key=spec.key, kind=spec.kind,
                    language=spec.language, instance=rotulo_instancia,
                    n=n, seed=seed, runs=len(amostras),
                    complexity_time=spec.complexity_time,
                    complexity_space=spec.complexity_space,
                    time_median_ms=_mediana_ms(amostras),
                    time_samples_ms=amostras,
                    quality=qualidade, status=status, detail=detalhe,
                ))

            _aplicar_referencia(da_celula, chave_referencia)
            registros.extend(da_celula)

    return registros
