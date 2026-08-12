"""
Descricao de um algoritmo participante de um benchmark.

Substitui a tupla de quatro posicoes `(nome, complexidade, tipo, fn)` usada ate
aqui pelos tres benchmarks (decisao D2 da spec tecnica). A troca resolve dois
problemas concretos.

**Campos que faltavam.** A tupla nao comportava a complexidade de espaco
(pedido do Prof. Maicon, p. 7 do feedback de TCC I) nem a linguagem de
implementacao, que dirige a separacao das tabelas do AC-02.

**Selecao posicional.** As secoes secundarias dos benchmarks eram montadas por
fatia -- `ALGORITHMS_ALL[:4] + [ALGORITHMS_ALL[5]]` -- de modo que inserir um
algoritmo na lista principal alterava a composicao da secao em silencio. Com
`key`, a selecao passa a ser nomeada e falha alto quando a chave nao existe.
"""

from dataclasses import dataclass
from typing import Callable, Optional

# Garantia de otimalidade do metodo.
EXATO = "exato"
HEURISTICA = "heuristica"
BASELINE = "baseline"
TIPOS = (EXATO, HEURISTICA, BASELINE)

# Linguagem em que o algoritmo executa de fato.
#
# Classifica a IMPLEMENTACAO, nao a origem (decisao D8): o NetworkX e uma
# biblioteca, mas e Python puro, entao compara de igual para igual com os
# wrappers de repositorio. Somente igraph, SciPy e o Jonker-Volgenant sao
# codigo compilado.
PYTHON = "python"
C = "c"
LINGUAGENS = (PYTHON, C)


@dataclass(frozen=True)
class AlgorithmSpec:
    """
    Um algoritmo dentro de um benchmark.

    Campos:
        key              : identificador estavel, usado para selecao nomeada.
                           Nao aparece nas tabelas.
        name             : rotulo exibido nas tabelas e no CSV.
        complexity_time  : complexidade assintotica de tempo, ex. "O(E·√V)".
        complexity_space : complexidade assintotica de espaco, ex. "O(V + E)".
        kind             : um de TIPOS.
        language         : um de LINGUAGENS. Dirige a separacao das tabelas.
        fn               : funcao que resolve uma instancia, na interface padrao
                           do problema.
        source_url       : URL do repositorio de origem, para a rastreabilidade
                           exigida pelo AC-23. Vazio para reimplementacoes.
        notes            : ressalva a exibir junto do algoritmo, ex. a zona
                           cinzenta dos lacos Python sobre arrays NumPy.
        instrumented_fn  : variante instrumentada com contadores de operacoes.
                           Condicional (AC-14) e ainda pendente de decisao; o
                           tempo NUNCA e medido nesta variante, porque contar
                           distorce o que se quer medir.
    """

    key: str
    name: str
    complexity_time: str
    complexity_space: str
    kind: str
    language: str
    fn: Callable
    source_url: str = ""
    notes: str = ""
    instrumented_fn: Optional[Callable] = None

    def __post_init__(self):
        if self.kind not in TIPOS:
            raise ValueError(
                f"{self.key}: kind={self.kind!r} invalido; esperado um de {TIPOS}"
            )
        if self.language not in LINGUAGENS:
            raise ValueError(
                f"{self.key}: language={self.language!r} invalido; "
                f"esperado um de {LINGUAGENS}"
            )


def selecionar(specs, chaves):
    """
    Seleciona algoritmos por chave, na ordem em que as chaves forem pedidas.

    Levanta KeyError quando uma chave nao existe. Falhar alto e o objetivo:
    era exatamente o silencio da selecao por fatia posicional que permitia
    inserir um algoritmo e mudar a composicao de uma secao sem aviso.
    """
    por_chave = {s.key: s for s in specs}
    ausentes = [c for c in chaves if c not in por_chave]
    if ausentes:
        raise KeyError(
            f"chave(s) inexistente(s): {ausentes}. "
            f"Disponiveis: {sorted(por_chave)}"
        )
    return [por_chave[c] for c in chaves]


def por_linguagem(specs, linguagem):
    """Filtra os algoritmos de uma linguagem, preservando a ordem original."""
    return [s for s in specs if s.language == linguagem]
