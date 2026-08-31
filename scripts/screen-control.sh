#!/usr/bin/env bash
# ==============================================================================
# Script: Control LCD Backlight on Redmi 5A (postmarketOS)
# ==============================================================================
set -euo pipefail

BACKLIGHT_PATH="/sys/class/backlight/backlight/brightness"

if [ ! -f "${BACKLIGHT_PATH}" ]; then
    echo "Error: Backlight sysfs node not found at ${BACKLIGHT_PATH}."
    exit 1
fi

case "${1:-}" in
    off)
        echo 0 > "${BACKLIGHT_PATH}"
        echo "LCD backlight turned OFF (0% brightness)."
        ;;
    dim)
        echo 10 > "${BACKLIGHT_PATH}"
        echo "LCD backlight dimmed to minimum (10/255)."
        ;;
    on)
        echo 128 > "${BACKLIGHT_PATH}"
        echo "LCD backlight set to standard brightness (128/255)."
        ;;
    max)
        echo 255 > "${BACKLIGHT_PATH}"
        echo "LCD backlight set to maximum brightness (255/255)."
        ;;
    set)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 set <0-255>"
            exit 1
        fi
        echo "$2" > "${BACKLIGHT_PATH}"
        echo "LCD backlight set to $2/255."
        ;;
    *)
        echo "Usage: $0 {off|dim|on|max|set <0-255>}"
        exit 1
        ;;
esac
