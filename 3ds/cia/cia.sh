#!/bin/bash
# Packs PizzaMagna.cia from the parts build.sh left in build-3ds/cia-parts (the program, the RomFS with the game, the
# HOME Menu icon and banner), with makerom from 3DSGuy/Project_CTR's releases. Runs on the GitHub runner itself
# (.github/workflows/3ds.yml): makerom's Linux build needs a newer glibc than the devkitPro container has.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=${OUT:-$ROOT/build-3ds}
P=$OUT/cia-parts
W=$(mktemp -d)
UNIQUE_ID=0xF8A57          # homebrew range; the title ID becomes 000400000F8A5700
PRODUCT_CODE=CTR-H-PZMG
# makerom: the newest Linux build among Project_CTR's recent releases (it releases makerom and ctrtool apart)
MR=$(curl -fsSL ${GITHUB_TOKEN:+-H "Authorization: Bearer $GITHUB_TOKEN"} "https://api.github.com/repos/3DSGuy/Project_CTR/releases?per_page=30" \
  | grep -o '"browser_download_url": *"[^"]*"' | cut -d'"' -f4 | grep -E 'makerom.*(ubuntu|linux).*x86_64.*\.zip$' | head -1)
echo "makerom: $MR"
curl -fsSL -o "$W/makerom.zip" "$MR" && (cd "$W" && unzip -oq makerom.zip)
MAKEROM=$(find "$W" -type f -name makerom | head -1); chmod +x "$MAKEROM"
"$MAKEROM" -f cia -o "$OUT/PizzaMagna.cia" -target t -exefslogo -elf "$P/lovepotion.elf" -rsf "$ROOT/3ds/cia/app.rsf" \
  -icon "$P/icon.icn" -banner "$P/banner.bnr" \
  -DAPP_TITLE="PizzaMagna" -DAPP_PRODUCT_CODE="$PRODUCT_CODE" -DAPP_UNIQUE_ID="$UNIQUE_ID" -DAPP_ROMFS="$P/romfs" \
  -DAPP_CATEGORY=Application -DAPP_USE_ON_SD=true -DAPP_ENCRYPTED=false -DAPP_MEMORY_TYPE=Application \
  -DAPP_SYSTEM_MODE=64MB -DAPP_SYSTEM_MODE_EXT=124MB -DAPP_CPU_SPEED=804MHz -DAPP_ENABLE_L2_CACHE=true -DAPP_VERSION_MAJOR=1
ls -la "$OUT/PizzaMagna.cia"
