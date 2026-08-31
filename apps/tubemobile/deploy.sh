#!/usr/bin/env bash
# ==============================================================================
# Script: Deploy TubeMobile to Redmi 5A (postmarketOS)
# ==============================================================================
set -euo pipefail

TARGET_IP="192.168.100.21"
TARGET_USER="kouzen"
SSH_OPTS="-o StrictHostKeyChecking=no"

echo "=== [1/3] Syncing TubeMobile Application Files to Redmi 5A ==="
ssh $SSH_OPTS ${TARGET_USER}@${TARGET_IP} "
mkdir -p /tmp/tubemobile
"

scp $SSH_OPTS -r /home/kouzen/Documents/Projects/lowlevel/apps/tubemobile/tubemobile ${TARGET_USER}@${TARGET_IP}:/tmp/tubemobile/
scp $SSH_OPTS -r /home/kouzen/Documents/Projects/lowlevel/apps/tubemobile/data ${TARGET_USER}@${TARGET_IP}:/tmp/tubemobile/

echo "=== [2/3] Installing to System Directories ==="
ssh $SSH_OPTS ${TARGET_USER}@${TARGET_IP} '
echo "276543" | sudo -S bash -c "
mkdir -p /usr/local/share/tubemobile
rm -rf /usr/local/share/tubemobile/*
cp -r /tmp/tubemobile/tubemobile /usr/local/share/tubemobile/

# Install Icon
mkdir -p /usr/share/icons/hicolor/scalable/apps
cp /tmp/tubemobile/data/icons/tubemobile.svg /usr/share/icons/hicolor/scalable/apps/

# Install Desktop Entry
cp /tmp/tubemobile/data/com.github.kouzen.tubemobile.desktop /usr/share/applications/

# Update icon and desktop databases
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database /usr/share/applications/ 2>/dev/null || true

# Cleanup
rm -rf /tmp/tubemobile
"
'

echo "=== [3/3] Deployment Successful! ==="
echo "TubeMobile sudah berhasil dipasang di Redmi 5A Anda!"
