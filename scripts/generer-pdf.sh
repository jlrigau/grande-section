#!/usr/bin/env bash
# Génère tous les PDF du site dans <dossier-site>/pdf/ :
#  - un PDF par document et par zone de vacances (A, B, C), via la vue imprimer.html
#  - un PDF de fiches élève par période
# Usage : scripts/generer-pdf.sh <dossier-site-assemblé>
# Variables : CHROME_BIN (défaut : google-chrome), PORT (défaut : 8931)
set -euo pipefail

SITE_DIR=${1:?"dossier du site assemblé requis"}
CHROME_BIN=${CHROME_BIN:-google-chrome}
PORT=${PORT:-8931}
OUT="$SITE_DIR/pdf"

python3 -m http.server "$PORT" --directory "$SITE_DIR" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1

imprime() { # imprime <url> <fichier-pdf>
  "$CHROME_BIN" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --no-pdf-header-footer --virtual-time-budget=10000 \
    --print-to-pdf="$2" "$1" 2>/dev/null
  [ -s "$2" ] || { echo "ÉCHEC : $2" >&2; exit 1; }
}

DOCS="projet-annuel programmation langage maths eps arts temps-espace monde evar eval-guide eval-p1 eval-p2 eval-p3 eval-p4 eval-p5"
for Z in A B C; do
  mkdir -p "$OUT/zone-$Z"
  for D in $DOCS; do
    imprime "http://127.0.0.1:$PORT/imprimer.html?doc=$D&zone=$Z" "$OUT/zone-$Z/$D.pdf"
  done
  echo "Zone $Z : $(ls "$OUT/zone-$Z" | wc -l) PDF"
done

for N in 1 2 3 4 5; do
  imprime "http://127.0.0.1:$PORT/fiches/periode-$N.html" "$OUT/fiches-eleve-periode-$N.pdf"
  imprime "http://127.0.0.1:$PORT/fiches/entrainement-periode-$N.html" "$OUT/fiches-entrainement-periode-$N.pdf"
done
echo "Fiches élève : 5 PDF évaluation + 5 PDF entraînement"
echo "Total : $(find "$OUT" -name '*.pdf' | wc -l) PDF générés dans $OUT"
