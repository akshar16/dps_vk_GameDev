#!/usr/bin/env bash
set -euo pipefail
# Build a macOS .app bundle using PyInstaller and zip it for itch.io.

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$ROOT_DIR"

APP_NAME="dps_saket-macos"

# Clean previous build
rm -rf build dist "$APP_NAME.spec" || true

/usr/local/bin/python3 -m PyInstaller \
  --noconfirm --windowed --onedir \
  --name "$APP_NAME" start_screen.py \
  --add-data "stage 1:stage 1" \
  --add-data "stage 2:stage 2" \
  --add-data "fonts:fonts" \
  --add-data "hearts:hearts"

mkdir -p builds
cd dist
zip -r ../builds/${APP_NAME}.zip ${APP_NAME}.app

echo "macOS build complete: $ROOT_DIR/builds/${APP_NAME}.zip"
