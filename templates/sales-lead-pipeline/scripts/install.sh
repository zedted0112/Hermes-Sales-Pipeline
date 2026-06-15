#!/usr/bin/env bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$HERMES_HOME/skills" "$HERMES_HOME/skill-bundles"

echo "Installing sales-lead-pipeline skills → $HERMES_HOME/skills/"
for skill_dir in "$ROOT/skills"/*; do
  name="$(basename "$skill_dir")"
  rm -rf "$HERMES_HOME/skills/$name"
  cp -R "$skill_dir" "$HERMES_HOME/skills/"
  echo "  ✓ $name"
done

cp "$ROOT/skill-bundles/sales-pipeline.yaml" "$HERMES_HOME/skill-bundles/"
echo "  ✓ skill-bundles/sales-pipeline.yaml"

mkdir -p "$HERMES_HOME/leads/research" "$HERMES_HOME/leads/demos" "$HERMES_HOME/leads/drafts"
echo ""
echo "Done. In Hermes chat run: /reload-skills"
echo "Optional: hermes skills install skills-sh/connorads/dotfiles/web-animation-design --yes"
