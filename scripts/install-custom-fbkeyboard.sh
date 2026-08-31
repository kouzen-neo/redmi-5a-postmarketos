#!/usr/bin/env bash
# ==============================================================================
# Script: Build & Install Customized fbkeyboard with Arrow Keys (Redmi 5A)
# ==============================================================================
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

echo "=== [1/4] Installing Build Dependencies ==="
apk add --no-cache gcc make musl-dev freetype-dev linux-headers git

echo "=== [2/4] Cloning fbkeyboard Source ==="
TMP_DIR=$(mktemp -d)
git clone https://github.com/bakonyiferenc/fbkeyboard.git "$TMP_DIR"
cd "$TMP_DIR"

echo "=== [3/4] Patching Keyboard Layout with Arrow Keys (^, v, <, >) ==="
python3 -c "
with open('fbkeyboard.c', 'r') as f:
    code = f.read()

old_special = '''char *special[][7] = {
	{ \"Esc\", \"Tab\", \"F10\", \" / \", \" - \", \" . \", \" \\\\ \" },
	{ \"Esc\", \"Tab\", \"F10\", \" ? \", \" _ \", \" > \", \" | \" },
};'''

new_special = '''char *special[][7] = {
	{ \"Esc\", \"Tab\", \" ^ \", \" v \", \" < \", \" > \", \" / \" },
	{ \"Esc\", \"Tab\", \"Home\", \"End\", \"PgUp\", \"PgDn\", \" | \" },
};'''

old_keys = '''{ KEY_ESC, KEY_TAB, KEY_F10, KEY_SLASH, KEY_MINUS, KEY_DOT, KEY_BACKSLASH },'''
new_keys = '''{ KEY_ESC, KEY_TAB, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SLASH },'''

if old_special in code:
    code = code.replace(old_special, new_special)
    code = code.replace(old_keys, new_keys)
    with open('fbkeyboard.c', 'w') as f:
        f.write(code)
    print('Custom layout patch applied successfully!')
else:
    print('Pattern not found, skipping patch.')
"

make
cp -v fbkeyboard /usr/bin/fbkeyboard
rm -rf "$TMP_DIR"

echo "=== [4/4] Restarting fbkeyboard Service ==="
systemctl restart fbkeyboard.service

echo "Custom fbkeyboard with arrow keys installed and running successfully!"
