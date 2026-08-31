#!/usr/bin/env bash
# ==============================================================================
# Script: Build & Install Stock fbkeyboard with Matrix Green Theme (Redmi 5A)
# ==============================================================================
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

echo "=== [1/3] Installing Build Dependencies ==="
apk add --no-cache gcc make musl-dev freetype-dev linux-headers git

echo "=== [2/3] Cloning fbkeyboard & Patching Green Theme ==="
TMP_DIR=$(mktemp -d)
git clone https://github.com/bakonyiferenc/fbkeyboard.git "$TMP_DIR"
cd "$TMP_DIR"

python3 -c "
with open('fbkeyboard.c', 'r') as f:
    code = f.read()

# Matrix Cyberpunk Neon Green Colors (0x00ff00)
code = code.replace('#define TOUCHCOLOR 0x4444ee', '#define TOUCHCOLOR 0x00ff00')
code = code.replace('#define BUTTONCOLOR 0x111122', '#define BUTTONCOLOR 0x000000')
code = code.replace('#define BACKLITCOLOR 0xff0000', '#define BACKLITCOLOR 0x00ff00')

with open('fbkeyboard.c', 'w') as f:
    f.write(code)
print('Green theme applied successfully to stock layout!')
"

make clean && make
cp -v fbkeyboard /usr/bin/fbkeyboard
rm -rf "$TMP_DIR"

echo "=== [3/3] Restarting fbkeyboard Service ==="
systemctl restart fbkeyboard.service

echo "Stock fbkeyboard with Matrix Green theme is active and running!"
