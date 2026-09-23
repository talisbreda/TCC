"""
Saidas dos benchmarks (AC-15).

Do `ResultRecord` derivam tres formas, uma fonte de verdade so (decisao D4):

  1. **CSV de dados brutos** -- preserva tudo para reanalise e alimenta os
     graficos do `pgfplots`.
  2. **Tabelas LaTeX** -- prontas para `\\input` no documento. Nenhum numero e
     digitado a mao no LaTeX, que e o que o AC-22 exige.
  3. **Tabelas no terminal** -- acompanhamento durante a execucao.

Alem dessas, o modulo grava o **CSV canonico de qualidade**, no formato que
`verify.py` compara contra o baseline pre-migracao (AC-17).

Separacao das tabelas de tempo por linguagem (decisao D8): comparar tempo entre
Python interpretado e nucleo compilado mede a linguagem, nao o algoritmo. A
qualidade, ao contrario, e independente de linguagem -- por isso a tabela de
qualidade reune todos os algoritmos.
"""

import csv
import re
import unicodedata
from pathlib import Path

from .algorithms import PYTHON, C
from .result import OK

COLUNAS_CSV = (
    "problem", "algorithm", "algorithm_key", "kind", "language",
    "instance", "n", "seed", "complexity_time", "complexity_space", "runs",
    "time_median_ms", "time_samples_ms",
    "quality", "reference_optimum", "quality_ratio",
    "status", "detail",
)

# Colunas do CSV canonico de qualidade -- casam com `verify.ler_csv`.
COLUNAS_QUALIDADE = ("problema", "secao", "instancia", "algoritmo", "n", "qualidade")

_NOME_LINGUAGEM = {PYTHON: "Python", C: "compilado (C/C++)"}

# Alem dos caracteres reservados, inclui os que o LaTeX compoe como outro
# glifo em modo texto. O caso que motivou: os rotulos de instancia do projeto
# usam "|" como separador ("Grafo 1 — Esparso | SEM perfeito"), e sem escape
# ele sai como travessao -- ambiguo, ja que o rotulo tambem contem travessoes.
_ESCAPES_LATEX = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    "|": r"\textbar{}", "<": r"\textless{}", ">": r"\textgreater{}",
}


def escapar_latex(texto):
    """Escapa os caracteres com significado especial em LaTeX."""
    return "".join(_ESCAPES_LATEX.get(c, c) for c in str(texto))


def complexidade_latex(texto):
    """
    Converte a complexidade da forma legivel para modo matematico.

    Os benchmarks registram a complexidade como e exibida no terminal
    ("O(E·√V)"). O documento a escreve em modo matematico ("$O(E\\sqrt{V})$"),
    seguindo as tabelas comparativas ja existentes nos capitulos.

    Marcadores de nota de rodape (`*`, `†`) sao preservados FORA do modo
    matematico, onde nao seriam compostos corretamente.
    """
    if not texto:
        return ""

    corpo = str(texto)
    marcadores = ""
    while corpo and corpo[-1] in "*†‡":
        marcadores = corpo[-1] + marcadores
        corpo = corpo[:-1]

    corpo = corpo.replace("·", r" \cdot ")
    corpo = re.sub(r"√(\w+)", r"\\sqrt{\1}", corpo)
    for sobrescrito, digito in (("²", "2"), ("³", "3"), ("⁴", "4")):
        corpo = corpo.replace(sobrescrito, f"^{{{digito}}}")
    corpo = re.sub(r"\^(\w)(?!\})", r"^{\1}", corpo)

    return f"${corpo}${marcadores}"


def _identificador(texto):
    """Reduz um rotulo a um identificador utilizavel em nome de arquivo."""
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    sem_acento = sem_acento.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", sem_acento.lower())).strip("-")


def _celula_tempo(registro):
    """Conteudo da celula na tabela de tempo."""
    if registro.status != OK:
        return {"timeout": "—", "bug_conhecido": registro.detail or "erro",
                "erro": "erro"}.get(registro.status, "—")
    if registro.time_median_ms is None:
        return "—"
    return f"{registro.time_median_ms:.2f}"


def _celula_qualidade(registro):
    """Conteudo da celula na tabela de qualidade."""
    return registro.qualidade_para_verificacao() or "—"


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def gravar_csv(registros, caminho):
    """
    Grava o CSV de dados brutos.

    `time_samples_ms` e serializado separado por ponto e virgula, para caber
    numa celula sem conflitar com o separador do CSV. Os contadores de
    operacoes, quando houver (AC-14), viram colunas `ops_<chave>`.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    chaves_ops = sorted({k for r in registros for k in r.ops})
    colunas = list(COLUNAS_CSV) + [f"ops_{k}" for k in chaves_ops]

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(colunas)
        for r in registros:
            linha = [
                r.problem, r.algorithm, r.algorithm_key, r.kind, r.language,
                r.instance, r.n, "" if r.seed is None else r.seed,
                r.complexity_time, r.complexity_space, r.runs,
                "" if r.time_median_ms is None else f"{r.time_median_ms:.6f}",
                ";".join(f"{a:.6f}" for a in r.time_samples_ms),
                "" if r.quality is None else r.quality,
                "" if r.reference_optimum is None else r.reference_optimum,
                "" if r.quality_ratio is None else f"{r.quality_ratio:.6f}",
                r.status, r.detail,
            ]
            linha += [r.ops.get(k, "") for k in chaves_ops]
            escritor.writerow(linha)
    return caminho


def gravar_qualidade_canonica(registros, caminho):
    """
    Grava a qualidade no formato canonico comparado pelo `verify.py` (AC-17).

    A coluna `secao` fica vazia: o harness nao tem secoes, e a chave de
    comparacao a ignora de proposito -- ver `verify.ler_csv`.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(COLUNAS_QUALIDADE)
        for r in registros:
            escritor.writerow([r.problem, "", r.instance, r.algorithm, r.n,
                               r.qualidade_para_verificacao()])
    return caminho


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------

def _tabela_latex(registros, tamanhos, titulo, rotulo, coluna_fn, com_espaco):
    linhas = [
        r"\begin{table}[H]",
        r"    \centering",
        f"    \\caption{{{titulo}}}",
        f"    \\label{{{rotulo}}}",
        r"    \renewcommand{\arraystretch}{1.2}",
        r"    \footnotesize",
        r"    \adjustbox{max width=\textwidth}{%",
    ]

    n_colunas = "r" * len(tamanhos)
    cabecalho = ["\\textbf{Algoritmo}", "\\textbf{Tipo}", "\\textbf{Tempo}"]
    alinhamento = "l l l "
    if com_espaco:
        cabecalho.append("\\textbf{Espaço}")
        alinhamento += "l "
    cabecalho += [f"\\textbf{{$n={n}$}}" for n in tamanhos]

    linhas += [
        f"    \\begin{{tabular}}{{@{{}} {alinhamento}{n_colunas} @{{}}}}",
        r"        \toprule",
        "        " + " & ".join(cabecalho) + r" \\",
        r"        \midrule",
    ]

    por_algoritmo = {}
    for r in registros:
        por_algoritmo.setdefault(r.algorithm_key, []).append(r)

    for chave, grupo in por_algoritmo.items():
        primeiro = grupo[0]
        por_n = {r.n: r for r in grupo}
        celulas = [
            escapar_latex(primeiro.algorithm),
            escapar_latex(primeiro.kind),
            complexidade_latex(primeiro.complexity_time),
        ]
        if com_espaco:
            celulas.append(complexidade_latex(primeiro.complexity_space))
        celulas += [
            escapar_latex(coluna_fn(por_n[n])) if n in por_n else "—"
            for n in tamanhos
        ]
        linhas.append("        " + " & ".join(celulas) + r" \\")

    linhas += [r"        \bottomrule", r"    \end{tabular}%", r"    }", r"\end{table}", ""]
    return "\n".join(linhas)


def gravar_tabelas_latex(registros, diretorio, problema):
    """
    Emite as tabelas LaTeX, uma por arquivo, prontas para `\\input`.

    Por instancia sao gerados:
      - uma tabela de **tempo por linguagem** (D8), com as complexidades
        assintoticas de tempo e espaco ao lado do valor medido -- e o que o
        Prof. Maicon pediu na p. 7 do feedback de TCC I;
      - uma tabela de **qualidade** reunindo todos os algoritmos, ja que
        qualidade independe de linguagem.

    Retorna a lista de arquivos gerados.
    """
    diretorio = Path(diretorio)
    diretorio.mkdir(parents=True, exist_ok=True)
    gerados = []

    instancias = []
    for r in registros:
        if r.instance not in instancias:
            instancias.append(r.instance)

    for instancia in instancias:
        da_instancia = [r for r in registros if r.instance == instancia]
        tamanhos = sorted({r.n for r in da_instancia})
        id_inst = _identificador(instancia)[:40]

        for linguagem in (PYTHON, C):
            do_grupo = [r for r in da_instancia if r.language == linguagem]
            if not do_grupo:
                continue
            caminho = diretorio / f"{problema}-{id_inst}-tempo-{linguagem}.tex"
            caminho.write_text(_tabela_latex(
                do_grupo, tamanhos,
                titulo=(f"Tempo de execução em {_NOME_LINGUAGEM[linguagem]} — "
                        f"{escapar_latex(instancia)} (mediana, ms)"),
                rotulo=f"tab:{problema}-{id_inst}-tempo-{linguagem}",
                coluna_fn=_celula_tempo, com_espaco=True,
            ), encoding="utf-8")
            gerados.append(caminho)

        caminho = diretorio / f"{problema}-{id_inst}-qualidade.tex"
        caminho.write_text(_tabela_latex(
            da_instancia, tamanhos,
            titulo=f"Qualidade da solução — {escapar_latex(instancia)}",
            rotulo=f"tab:{problema}-{id_inst}-qualidade",
            coluna_fn=_celula_qualidade, com_espaco=False,
        ), encoding="utf-8")
        gerados.append(caminho)

    return gerados


# ---------------------------------------------------------------------------
# Terminal
# ---------------------------------------------------------------------------

def imprimir_tabelas(registros, problema):
    """Imprime o acompanhamento da execucao, agrupado como as tabelas emitidas."""
    instancias = []
    for r in registros:
        if r.instance not in instancias:
            instancias.append(r.instance)

    for instancia in instancias:
        da_instancia = [r for r in registros if r.instance == instancia]
        tamanhos = sorted({r.n for r in da_instancia})

        print(f"\n{'=' * 78}\n  {instancia}\n{'=' * 78}")

        for titulo, grupo, coluna_fn in (
            (f"Tempo em Python (mediana, ms)",
             [r for r in da_instancia if r.language == PYTHON], _celula_tempo),
            (f"Tempo compilado (C/C++) (mediana, ms)",
             [r for r in da_instancia if r.language == C], _celula_tempo),
            ("Qualidade da solução", da_instancia, _celula_qualidade),
        ):
            if not grupo:
                continue
            print(f"\n  {titulo}:\n")
            print(f"  {'Algoritmo':<30} {'Tipo':<11} {'Tempo':<12}"
                  + "".join(f"{'n=' + str(n):>12}" for n in tamanhos))
            print(f"  {'-' * 76}")

            por_algoritmo = {}
            for r in grupo:
                por_algoritmo.setdefault(r.algorithm_key, []).append(r)

            for _, itens in por_algoritmo.items():
                primeiro = itens[0]
                por_n = {r.n: r for r in itens}
                linha = (f"  {primeiro.algorithm:<30} {primeiro.kind:<11} "
                         f"{primeiro.complexity_time:<12}")
                for n in tamanhos:
                    celula = coluna_fn(por_n[n]) if n in por_n else "—"
                    linha += f"{celula:>12}"
                print(linha)
