#!/usr/bin/env bash
# ==============================================================================
# Script: Disable Wi-Fi Power Saving & Fix DNS (Redmi 5A / postmarketOS)
# ==============================================================================
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

echo "=== [1/3] Disabling Wi-Fi Power Save in NetworkManager ==="
mkdir -p /etc/NetworkManager/conf.d
cat << 'EOF' > /etc/NetworkManager/conf.d/disable-wifi-powersave.conf
[connection]
wifi.powersave = 2
EOF

echo "=== [2/3] Disabling Wi-Fi Power Save on wlan0 (Qualcomm WCN36xx) ==="
if command -v iw &>/dev/null; then
    iw dev wlan0 set power_save off 2>/dev/null || true
fi

echo "=== [3/3] Setting Static DNS Nameservers ==="
rm -f /etc/resolv.conf
cat << 'EOF' > /etc/resolv.conf
nameserver 192.168.100.1
nameserver 1.1.1.1
nameserver 8.8.8.8
EOF

systemctl restart NetworkManager 2>/dev/null || true

echo "Wi-Fi power saving disabled and DNS configured successfully."
