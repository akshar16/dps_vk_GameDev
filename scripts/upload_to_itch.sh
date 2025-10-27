#!/usr/bin/env bash
set -euo pipefail

# Interactive itch.io upload script
# This will guide you through uploading your game builds

echo "==================================="
echo "Itch.io Upload Helper"
echo "==================================="
echo ""

# Check if builds exist
if [ ! -f "builds/isdps_vk_GameDev-macos.zip" ]; then
  echo "❌ Error: builds/isdps_vk_GameDev-macos.zip not found"
  echo "Run: bash scripts/build_macos.sh"
  exit 1
fi

if [ ! -f "builds/isdps_vk_GameDev-web.zip" ]; then
  echo "❌ Error: builds/isdps_vk_GameDev-web.zip not found"
  echo "Run: bash scripts/build_web.sh"
  exit 1
fi

echo "✅ Found macOS build: $(du -h builds/isdps_vk_GameDev-macos.zip | cut -f1)"
echo "✅ Found web build: $(du -h builds/isdps_vk_GameDev-web.zip | cut -f1)"
echo ""

# Get itch.io target
echo "Enter your itch.io game target (format: username/game-slug)"
echo "Example: akshar16/survivor-game"
read -p "Target: " ITCH_TARGET

if [ -z "$ITCH_TARGET" ]; then
  echo "❌ No target provided. Exiting."
  exit 1
fi

# Confirm
echo ""
echo "Ready to upload to: $ITCH_TARGET"
echo ""
echo "This will push:"
echo "  - Web (HTML5) build → ${ITCH_TARGET}:html5"
echo "  - macOS build → ${ITCH_TARGET}:mac"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Upload cancelled."
  exit 0
fi

echo ""
echo "🚀 Uploading web build..."
butler push builds/isdps_vk_GameDev-web.zip "$ITCH_TARGET:html5"

echo ""
echo "🚀 Uploading macOS build..."
butler push builds/isdps_vk_GameDev-macos.zip "$ITCH_TARGET:mac"

echo ""
echo "✅ Upload complete!"
echo ""
echo "Visit your game page: https://itch.io/dashboard/game/$(echo $ITCH_TARGET | cut -d'/' -f2)"
echo ""
echo "Remember to:"
echo "  1. Set your game to 'Published' in the dashboard"
echo "  2. Add screenshots and cover image"
echo "  3. Write a description"
echo "  4. Set the HTML5 viewport to 1280x720"
