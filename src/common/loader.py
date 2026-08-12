"""
Carregamento de wrappers por caminho de arquivo.

Os diretorios do projeto contem hifens (`src/mcm/hopcroft-karp/`, `src/stable-
marriage/`), o que impede o `import` normal do Python. Por isso os wrappers sao
carregados por caminho, via `importlib`.

Ate aqui cada benchmark trazia sua propria copia deste helper, com o calculo da
raiz do projeto repetido. Este modulo unifica as tres copias (decisao D1).
"""

import importlib.util
from pathlib import Path

# src/common/loader.py -> src/common -> src -> raiz do projeto
RAIZ = Path(__file__).resolve().parent.parent.parent


def carregar(caminho_relativo, nome_modulo=None):
    """
    Carrega um modulo Python a partir de um caminho relativo a raiz do projeto.

    Parametros:
        caminho_relativo : str ou Path, ex. "src/mcm/hopcroft-karp/x.py"
        nome_modulo      : nome interno do modulo. Se omitido, usa o nome do
                           arquivo sem extensao.

    Retorno:
        O modulo carregado.

    Levanta FileNotFoundError com o caminho absoluto quando o arquivo nao
    existe -- mais util que o ImportError generico do importlib, ja que o erro
    tipico aqui e um caminho errado, nao um modulo ausente.
    """
    caminho = RAIZ / caminho_relativo
    if not caminho.is_file():
        raise FileNotFoundError(f"wrapper nao encontrado: {caminho}")

    nome = nome_modulo or caminho.stem
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def carregar_funcao(caminho_relativo, nome_funcao, nome_modulo=None):
    """
    Carrega um modulo e devolve uma de suas funcoes.

    Atalho para o caso comum: cada wrapper do projeto expoe exatamente uma
    funcao publica.
    """
    modulo = carregar(caminho_relativo, nome_modulo)
    try:
        return getattr(modulo, nome_funcao)
    except AttributeError:
        raise AttributeError(
            f"{caminho_relativo} nao define a funcao '{nome_funcao}'"
        ) from None
