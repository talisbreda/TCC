#!/usr/bin/env bash
# Recompila o PDF da monografia: pdflatex -> bibtex -> pdflatex x2.
# Uso: bash scripts/build_pdf.sh
cd "$(dirname "$0")/.." || exit 1

pdflatex -interaction=nonstopmode main.tex > /dev/null
bibtex main > /dev/null   # avisos do estilo ABNT (abntex2-alf.bst) sao esperados
pdflatex -interaction=nonstopmode main.tex > /dev/null
pdflatex -interaction=nonstopmode main.tex > /dev/null

# Em caso de erro, mantem o main.log para inspecao
if grep -aq "^! " main.log; then
    echo "ERRO na compilacao (detalhes em main.log):"
    grep -a -A2 "^! " main.log | head -20
    exit 1
fi

echo "main.pdf gerado: $(pdfinfo main.pdf 2>/dev/null | awk '/Pages/{print $2}') paginas"
indef=$(grep -aE -c "(Reference|Citation) .* undefined" main.log)
if [ "$indef" -gt 0 ]; then
    echo "aviso: $indef referencia(s)/citacao(oes) indefinida(s):"
    grep -aoE "(Reference|Citation) \`[^']+' on page [0-9]+" main.log | sort -u
fi

rm -f main.aux main.log main.toc main.out main.bbl main.blg main.lof main.lot
