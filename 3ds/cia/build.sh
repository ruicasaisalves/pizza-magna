#!/bin/bash
# Builds the 3DS port as PizzaMagna.3dsx (Homebrew Launcher) and the parts of PizzaMagna.cia (installed to the HOME
# Menu, e.g. with FBI's Remote Install > Scan QR Code), in build-3ds/cia-parts. Runs in the devkitpro/devkitarm
# container (.github/workflows/3ds.yml); cia.sh then packs the .cia on the runner itself, because makerom's Linux
# build needs a newer glibc than the container has.
#
# LÖVE Potion is built from source with one patch (lovepotion-cia.patch): installed as a .cia it has no program file
# to read the game from, so it reads it from romfs:/game.love. The game goes into both files as a zip of 3ds/game:
# glued to the end of the .3dsx (as LÖVE Potion's own fused builds do) and as game.love in the .cia's RomFS.
# bannertool (Epicpkmn11's fork) comes from its GitHub releases.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
CIA=$ROOT/3ds/cia
OUT=${OUT:-$ROOT/build-3ds}
W=$OUT/work
LOVEPOTION_TAG=3.0.2
TITLE="Pizza Magna"
DESC="Pizzeria tycoon in 90s pixel art"
AUTHOR="Pizza Magna"
P=$OUT/cia-parts
mkdir -p "$W" "$OUT" "$P"

# bannertool, the Linux build from its latest release
asset() {   # the newest asset matching $2 among the repo's recent releases
  local all url
  all=$(curl -fsSL ${GITHUB_TOKEN:+-H "Authorization: Bearer $GITHUB_TOKEN"} "https://api.github.com/repos/$1/releases?per_page=30" \
    | grep -o '"browser_download_url": *"[^"]*"' | cut -d'"' -f4)
  url=$(echo "$all" | grep -E "$2" | head -1)
  if [ -z "$url" ]; then echo "no asset matching $2 in $1; found:" >&2; echo "$all" | head -40 >&2; return 1; fi
  echo "$url"; }
mkdir -p "$W/bin"
# bannertool: the maintained fork (Steveice10's repository is gone)
BT=$(asset Epicpkmn11/bannertool 'bannertool\.zip$'); echo "bannertool: $BT"; curl -fsSL -o "$W/bannertool.zip" "$BT"
(cd "$W/bin" && unzip -oq ../bannertool.zip)
BANNERTOOL=$(find "$W/bin" -type f -path '*linux-x86_64*' -name bannertool | head -1)
chmod +x "$BANNERTOOL"

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

# the .cia's parts: the same program, the game in the RomFS, the HOME Menu icon and banner (cia.sh packs them)
rm -rf "$P/romfs" && mkdir -p "$P/romfs"
cp -r "$BASE_ROMFS/." "$P/romfs/"
cp "$W/game.love" "$P/romfs/game.love"
cp "$ELF" "$P/lovepotion.elf"
"$BANNERTOOL" makesmdh -s "$TITLE" -l "$DESC" -p "$AUTHOR" -i "$ROOT/3ds/icon.png" -o "$P/icon.icn"
"$BANNERTOOL" makebanner -i "$CIA/banner.png" -a "$CIA/banner.wav" -o "$P/banner.bnr"
ls -la "$OUT/PizzaMagna.3dsx" "$P"
