#!/usr/bin/env bash
# Hermes agent: run this script to build a demo — do not write HTML in chat.
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:?Usage: build.sh <slug> [template]}"
TEMPLATE="${2:-}"

if [ -n "$TEMPLATE" ]; then
  OUT="$(python3 "$SKILL_DIR/scripts/build_demo.py" "$SLUG" --template "$TEMPLATE")"
else
  OUT="$(python3 "$SKILL_DIR/scripts/build_demo.py" "$SLUG")"
fi
echo "$OUT"
OK="$(echo "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok', False))")"
if [[ "$OK" != "True" ]]; then
  echo "build_demo.py did not return ok:true" >&2
  exit 1
fi
DEMO_PATH="$(echo "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin)['demo_path'])")"
if [[ ! -f "$DEMO_PATH" ]]; then
  echo "Missing demo file: $DEMO_PATH" >&2
  exit 1
fi
echo "SUCCESS: open $DEMO_PATH"
