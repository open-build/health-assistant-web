#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
REVISION="$(python3 -c 'import json; print(json.load(open("forgeweb.json"))["revision"])')"
if [ ! -d ForgeWeb/.git ]; then
  git clone https://github.com/Buildly-Marketplace/ForgeWeb.git ForgeWeb
  git -C ForgeWeb checkout "$REVISION"
else
  CURRENT="$(git -C ForgeWeb rev-parse HEAD)"
  if [ "$CURRENT" != "$REVISION" ]; then
    echo "ForgeWeb revision differs from forgeweb.json; review it before proceeding." >&2
    exit 1
  fi
fi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/manage.py --initialize-only
printf '\nReady: .venv/bin/python scripts/manage.py\n'
