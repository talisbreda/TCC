"""
Registro de um resultado de benchmark.

Fonte unica de verdade das saidas (decisao D4 da spec tecnica): do
`ResultRecord` derivam o CSV de dados brutos, as tabelas LaTeX levadas ao
documento por `\\input` e a tabela impressa no terminal. Nenhum numero e digitado
a mao no LaTeX, que e o que o AC-22 exige.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

# Desfecho da medicao de uma celula.
OK = "ok"                        # executou e produziu resultado
TIMEOUT = "timeout"              # excedeu o orcamento de tempo (D5)
ERRO = "erro"                    # falhou por motivo nao previsto
BUG_CONHECIDO = "bug_conhecido"  # falhou por defeito documentado do wrapper
STATUS = (OK, TIMEOUT, ERRO, BUG_CONHECIDO)


@dataclass
class ResultRecord:
    """
    Uma celula medida: um algoritmo, sobre uma instancia, num tamanho.

    Campos de identificacao:
        problem     : "mcm" | "assignment" | "bottleneck" | "stable" | "general" | "mim"
        algorithm   : AlgorithmSpec.name -- o ROTULO, nao a chave. E o que o
                      baseline pre-migracao registra, e o que permite a
                      comparacao do AC-17.
        algorithm_key : AlgorithmSpec.key, para uso programatico.
        kind        : "exato" | "heuristica" | "baseline"
        language    : "python" | "c" -- dirige a separacao das tabelas (D8)
        instance    : rotulo da instancia, ex. "Grafo 1 — Esparso ..."
        n           : tamanho
        seed        : semente do gerador, quando houver

    Campos de medicao:
        runs            : repeticoes cronometradas
        time_median_ms  : mediana das repeticoes; None se nao mediu
        time_samples_ms : amostras individuais, para inspecao de variancia
        ops             : contadores de operacoes elementares. Condicional
                          (AC-14, pendente de decisao); vazio para codigo nao
                          instrumentado, inclusive os baselines compilados.

    Campos de qualidade:
        quality           : valor comparavel produzido -- cardinalidade, custo,
                            custo gargalo, pares bloqueantes
        reference_optimum : otimo obtido pelo algoritmo exato de referencia
        quality_ratio     : quality / reference_optimum, para o eixo
                            exato x heuristica (AC-18, AC-21)

    Desfecho:
        status : um de STATUS
        detail : motivo, quando status != ok. Ex. o limite estourado, ou a
                 excecao observada.
    """

    problem: str
    algorithm: str
    algorithm_key: str
    kind: str
    language: str
    instance: str
    n: int
    seed: Optional[int] = None

    runs: int = 0
    time_median_ms: Optional[float] = None
    time_samples_ms: List[float] = field(default_factory=list)
    ops: Dict[str, int] = field(default_factory=dict)

    quality: Optional[float] = None
    reference_optimum: Optional[float] = None
    quality_ratio: Optional[float] = None

    status: str = OK
    detail: str = ""

    def __post_init__(self):
        if self.status not in STATUS:
            raise ValueError(
                f"{self.algorithm_key}: status={self.status!r} invalido; "
                f"esperado um de {STATUS}"
            )

    @property
    def mediu_tempo(self):
        return self.time_median_ms is not None

    def chave_verificacao(self):
        """
        Chave usada na comparacao de nao-regressao do AC-17.

        Casa com a chave produzida por `verify.ler_csv`: identifica a celula
        pelo rotulo do algoritmo, e nao pela chave interna, porque o baseline
        pre-migracao so dispoe do rotulo impresso nas tabelas. A secao fica de
        fora de proposito -- ver `verify.ler_csv`.
        """
        return (self.problem, self.instance, self.algorithm, str(self.n))

    def qualidade_para_verificacao(self):
        """
        Qualidade no formato textual do baseline.

        O baseline registra a celula como impressa: um numero, ou o rotulo do
        desfecho quando nao houve resultado. Reproduzir esse formato e o que
        permite comparar diretamente.
        """
        if self.status == BUG_CONHECIDO:
            return self.detail or "Erro"
        if self.status == TIMEOUT:
            return "timeout"
        if self.status == ERRO:
            return "Erro"
        if self.quality is None:
            return ""
        if float(self.quality).is_integer():
            return str(int(self.quality))
        return str(self.quality)

    def como_dicionario(self):
        """Forma plana, para serializacao. `ops` e achatado em report.py."""
        return asdict(self)
