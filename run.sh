#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PYTHONUNBUFFERED=1
export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"

echo "Installing system dependencies..."

if ! command -v ffmpeg >/dev/null 2>&1 || \
   ! command -v curl >/dev/null 2>&1 || \
   ! command -v unzip >/dev/null 2>&1; then
    apt-get update -qq
    apt-get install -y -qq ffmpeg curl unzip
fi

echo "Installing Python dependencies..."
python3 -m pip install --quiet --upgrade -r requirements.txt

if ! command -v deno >/dev/null 2>&1; then
    echo "Installing Deno..."
    curl -fsSL https://deno.land/install.sh | sh -s -- -y
fi

echo "Starting Gradio..."
exec python3 app.py "$@"
