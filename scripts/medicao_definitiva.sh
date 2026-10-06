#!/usr/bin/env bash
# Rodada definitiva de medição dos benchmarks.
# Gera os números que vão para o capítulo de Resultados.
#
# ANTES de rodar (uma vez, precisa de sudo):
#     sudo cpupower frequency-set -g performance
# DEPOIS (para restaurar):
#     sudo cpupower frequency-set -g powersave
#
# Uso:  bash scripts/medicao_definitiva.sh
set -u

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"
PY="$RAIZ/.venv/bin/python"
CORE=3                     # P-core dedicado (0-3 são P-cores; 0 fica p/ o SO)
export PYTHONHASHSEED=0    # reprodutibilidade (fixa o não-determinismo do benchaplin)

echo "======================================================================"
echo "  RODADA DEFINITIVA DE MEDIÇÃO"
echo "======================================================================"

# --- Checagem das condições ideais ---
avisos=0
gov=$(cat /sys/devices/system/cpu/cpu${CORE}/cpufreq/scaling_governor 2>/dev/null)
if [ "$gov" != "performance" ]; then
    echo "  [AVISO] governador = '$gov' (ideal: performance)."
    echo "          rode: sudo cpupower frequency-set -g performance"
    avisos=$((avisos+1))
else
    echo "  [ok] governador: performance"
fi

if [ "$(cat /sys/class/power_supply/AC*/online 2>/dev/null | head -1)" != "1" ]; then
    echo "  [AVISO] na bateria — conecte à tomada."; avisos=$((avisos+1))
else
    echo "  [ok] na tomada"
fi

pesados=$(ps -eo pcpu,comm --sort=-pcpu --no-headers | awk '$1>10 && $2!~/python|ps|awk/ {print $2}' | head -3 | paste -sd, -)
if [ -n "$pesados" ]; then
    echo "  [AVISO] processos pesados ativos: $pesados (feche para reduzir ruído)"; avisos=$((avisos+1))
else
    echo "  [ok] sem processos pesados competindo"
fi

echo "  núcleo fixado: CPU $CORE (P-core) | PYTHONHASHSEED=$PYTHONHASHSEED"
echo "----------------------------------------------------------------------"
if [ "$avisos" -gt 0 ]; then
    echo "  $avisos aviso(s). Continuando em 8s (Ctrl-C para abortar e ajustar)..."
    sleep 8
fi

# --- Execução: cada benchmark no core fixo, com hash seed fixo ---
run() {
    local nome="$1"; local script="$2"
    echo
    echo ">>> $nome  ($(date +%H:%M:%S))"
    local t0=$(date +%s)
    taskset -c "$CORE" "$PY" -u "$script"
    local rc=$?
    local dt=$(( $(date +%s) - t0 ))
    echo ">>> $nome terminou em ${dt}s (exit=$rc)"
}

run "MCM bipartido"        src/mcm/mcm_benchmark.py
run "Casamento estável"    src/stable-marriage/stable_marriage_benchmark.py
run "Atribuição gargalo"   src/bottleneck/bottleneck_benchmark.py
run "Grafos gerais"        src/general/general_benchmark.py
run "MIM"                  src/mim/mim_benchmark.py
run "Atribuição linear"    src/assignment/assignment_benchmark.py   # o mais lento (benchaplin)

echo
echo "======================================================================"
echo "  CONCLUÍDO. Resultados regenerados em results/ (CSV) e results/tex/."
echo "  Não esqueça de restaurar:  sudo cpupower frequency-set -g powersave"
echo "======================================================================"
