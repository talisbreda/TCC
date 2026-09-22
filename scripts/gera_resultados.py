"""
Gera artefatos do capítulo de Resultados a partir dos CSVs dos benchmarks:
  - results/tex/exp-<prob>.tex   : tabela expoente previsto x medido (AC-12)
  - results/plot/<prob>.csv      : dados tidy (n + tempo por algoritmo) p/ pgfplots
Tudo derivado dos dados medidos; nenhum número é digitado à mão (AC-22).
"""
import csv, re, unicodedata
from pathlib import Path
from collections import defaultdict

RAIZ = Path(__file__).resolve().parent.parent
TEX = RAIZ / "results" / "tex"
PLOT = RAIZ / "results" / "plot"
PLOT.mkdir(exist_ok=True)

# instância representativa por problema (para tabela de expoente e gráfico)
REPRESENTATIVA = {
    "mcm": "Grafo 3 — Denso   | COM perfeito | MCM = n",
    "assignment": "Matriz 1 — Densa uniforme  | custo in [1,100]",
    "bottleneck": "Matriz 1 — Densa uniforme  | custo in [1,100]",
    "stable-marriage": "Perfil 1 — Aleatório       | permutações uniformes",
    "general-weight": "Peso — esparso (grau ~3)",
    "mim-grande": "Grafo esparso (grau ~3)",
}

def esc(s):
    for a,b in [("\\","\\textbackslash{}"),("&","\\&"),("%","\\%"),("_","\\_"),
                ("#","\\#"),("·"," \\cdot "),("√","\\sqrt"),("²","^{2}"),("³","^{3}")]:
        s=s.replace(a,b)
    return s

def compl_math(s):
    s=s.replace("·",r" \cdot ").replace("²","^{2}").replace("³","^{3}").replace("⁴","^{4}")
    s=re.sub(r"√(\w+)", r"\\sqrt{\1}", s)
    s=re.sub(r"\^(\w)(?!\})", r"^{\1}", s)
    return f"${s}$" if s else ""

def key(s):
    s=unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode()
    return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")[:40]

def carrega(prob):
    base = prob.split("-")[0] if prob.startswith("general") or prob.startswith("mim") else prob
    arq = {"mcm":"mcm","assignment":"assignment","bottleneck":"bottleneck",
           "stable-marriage":"stable-marriage","general-weight":"general",
           "mim-grande":"mim"}[prob]
    dados=list(csv.DictReader(open(RAIZ/f"results/{arq}.csv",encoding="utf-8")))
    cres=list(csv.DictReader(open(RAIZ/f"results/{arq}-crescimento.csv",encoding="utf-8")))
    pfil = prob if prob in ("general-weight","mim-grande") else None
    if pfil:
        dados=[r for r in dados if r["problem"]==pfil]
        cres=[r for r in cres if r["problem"]==pfil]
    return dados, cres

def tabela_exp(prob, inst):
    _, cres = carrega(prob)
    linhas=[r for r in cres if r["instance"]==inst and r["expoente_empirico"]]
    if not linhas: return None
    out=[r"\begin{table}[H]", r"    \centering",
         f"    \\caption{{Expoente empírico de crescimento --- {esc(inst)}}}",
         f"    \\label{{tab:exp-{key(prob)}}}",
         r"    \renewcommand{\arraystretch}{1.25}", r"    \footnotesize",
         r"    \begin{tabularx}{\textwidth}{@{} X l c c @{}}",
         r"        \toprule",
         r"        \textbf{Algoritmo} & \textbf{Compl.\ teórica} & \textbf{Expoente medido} & \textbf{$R^2$} \\",
         r"        \midrule"]
    for r in linhas:
        out.append(f"        {esc(r['algorithm'])} & {compl_math(r['complexity_time'])} & "
                   f"{float(r['expoente_empirico']):.2f} & {float(r['r2']):.3f} \\\\")
    out += [r"        \bottomrule", r"    \end{tabularx}", r"\end{table}", ""]
    (TEX/f"exp-{key(prob)}.tex").write_text("\n".join(out),encoding="utf-8")
    return f"exp-{key(prob)}.tex"

def plot_csv(prob, inst):
    """Um arquivo por série (n, t), só com os pontos medidos -- evita células
    vazias que quebrariam o pgfplots."""
    dados,_=carrega(prob)
    pontos=defaultdict(list); nomes={}
    for r in dados:
        if r["instance"]!=inst or r["status"]!="ok" or not r["time_median_ms"]: continue
        pontos[r["algorithm_key"]].append((int(r["n"]), float(r["time_median_ms"])))
        nomes[r["algorithm_key"]]=r["algorithm"]
    for k,pts in pontos.items():
        with open(PLOT/f"{key(prob)}-{k}.csv","w",newline="") as f:
            w=csv.writer(f); w.writerow(["n","t"])
            for n,t in sorted(pts): w.writerow([n,f"{t:.4f}"])
    return list(pontos), nomes

if __name__=="__main__":
    for prob,inst in REPRESENTATIVA.items():
        t=tabela_exp(prob,inst)
        algs,nomes=plot_csv(prob,inst)
        print(f"{prob}: {t} | {len(algs)} séries")
