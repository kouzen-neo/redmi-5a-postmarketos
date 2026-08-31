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

echo "=== [1/4] Installing Phosh Mobile UI Packages ==="
apk add --no-cache postmarketos-ui-phosh postmarketos-ui-phosh-systemd gnome-console

echo "=== [2/4] Disabling Auto-Start on Boot (Console Stays Default) ==="
# Disable TinyDM display manager so device always boots into Console UI
systemctl disable tinydm.service 2>/dev/null || true
systemctl set-default multi-user.target 2>/dev/null || true

echo "=== [3/4] Creating 'start-phosh' and 'stop-phosh' Helper Commands ==="

# Script start-phosh / start-gui
cat << 'EOF' > /usr/local/bin/start-phosh
#!/bin/sh
echo "=== Memulai Antarmuka Grafis Phosh... ==="
# Matikan fbkeyboard agar input touchscreen dialihkan ke Wayland/Phosh
echo "276543" | sudo -S systemctl stop fbkeyboard.service 2>/dev/null || sudo systemctl stop fbkeyboard.service
# Jalankan TinyDM Display Manager
echo "276543" | sudo -S systemctl start tinydm.service 2>/dev/null || sudo systemctl start tinydm.service
echo "Phosh GUI telah aktif di layar HP Anda!"
EOF

chmod +x /usr/local/bin/start-phosh
ln -sf /usr/local/bin/start-phosh /usr/local/bin/start-gui

# Script stop-phosh / stop-gui
cat << 'EOF' > /usr/local/bin/stop-phosh
#!/bin/sh
echo "=== Menghentikan Antarmuka Phosh & Kembali ke Konsol... ==="
# Hentikan TinyDM
echo "276543" | sudo -S systemctl stop tinydm.service 2>/dev/null || sudo systemctl stop tinydm.service
# Nyalakan kembali fbkeyboard di tty1
echo "276543" | sudo -S systemctl restart fbkeyboard.service 2>/dev/null || sudo systemctl restart fbkeyboard.service
echo "Kembali ke Terminal Konsol (RAM ~600MB dibebaskan bersih)!"
EOF

chmod +x /usr/local/bin/stop-phosh
ln -sf /usr/local/bin/stop-phosh /usr/local/bin/stop-gui

echo "=== [4/4] Verifying fbkeyboard Service ==="
systemctl restart fbkeyboard.service

echo "=========================================================================="
echo " Phosh GUI On-Demand BERHASIL DIPASANG!"
echo " - Default Boot: Tetap di Terminal Konsol (Cepat & Hemat Daya)"
echo " - Untuk masuk GUI  : Ketik 'start-phosh' atau 'start-gui'"
echo " - Untuk keluar GUI : Ketik 'stop-phosh' atau 'stop-gui' (atau klik Log Out)"
echo "=========================================================================="
