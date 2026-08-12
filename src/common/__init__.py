"""
Infraestrutura compartilhada pelos benchmarks.

Os benchmarks de cada problema reimplementavam o mesmo esqueleto -- carregamento
de wrappers, laco de cronometragem, formatacao de tabela e tratamento de erro
por celula -- em copias que ja haviam divergido entre si. Este pacote centraliza
essa infraestrutura (decisao D1 da spec tecnica).

Os wrappers em `src/` seguem sem saber que este pacote existe: ele se insere
entre eles e os benchmarks, sem alterar a arquitetura de tres camadas.
"""
