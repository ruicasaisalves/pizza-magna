#!/bin/bash
# Builds the 3DS port as PizzaMagna.3dsx (Homebrew Launcher) and PizzaMagna.cia (installed to the HOME Menu,
# e.g. with FBI's Remote Install > Scan QR Code). Runs in the devkitpro/devkitarm container (.github/workflows/3ds.yml).
#
# LÖVE Potion is built from source with one patch (lovepotion-cia.patch): installed as a .cia it has no program file
# to read the game from, so it reads it from romfs:/game.love. The game goes into both files as a zip of 3ds/game:
# glued to the end of the .3dsx (as LÖVE Potion's own fused builds do) and as game.love in the .cia's RomFS.
# makerom and bannertool come from their GitHub releases.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
CIA=$ROOT/3ds/cia
OUT=${OUT:-$ROOT/build-3ds}
W=$OUT/work
LOVEPOTION_TAG=3.0.2
TITLE="Pizza Magna"
DESC="Pizzeria tycoon in 90s pixel art"
AUTHOR="Pizza Magna"
UNIQUE_ID=0xF8A57          # homebrew range; the title ID becomes 000400000F8A5700
PRODUCT_CODE=CTR-H-PZMG
mkdir -p "$W" "$OUT"

# tools: makerom (Project_CTR) and bannertool, the Linux builds from their latest releases
asset() {   # the newest asset matching $2 among the repo's recent releases (Project_CTR releases makerom and ctrtool apart)
  local all url
  all=$(curl -fsSL ${GITHUB_TOKEN:+-H "Authorization: Bearer $GITHUB_TOKEN"} "https://api.github.com/repos/$1/releases?per_page=30" \
    | grep -o '"browser_download_url": *"[^"]*"' | cut -d'"' -f4)
  url=$(echo "$all" | grep -E "$2" | head -1)
  if [ -z "$url" ]; then echo "no asset matching $2 in $1; found:" >&2; echo "$all" | head -40 >&2; return 1; fi
  echo "$url"; }
mkdir -p "$W/bin"
MR=$(asset 3DSGuy/Project_CTR 'makerom.*(ubuntu|linux).*x86_64.*\.zip$'); echo "makerom: $MR"; curl -fsSL -o "$W/makerom.zip" "$MR"
BT=$(asset Steveice10/bannertool 'bannertool\.zip$'); echo "bannertool: $BT"; curl -fsSL -o "$W/bannertool.zip" "$BT"
(cd "$W/bin" && unzip -oq ../makerom.zip && unzip -oq ../bannertool.zip)
MAKEROM=$(find "$W/bin" -type f -name makerom | head -1)
BANNERTOOL=$(find "$W/bin" -type f -path '*linux-x86_64*' -name bannertool | head -1)
chmod +x "$MAKEROM" "$BANNERTOOL"

# LÖVE Potion, patched
rm -rf "$W/lovepotion" "$W/lp-build"
git clone -q --depth 1 --branch "$LOVEPOTION_TAG" https://github.com/lovebrew/lovepotion "$W/lovepotion"
patch -d "$W/lovepotion" -p1 < "$CIA/lovepotion-cia.patch"
/opt/devkitpro/portlibs/3ds/bin/arm-none-eabi-cmake -S "$W/lovepotion" -B "$W/lp-build" >/dev/null
make -C "$W/lp-build" -j"$(nproc)" >/dev/null
ELF=$(find "$W/lp-build" -name 'lovepotion.elf' | head -1)
SHBIN=$(find "$W/lp-build" -name '*.shbin' | head -1)
BASE_ROMFS=$(dirname "$(dirname "$SHBIN")")     # LÖVE Potion's own RomFS: shaders/ and nogame/
echo "elf: $ELF  romfs: $BASE_ROMFS"; ls -R "$BASE_ROMFS"

# the game, as a zip
rm -f "$W/game.love"
(cd "$ROOT/3ds/game" && zip -qr -9 "$W/game.love" .)

# .3dsx: LÖVE Potion with our icon and title, the game glued to the end
smdhtool --create "$TITLE" "$DESC" "$AUTHOR" "$ROOT/3ds/icon.png" "$W/icon.smdh"
3dsxtool "$ELF" "$OUT/PizzaMagna.3dsx" --smdh="$W/icon.smdh" --romfs="$BASE_ROMFS"
cat "$W/game.love" >> "$OUT/PizzaMagna.3dsx"

# .cia: the same program, the game in the RomFS, the HOME Menu icon and banner
rm -rf "$W/romfs" && mkdir -p "$W/romfs"
cp -r "$BASE_ROMFS/." "$W/romfs/"
cp "$W/game.love" "$W/romfs/game.love"
"$BANNERTOOL" makesmdh -s "$TITLE" -l "$DESC" -p "$AUTHOR" -i "$ROOT/3ds/icon.png" -o "$W/icon.icn"
"$BANNERTOOL" makebanner -i "$CIA/banner.png" -a "$CIA/banner.wav" -o "$W/banner.bnr"
"$MAKEROM" -f cia -o "$OUT/PizzaMagna.cia" -target t -exefslogo -elf "$ELF" -rsf "$CIA/app.rsf" \
  -icon "$W/icon.icn" -banner "$W/banner.bnr" \
  -DAPP_TITLE="PizzaMagna" -DAPP_PRODUCT_CODE="$PRODUCT_CODE" -DAPP_UNIQUE_ID="$UNIQUE_ID" -DAPP_ROMFS="$W/romfs" \
  -DAPP_CATEGORY=Application -DAPP_USE_ON_SD=true -DAPP_ENCRYPTED=false -DAPP_MEMORY_TYPE=Application \
  -DAPP_SYSTEM_MODE=64MB -DAPP_SYSTEM_MODE_EXT=124MB -DAPP_CPU_SPEED=804MHz -DAPP_VERSION_MAJOR=1
ls -la "$OUT"/PizzaMagna.*
