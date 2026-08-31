#!/usr/bin/env bash
# ==============================================================================
# Script: Install Phosh GUI (On-Demand Mode) for Xiaomi Redmi 5A (riva)
# Keeps Terminal Console as Default Boot Target, Launches GUI only on command
# ==============================================================================
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

echo "=== [1/4] Configuring Phosh Auto-login & Greetd ==="
cat << 'EOF' > /etc/phrog/greetd-config.toml
[terminal]
vt = 7

[default_session]
command = "/usr/libexec/phrog-greetd-session"
user = "greetd"

[initial_session]
command = "systemd-cat phosh-session"
user = "kouzen"
EOF

echo "=== [2/4] Configuring Passwordless Sudo for GUI Helpers ==="
cat << 'EOF' > /etc/sudoers.d/99-phosh-helpers
kouzen ALL=(ALL) NOPASSWD: /usr/local/bin/start-phosh, /usr/local/bin/stop-phosh, /usr/local/bin/start-gui, /usr/local/bin/stop-gui, /usr/local/bin/start-posh, /usr/local/bin/stop-posh, /usr/bin/systemctl, /usr/bin/chvt
EOF
chmod 0440 /etc/sudoers.d/99-phosh-helpers

echo "=== [3/4] Disabling Auto-Start on Boot (Console Stays Default) ==="
systemctl disable greetd.service display-manager.service 2>/dev/null || true
systemctl set-default multi-user.target 2>/dev/null || true

echo "=== [4/4] Creating 'start-phosh' and 'stop-phosh' Helper Commands ==="

# Script start-phosh / start-gui / start-posh
cat << 'EOF' > /usr/local/bin/start-phosh
#!/bin/sh
if [ "$(id -u)" -ne 0 ]; then
    exec sudo "$0" "$@"
fi

echo "=== Memulai Antarmuka Grafis Phosh... ==="
systemctl restart greetd.service 2>/dev/null || true
chvt 7 2>/dev/null || true
systemctl stop fbkeyboard.service 2>/dev/null || true
echo "Phosh GUI telah aktif di layar HP Anda!"
EOF

chmod +x /usr/local/bin/start-phosh
ln -sf /usr/local/bin/start-phosh /usr/local/bin/start-gui
ln -sf /usr/local/bin/start-phosh /usr/local/bin/start-posh

# Script stop-phosh / stop-gui
cat << 'EOF' > /usr/local/bin/stop-phosh
#!/bin/sh
if [ "$(id -u)" -ne 0 ]; then
    exec sudo "$0" "$@"
fi

echo "=== Menghentikan Antarmuka Phosh & Kembali ke Konsol... ==="
systemctl stop greetd.service 2>/dev/null || true
chvt 1 2>/dev/null || true
systemctl restart getty@tty1.service 2>/dev/null || true
systemctl restart fbkeyboard.service 2>/dev/null || true
echo "Kembali ke Terminal Konsol tty1 Berhasil!"
EOF

chmod +x /usr/local/bin/stop-phosh
ln -sf /usr/local/bin/stop-phosh /usr/local/bin/stop-gui
ln -sf /usr/local/bin/stop-phosh /usr/local/bin/stop-posh

echo "=========================================================================="
echo " Phosh GUI On-Demand BERHASIL DIKONFIGURASI!"
echo " - Default Boot: Tetap di Terminal Konsol (Cepat & Hemat Daya)"
echo " - Untuk masuk GUI  : Ketik 'start-phosh' (Tanpa perlu password/sudo)"
echo " - Untuk keluar GUI : Ketik 'stop-phosh' (Tanpa perlu password/sudo)"
echo "=========================================================================="
