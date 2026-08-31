# Troubleshooting & Debugging Guide

This document records technical issues encountered during the Mainline Linux porting process on the Qualcomm Snapdragon 425 platform and their solutions.

---

## 1. Fastboot Raw Image Flash Stall (Empty Log)

### Symptom:
Executing `fastboot flash userdata <raw_image.img>` hangs without error messages or progress output for extended periods.

### Root Cause:
The stock Qualcomm fastboot implementation has limited USB transfer buffer capacity. When attempting to stream uncompressed raw images (>1 GB) containing zero-filled blocks, the USB bulk endpoint stalls.

### Solution:
Deploy using the **Android Recovery Installer ZIP** method:
```bash
pmbootstrap install --android-recovery-zip --password <PASSWORD>
```
Transfer the resulting zip to the recovery environment (TWRP / OrangeFox / PitchBlack):
```bash
adb push ~/.local/var/pmbootstrap/chroot_buildroot_aarch64/var/lib/postmarketos-android-recovery-installer/pmos-qcom-msm89x7.zip /tmp/pmos.zip
adb shell twrp install /tmp/pmos.zip
```
The recovery installer executes partition formatting and rootfs extraction locally via the phone's native kernel and eMMC storage controller (~30 MB/s transfer speed).

---

## 2. Host Kernel Module `loop` Mismatch (Arch / CachyOS)

### Symptom:
```text
modprobe: FATAL: Module loop not found in directory /lib/modules/...
```

### Root Cause:
When the host Linux kernel package is updated without a system reboot, the `/lib/modules/` directory corresponding to the currently running kernel version may be removed or replaced.

### Solution:
Extract the matching module tree from the package manager cache:
```bash
sudo tar -xvf /var/cache/pacman/pkg/linux-cachyos-<RUNNING_VERSION>.pkg.tar.zst -C / usr/lib/modules/<RUNNING_VERSION>
sudo depmod -a <RUNNING_VERSION>
sudo modprobe loop
```
Ensure that device nodes `/dev/loop0` through `/dev/loop7` are available:
```bash
for i in {0..7}; do
    [ ! -b /dev/loop$i ] && sudo mknod -m 0660 /dev/loop$i b 7 $i && sudo chown root:disk /dev/loop$i
done
```

---

## 3. Partition UUID Alignment in `extlinux.conf`

### Symptom:
The kernel boots, but the initramfs fails to mount the root filesystem with the message:
```text
Waiting for root device UUID=...
```

### Solution:
1. Boot into recovery mode.
2. Query the actual partition UUIDs:
   ```bash
   adb shell blkid | grep pmOS
   ```
3. Update `pmos_boot_uuid` and `pmos_root_uuid` in `/boot/extlinux/extlinux.conf` and `/etc/fstab` on the target root filesystem.
