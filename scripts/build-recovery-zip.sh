#!/usr/bin/env bash
# ==============================================================================
# Script: Build Android Recovery Installer ZIP for Redmi 5A (riva)
# ==============================================================================
set -euo pipefail

VENV_DIR="${HOME}/.local/share/pmbootstrap-venv"
PMB="${VENV_DIR}/bin/pmbootstrap"
WORKDIR="${HOME}/.local/var/pmbootstrap"
EXPORT_DIR="${HOME}/pmos-export"

echo "=== [1/3] Configuring Target Device (qcom-msm89x7) ==="
${PMB} config device qcom-msm89x7
${PMB} config ui console
${PMB} config extra_packages "openssh,htop,nano,tmux,neofetch,curl,git"

echo "=== [2/3] Building Recovery Installer ZIP ==="
${PMB} install --android-recovery-zip

echo "=== [3/3] Exporting Installation Package ==="
mkdir -p "${EXPORT_DIR}"
RECOVERY_ZIP=$(find "${WORKDIR}/chroot_buildroot_aarch64" -name "pmos-*.zip" | head -n 1)

if [ -f "${RECOVERY_ZIP}" ]; then
    cp -v "${RECOVERY_ZIP}" "${EXPORT_DIR}/pmos-qcom-msm89x7.zip"
    echo "=================================================================="
    echo "SUCCESS: Installer package saved to: ${EXPORT_DIR}/pmos-qcom-msm89x7.zip"
    echo "=================================================================="
else
    echo "Error: Recovery zip artifact not found."
    exit 1
fi
