#!/usr/bin/env bash
# ==============================================================================
# Script: Automatically Format & Mount 10GB Internal eMMC Partition (/data)
# Target Device: Xiaomi Redmi 5A (riva / Qualcomm Snapdragon 425)
# ==============================================================================
set -euo pipefail

MOUNT_POINT="/data"
USER_NAME="${SUDO_USER:-$(whoami)}"

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

echo "=== [1/4] Detecting 10GB Userdata Partition ==="
TARGET_DEV=""
for dev in /dev/block/bootdevice/by-name/userdata /dev/mmcblk0p49 /dev/mmcblk1p49; do
    if [ -b "$dev" ]; then
        TARGET_DEV="$dev"
        break
    fi
done

if [ -z "${TARGET_DEV}" ]; then
    echo "Error: Userdata partition not found."
    exit 1
fi

echo "Found userdata partition: ${TARGET_DEV}"

echo "=== [2/4] Formatting Partition to ext4 ==="
# Check if already formatted as ext4
EXISTING_FS=$(blkid -s TYPE -o value "${TARGET_DEV}" 2>/dev/null || true)
if [ "${EXISTING_FS}" != "ext4" ]; then
    echo "Formatting ${TARGET_DEV} to ext4..."
    mkfs.ext4 -F -L "data" "${TARGET_DEV}"
else
    echo "Partition is already formatted as ext4."
fi

PART_UUID=$(blkid -s UUID -o value "${TARGET_DEV}")
echo "Partition UUID: ${PART_UUID}"

echo "=== [3/4] Configuring Persistent Mount in /etc/fstab ==="
mkdir -p "${MOUNT_POINT}"

if ! grep -q "${MOUNT_POINT}" /etc/fstab; then
    echo "UUID=${PART_UUID}  ${MOUNT_POINT}  ext4  defaults,noatime  0  2" >> /etc/fstab
    echo "Added ${MOUNT_POINT} entry to /etc/fstab."
else
    echo "${MOUNT_POINT} is already registered in /etc/fstab."
fi

mount -a

echo "=== [4/4] Setting Permissions for User (${USER_NAME}) ==="
if [ "${USER_NAME}" != "root" ] && id "${USER_NAME}" &>/dev/null; then
    chown -R "${USER_NAME}:${USER_NAME}" "${MOUNT_POINT}"
    chmod 775 "${MOUNT_POINT}"
    
    USER_HOME=$(eval echo "~${USER_NAME}")
    if [ -d "${USER_HOME}" ] && [ ! -e "${USER_HOME}/data" ]; then
        ln -s "${MOUNT_POINT}" "${USER_HOME}/data"
        chown -h "${USER_NAME}:${USER_NAME}" "${USER_HOME}/data"
        echo "Created shortcut: ${USER_HOME}/data -> ${MOUNT_POINT}"
    fi
fi

echo "=================================================================="
echo "Storage activation complete! Current disk status:"
df -h / "${MOUNT_POINT}"
echo "=================================================================="
