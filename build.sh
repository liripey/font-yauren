#!/usr/bin/env bash
# Gera os 7 pesos (OTF + WOFF2), espécimes e métricas de QA.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
(cd source && python3 -m yauren.build "$@")
python3 tools/specimen.py
python3 tools/qa_report.py > docs/metricas.md
echo "Pronto: fonts/otf, fonts/webfonts, docs/img, docs/metricas.md"
