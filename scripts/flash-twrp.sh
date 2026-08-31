#!/usr/bin/env bash
# ==============================================================================
# Script: Flash postmarketOS to Redmi 5A via Recovery (TWRP / PBRP)
# ==============================================================================
set -euo pipefail

ZIP_PATH="${1:-${HOME}/pmos-export/pmos-qcom-msm89x7.zip}"

echo "=== [1/3] Checking Device Recovery Connection ==="
if ! adb devices | grep -q "recovery"; then
    echo "Error: Redmi 5A not detected in recovery mode."
    echo "Please boot into TWRP/PBRP and ensure the USB cable is connected."
    exit 1
fi

if [ ! -f "${ZIP_PATH}" ]; then
    echo "Error: Installer zip not found at: ${ZIP_PATH}"
    echo "Please run scripts/build-recovery-zip.sh first."
    exit 1
fi

echo "=== [2/3] Uploading Installer Package to Device RAM ==="
adb push "${ZIP_PATH}" /tmp/pmos.zip

echo "=== [3/3] Executing postmarketOS Installation ==="
adb shell twrp install /tmp/pmos.zip

echo "=================================================================="
echo "Installation complete. Reboot device with: adb reboot"
echo "=================================================================="
