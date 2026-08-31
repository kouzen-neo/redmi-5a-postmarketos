# Troubleshooting & Debugging Guide

This document records technical issues encountered during the Mainline Linux porting and deployment process on the Qualcomm Snapdragon 425 platform and their concrete solutions.

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

## 2. Emergency Mode on Boot ("Cannot open access to console, the root account is locked")

### Symptom:
After making manual partition changes or `extlinux.conf` modifications, the system boots into a text screen saying:
```text
You are in emergency mode. After logging in, type "journalctl -xb" to view system logs...
Cannot open access to console, the root account is locked.
```

### Root Cause:
`systemd` enters emergency mode if any entry in `/etc/fstab` fails to mount (e.g. invalid UUID, missing device, or fsck error). In default postmarketOS, the `root` account has no password set (only the default user has `sudo` access), preventing manual login in emergency console mode.

### Solution:
1. Reboot the phone into Recovery Mode (hold `Power + Volume Up` for ~8-10s).
2. Connect USB to PC and inspect `/boot/extlinux/extlinux.conf` and `/etc/fstab` via `adb shell`:
   ```bash
   adb shell
   # Mount boot and rootfs partitions
   losetup -o 1048576 /dev/block/loop0 /dev/block/mmcblk0p24
   losetup -o 255852544 /dev/block/loop1 /dev/block/mmcblk0p24
   mkdir -p /mnt/boot /mnt/root
   mount /dev/block/loop0 /mnt/boot
   mount /dev/block/loop1 /mnt/root
   ```
3. Ensure `pmos_root_uuid` in `/mnt/boot/extlinux/extlinux.conf` exactly matches the UUID of `pmOS_root` (`7c50ec00-f65c-4c4b-82c6-a0c13f0c8612`).
4. Ensure `/mnt/root/etc/fstab` only contains valid, existing partition UUIDs.
5. Unmount and reboot:
   ```bash
   umount /mnt/boot /mnt/root
   adb reboot
   ```

---

## 3. Host Kernel Module `loop` Mismatch (Arch / CachyOS)

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
