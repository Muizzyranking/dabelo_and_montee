#!/usr/bin/env bash
set -euo pipefail


# ── Fonts (watermark) ────────────────────────────────────────────────
FONTS_DIR="static/fonts"
mkdir -p "$FONTS_DIR"

# ── Cormorant (Dabelo watermark) ──────────────────────────────────────
CORMORANT="$FONTS_DIR/Cormorant-Regular.ttf"
if [ ! -f "$CORMORANT" ]; then
  echo "Downloading Cormorant-Regular.ttf..."
  curl -sL "https://github.com/CatharsisFonts/Cormorant/raw/master/fonts/ttf/Cormorant-Regular.ttf" \
    -o "$CORMORANT"
  echo "  ✓ Saved to $CORMORANT"
else
  echo "  ✓ Cormorant-Regular.ttf already present"
fi

# ── Playfair Display (Motee watermark) ───────────────────────────────
PLAYFAIR="$FONTS_DIR/PlayfairDisplay-Regular.ttf"
if [ ! -f "$PLAYFAIR" ]; then
  echo "Downloading PlayfairDisplay-Regular.ttf..."
  curl -sL "https://github.com/clauseggers/Playfair/raw/master/fonts/ttf/PlayfairDisplay-Regular.ttf" \
    -o "$PLAYFAIR"
  echo "  ✓ Saved to $PLAYFAIR"
else
  echo "  ✓ PlayfairDisplay-Regular.ttf already present"
fi


# ── Chart.js (admin dashboard) ───────────────────────────────────────
if [ ! -f static/js/admin_dashboard/chart.umd.min.js ]; then
  echo "Downloading Chart.js..."
  mkdir -p static/js/admin_dashboard
  curl -sL "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" \
    -o static/js/admin_dashboard/chart.umd.min.js
  echo "  ✓ Chart.js saved"
else
  echo "  ✓ Chart.js already present"
fi

if [ ! -f ./tailwindcss ]; then
  echo "Downloading Tailwind CSS binary..."
  curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
  mv tailwindcss-linux-x64 tailwindcss
  chmod +x tailwindcss
fi

echo "Compiling Tailwind CSS..."
./tailwindcss -i static/css/input.css -o static/css/output.css --minify
echo "  ✓ CSS compiled"
