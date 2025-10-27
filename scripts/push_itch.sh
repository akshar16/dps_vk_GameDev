#!/usr/bin/env bash
set -euo pipefail
# Push local builds to itch.io via butler.
# Usage: ./scripts/push_itch.sh user/game

if ! command -v butler >/dev/null 2>&1; then
  echo "butler not found. Install with: brew install itch-tools/tap/butler"
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 user/game"
  exit 1
fi

TARGET="$1"
ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$ROOT_DIR"

if [ ! -f builds/isdps_vk_GameDev-macos.zip ]; then
  echo "Missing builds/isdps_vk_GameDev-macos.zip. Build it first (scripts/build_macos.sh)."
else
  butler push builds/isdps_vk_GameDev-macos.zip "$TARGET:mac"
fi

if [ ! -f builds/isdps_vk_GameDev-web.zip ]; then
  echo "Missing builds/isdps_vk_GameDev-web.zip. Build it first (scripts/build_web.sh)."
else
  butler push builds/isdps_vk_GameDev-web.zip "$TARGET:html5"
fi
