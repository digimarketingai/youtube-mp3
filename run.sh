#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing dependencies..."
python3 -m pip install -q -U "yt-dlp[default]"

if ! command -v ffmpeg >/dev/null || \
   ! command -v curl >/dev/null || \
   ! command -v unzip >/dev/null; then
    apt-get update -qq
    apt-get install -y -qq ffmpeg curl unzip
fi

export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"

if ! command -v deno >/dev/null; then
    curl -fsSL https://deno.land/install.sh | sh -s -- -y
fi

python3 "$ROOT/clip.py" "$@"
