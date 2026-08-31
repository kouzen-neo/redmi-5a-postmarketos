#!/usr/bin/env bash
# ==============================================================================
# Script: Build & Install Stock fbkeyboard with Matrix Green & Arrow Navigation Keys
# Target: Xiaomi Redmi 5A (riva) / postmarketOS
# ==============================================================================
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

echo "=== [1/3] Installing Build Dependencies ==="
apk add --no-cache gcc make musl-dev freetype-dev linux-headers git

echo "=== [2/3] Cloning fbkeyboard & Patching Green Theme + Arrow Keys ==="
TMP_DIR=$(mktemp -d)
git clone https://github.com/bakonyiferenc/fbkeyboard.git "$TMP_DIR"
cd "$TMP_DIR"

python3 -c "
with open('fbkeyboard.c', 'r') as f:
    code = f.read()

# 1. Matrix Cyberpunk Neon Green Colors (0x00ff00)
code = code.replace('#define TOUCHCOLOR 0x4444ee', '#define TOUCHCOLOR 0x00ff00')
code = code.replace('#define BUTTONCOLOR 0x111122', '#define BUTTONCOLOR 0x000000')
code = code.replace('#define BACKLITCOLOR 0xff0000', '#define BACKLITCOLOR 0x00ff00')

# 2. Arrow Keys Navigation in Top Special Row (^, v, <, >)
old_special = '''char *special[][7] = {
	{ \"Esc\", \"Tab\", \"F10\", \" / \", \" - \", \" . \", \" \\\\ \" },
	{ \"Esc\", \"Tab\", \"F10\", \" ? \", \" _ \", \" > \", \" | \" },
};'''

new_special = '''char *special[][7] = {
	{ \"Esc\", \"Tab\", \" ^ \", \" v\", \" < \", \" > \", \" / \" },
	{ \"Esc\", \"Tab\", \"Home\", \"End\", \"PgUp\", \"PgDn\", \" | \" },
};'''

old_keys = '''{ KEY_ESC, KEY_TAB, KEY_F10, KEY_SLASH, KEY_MINUS, KEY_DOT, KEY_BACKSLASH },'''
new_keys = '''{ KEY_ESC, KEY_TAB, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SLASH },'''

code = code.replace(old_special, new_special)
code = code.replace(old_keys, new_keys)

with open('fbkeyboard.c', 'w') as f:
    f.write(code)
print('Green theme and Arrow keys applied successfully to stock layout!')
"

make clean && make
cp -v fbkeyboard /usr/bin/fbkeyboard
rm -rf "$TMP_DIR"

echo "=== [3/3] Restarting fbkeyboard Service ==="
systemctl restart fbkeyboard.service

echo "Clean fbkeyboard with Matrix Green theme and Arrow keys is active and running!"
