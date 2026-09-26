#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-GTAV-GOLD.apk}"
OUT="${2:-GTAV-GOLD-BUILD.apk}"
EXPECTED="c7db44f0decdbe07ca2302ac4a4c75728eb085530f4ea1b2da9639b35e05fd93"

echo "$EXPECTED  $BASE" | sha256sum -c -

rm -rf build/apk
mkdir -p build/apk
unzip -q "$BASE" -d build/apk

if [ -f patch/libgtav_native_renderer.so ]; then
  target="$(find build/apk -type f -path '*/lib/arm64-v8a/libgtav_native_renderer.so' -print -quit)"
  test -n "$target"
  cp patch/libgtav_native_renderer.so "$target"
  echo "Injected renderer: $(sha256sum patch/libgtav_native_renderer.so)"
else
  echo "No renderer patch supplied; rebuilding exact Gold payload."
fi

rm -f "$OUT"
(
  cd build/apk
  zip -q -r -0 "../../$OUT" .
)
sha256sum "$OUT"
