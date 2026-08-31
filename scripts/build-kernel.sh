#!/usr/bin/env bash
# ==============================================================================
# Script: Compile Mainline Linux Kernel for MSM8917 (Redmi 5A)
# ==============================================================================
set -euo pipefail

VENV_DIR="${HOME}/.local/share/pmbootstrap-venv"
PMB="${VENV_DIR}/bin/pmbootstrap"

if [ ! -f "${PMB}" ]; then
    echo "Error: pmbootstrap binary not found in ${VENV_DIR}."
    exit 1
fi

echo "=== [1/2] Compiling Mainline Linux Kernel (linux-postmarketos-qcom-msm89x7) ==="
${PMB} build --arch=aarch64 linux-postmarketos-qcom-msm89x7

echo "=== [2/2] Updating Device Package & DTB (device-qcom-msm89x7) ==="
${PMB} build --arch=aarch64 device-qcom-msm89x7

echo "Build complete. Compiled packages are available in pmbootstrap cache."
