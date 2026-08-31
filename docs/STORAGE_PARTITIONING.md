# Storage Architecture & Partition Layout (Redmi 5A)

This document details the internal 16 GB eMMC partition layout of the Xiaomi Redmi 5A (`riva` / Qualcomm MSM8917) and how storage is mapped in postmarketOS.

---

## eMMC Partition Overview (16 GB Physical Flash)

On Qualcomm platforms, the internal eMMC is divided into multiple hardware partitions. The two largest partitions are:

1. **System Partition (`/dev/block/bootdevice/by-name/system` / `mmcblk0p24` - 3 GB):**
   * Formatted by the postmarketOS recovery installer into a subpartitioned image:
     * `/boot` (`pmOS_boot` - ext2, 243 MB)
     * `/` (`pmOS_root` - ext4, 2.8 GB)
   * Holds the Linux base system, core packages, and system daemons.

2. **Userdata Partition (`/dev/block/bootdevice/by-name/userdata` / `mmcblk0p49` - 10 GB):**
   * The largest contiguous flash area (~10 GB).
   * Left unmounted by default after initial recovery ZIP installation.
   * Formatted as **ext4** and mounted at **`/data`** to provide the main high-capacity workspace.

---

## Partition Mapping Table

| Mount Point | Partition Node | Size | Filesystem | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`/boot`** | Subpartition inside `system` | ~243 MB | `ext2` | Kernel (`vmlinuz`), DTBs, and `extlinux.conf` |
| **`/`** | Subpartition inside `system` | ~2.8 GB | `ext4` | Base OS rootfs, binaries, and system libraries |
| **`/data`** | `/dev/block/bootdevice/by-name/userdata` | **~10.0 GB** | `ext4` | Main persistent data, user projects, downloads |
| **`/run/msm-firmware-loader/mnt/modem`** | `/dev/block/bootdevice/by-name/modem` | ~84 MB | `vfat` (RO) | Qualcomm Baseband and Wi-Fi/BT microcode |
| **`/run/msm-firmware-loader/mnt/dsp`** | `/dev/block/bootdevice/by-name/dsp` | ~16 MB | `ext4` (RO) | Hexagon DSP coprocessor firmware |
| **`/run/msm-firmware-loader/mnt/persist`** | `/dev/block/bootdevice/by-name/persist` | ~32 MB | `ext4` (RO) | Hardware calibration and MAC address data |

---

## Automated Activation of the 10 GB Partition

To initialize and permanently mount the 10 GB partition on any fresh installation:

```bash
sudo ./scripts/setup-storage.sh
```

This script:
1. Detects `/dev/block/bootdevice/by-name/userdata`.
2. Formats the volume as `ext4` (with volume label `data`).
3. Appends the persistent UUID to `/etc/fstab` with `defaults,noatime`.
4. Creates the mountpoint `/data` and sets permissions for the non-root user.
5. Adds a user-space symlink at `~/data`.
