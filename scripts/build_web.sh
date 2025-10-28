#!/usr/bin/env bash
set -euo pipefail
# Build a web (HTML5) version of the game using pygbag.
# Output will be in dist/web and zipped to builds/isdps_vk_GameDev-web.zip.

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$ROOT_DIR"

# Clean previous dist
rm -rf build dist || true

# Build with pygbag (packs start_screen.py and assets)
pygbag --build start_screen.py

# Create builds folder at repo root (absolute path)
mkdir -p "$ROOT_DIR/builds"

# Find the web output directory created by pygbag
if [ -d "build/web" ]; then
  WEB_OUT="build/web"
elif [ -d "dist/web" ]; then
  WEB_OUT="dist/web"
else
  # Fallback: pygbag writes to build/ by default in recent versions
  WEB_OUT="build/web"
fi

# Zip the web folder for itch.io upload (as HTML5)
# Important: zip the CONTENTS of the web folder so index.html is at the ZIP root
ZIP_PATH="$ROOT_DIR/builds/isdps_vk_GameDev-web.zip"
cd "$WEB_OUT"
zip -r "$ZIP_PATH" .

echo "Web build complete: $ROOT_DIR/builds/isdps_vk_GameDev-web.zip"
