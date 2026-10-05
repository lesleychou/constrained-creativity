#!/bin/bash
set -euo pipefail

PORT=8123

cd "$(dirname "$0")"

bundle exec jekyll build --watch &
WATCHER=$!
trap 'kill $WATCHER 2>/dev/null' EXIT

for _ in $(seq 60); do
    [ -f _site/index.html ] && break
    sleep 0.2
done

[ -f _site/index.html ] || { echo "build produced no _site/index.html" >&2; exit 1; }

python3 -m http.server "${1:-$PORT}" --directory _site
