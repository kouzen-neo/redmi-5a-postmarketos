#!/usr/bin/env bash
# ==============================================================================
# Script: Complete Uninstall / Removal of Phosh UI (Redmi 5A)
# Restores 100% Console-Only Mode with Green fbkeyboard
# ==============================================================================
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

echo "=== [1/4] Stopping Phosh & TinyDM Services ==="
systemctl stop tinydm.service 2>/dev/null || true
systemctl disable tinydm.service 2>/dev/null || true

echo "=== [2/4] Removing Phosh & Desktop Packages ==="
apk del postmarketos-ui-phosh \
        postmarketos-ui-phosh-systemd \
        phosh \
        phoc \
        squeekboard \
        tinydm \
        tinydm-systemd \
        phosh-mobile-settings \
        phosh-osk-data \
        2>/dev/null || true

echo "=== [3/4] Removing Helper Commands ==="
rm -f /usr/local/bin/start-phosh \
      /usr/local/bin/stop-phosh \
      /usr/local/bin/start-gui \
      /usr/local/bin/stop-gui

echo "=== [4/4] Restoring Console fbkeyboard Service ==="
systemctl daemon-reload
systemctl restart fbkeyboard.service

echo "=== Phosh UI has been completely removed! Console mode restored 100% ==="
