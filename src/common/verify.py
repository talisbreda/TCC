"""
Verificacao de nao-regressao dos benchmarks (AC-17).

Extrai das saidas dos benchmarks o conjunto canonico de registros de qualidade

    (problema, secao, instancia, algoritmo, n) -> qualidade

e grava um CSV independente de layout. Esse CSV e o artefato de referencia do
AC-17: apos a migracao para o harness compartilhado, a qualidade produzida pelos
benchmarks deve ser identica a registrada aqui.

Por que nao comparar o texto diretamente (decisao D10 da spec tecnica):
a migracao muda o layout de proposito -- tabelas separadas por linguagem, coluna
de complexidade de espaco, emissao de CSV. Um diff literal acusaria diferenca em
toda linha sem dizer nada sobre regressao. A comparacao precisa ser semantica.

As colunas sao fatiadas por POSICAO derivada do cabecalho, e nao por divisao em
espacos em branco, porque celulas como "0 =ref" (casamento estavel) contem
espaco interno.

Uso:
    # gera o baseline canonico a partir das saidas em texto
    python src/common/verify.py extrair results/baseline/mcm.txt mcm

    # compara dois baselines canonicos (antes x depois da migracao)
    python src/common/verify.py comparar antes.csv depois.csv
"""

import csv
import re
import sys
from pathlib import Path

# Linhas que iniciam uma tabela de qualidade, uma por problema.
_MARCADORES_QUALIDADE = (
    "MCM encontrado por algoritmo",       # mcm
    "Custo encontrado por algoritmo",     # assignment
    "Pares bloqueantes",                  # stable-marriage
)

_ROTULO_TAMANHO = re.compile(r"n=\d+")

CAMPOS = ("problema", "secao", "instancia", "algoritmo", "n", "qualidade")


def _colunas(cabecalho):
    """
    Deriva a geometria das colunas de tamanho a partir do cabecalho.

    Os rotulos "n=NNN" sao impressos alinhados a direita numa largura fixa, de
    modo que o fim do rotulo coincide com o fim da coluna. Retorna os rotulos,
    as posicoes finais e a largura da coluna.
    """
    achados = list(_ROTULO_TAMANHO.finditer(cabecalho))
    if not achados:
        return [], [], 0

    rotulos = [int(m.group()[2:]) for m in achados]
    fins = [m.end() for m in achados]
    largura = fins[1] - fins[0] if len(fins) > 1 else fins[0]
    return rotulos, fins, largura


def _ler_tabela(linhas, inicio, problema, secao, instancia):
    """
    Le a tabela de qualidade que comeca na linha marcadora `inicio`.

    Retorna (indice_da_proxima_linha, registros).
    """
    i = inicio + 1
    while i < len(linhas) and "n=" not in linhas[i]:
        i += 1
    if i >= len(linhas):
        return inicio + 1, []

    rotulos, fins, largura = _colunas(linhas[i])
    if not rotulos:
        return i + 1, []

    i += 1
    if i < len(linhas) and set(linhas[i].strip()) == {"-"}:
        i += 1

    registros = []
    while i < len(linhas) and linhas[i].strip():
        linha = linhas[i]
        prefixo = linha[: fins[0] - largura]
        # O prefixo traz nome, complexidade e tipo separados por 2+ espacos;
        # o nome do algoritmo pode conter espacos simples.
        partes = re.split(r"\s{2,}", prefixo.strip())
        algoritmo = partes[0] if partes else ""

        for n, fim in zip(rotulos, fins):
            qualidade = linha[fim - largura:fim].strip()
            registros.append((problema, secao, instancia, algoritmo, n, qualidade))
        i += 1

    return i, registros


def extrair(caminho, problema):
    """Extrai todos os registros de qualidade de uma saida de benchmark."""
    linhas = Path(caminho).read_text(encoding="utf-8").splitlines()
    registros = []
    secao = ""
    instancia = ""

    i = 0
    while i < len(linhas):
        linha = linhas[i]
        despida = linha.strip()

        if "SEÇÃO" in linha:
            secao = despida
            i += 1
            continue

        # Separador de instancia: linha de "=", nome, linha de "=".
        # O nome precisa ser nao-vazio: o banner do topo do benchmark tambem
        # produz duas linhas de "=" separadas por uma linha em branco.
        if despida and set(despida) == {"="}:
            if (i + 2 < len(linhas)
                    and linhas[i + 1].strip()
                    and set(linhas[i + 2].strip()) == {"="}):
                instancia = linhas[i + 1].strip()
                i += 3
                continue

        if any(m in linha for m in _MARCADORES_QUALIDADE):
            i, novos = _ler_tabela(linhas, i, problema, secao, instancia)
            registros.extend(novos)
            continue

        i += 1

    return registros


def gravar_csv(registros, caminho):
    # lineterminator="\n": o padrao do csv e "\r\n", que sujaria o diff destes
    # arquivos versionados.
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(CAMPOS)
        escritor.writerows(registros)


def ler_csv(caminho):
    """Le um baseline canonico como dicionario chave -> qualidade."""
    with open(caminho, newline="", encoding="utf-8") as f:
        return {
            (l["problema"], l["secao"], l["instancia"], l["algoritmo"], l["n"]): l["qualidade"]
            for l in csv.DictReader(f)
        }


def comparar(caminho_antes, caminho_depois):
    """
    Compara dois baselines canonicos. Retorna a lista de divergencias; lista
    vazia significa ausencia de regressao.
    """
    antes = ler_csv(caminho_antes)
    depois = ler_csv(caminho_depois)

    divergencias = []
    for chave in sorted(set(antes) | set(depois)):
        a = antes.get(chave)
        d = depois.get(chave)
        if a != d:
            divergencias.append((chave, a, d))
    return divergencias


def main(argv):
    if len(argv) >= 4 and argv[1] == "extrair":
        entrada, problema = argv[2], argv[3]
        registros = extrair(entrada, problema)
        saida = Path(entrada).with_name(f"{problema}-qualidade.csv")
        gravar_csv(registros, saida)
        print(f"{len(registros)} registros de qualidade -> {saida}")
        return 0

    if len(argv) >= 4 and argv[1] == "comparar":
        divergencias = comparar(argv[2], argv[3])
        if not divergencias:
            print("Sem regressao: as qualidades sao identicas.")
            return 0
        print(f"REGRESSAO: {len(divergencias)} divergencia(s).")
        for chave, a, d in divergencias:
            print(f"  {chave}: antes={a!r} depois={d!r}")
        return 1

    print(__doc__.strip().splitlines()[-4].strip())
    print("Uso: verify.py extrair <saida.txt> <problema>")
    print("     verify.py comparar <antes.csv> <depois.csv>")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
