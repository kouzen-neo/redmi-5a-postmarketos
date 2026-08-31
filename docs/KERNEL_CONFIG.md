# Mainline Linux Kernel Configuration (Qualcomm MSM8917)

Configuration file: [`port/linux-postmarketos-qcom-msm89x7/config-postmarketos-qcom-msm89x7.aarch64`](../port/linux-postmarketos-qcom-msm89x7/config-postmarketos-qcom-msm89x7.aarch64)

---

## Essential Kernel Subsystems and Drivers

### 1. Wireless & Network Subsystems
* `CONFIG_WCN36XX=m`: Open-source driver for Qualcomm WCN36xx Wi-Fi chipsets (WCN3620/WCN3660/WCN3680).
* `CONFIG_BT_QCA=m`: Qualcomm Atheros Bluetooth driver.
* `CONFIG_USB_NET_DRIVERS=y`: Drivers for USB Network CDC-NCM and CDC-Ethernet.

### 2. Graphics & Display Subsystem
* `CONFIG_DRM_MSM=m`: Direct Rendering Manager (DRM) for Qualcomm Adreno GPUs and Mobile Display Subsystem (MDSS).
* `CONFIG_DRM_PANEL_SIMPLE=y`: Generic DSI panel framework.
* `CONFIG_BACKLIGHT_CLASS_DEVICE=y`: Hardware LCD backlight control via `/sys/class/backlight/`.

### 3. Power Management & Chipset Bus
* `CONFIG_ARCH_QCOM=y`: Base Qualcomm ARM64 platform architecture support.
* `CONFIG_QCOM_SMD_RPM=y`: Resource Power Manager (RPM) communication over Shared Memory Driver (SMD).
* `CONFIG_QCOM_SPMI_PMIC=y`: Qualcomm SPMI Power Management IC driver.

### 4. USB Gadget Subsystems
* `CONFIG_USB_CONFIGFS=y`: ConfigFS-based USB gadget interface.
* `CONFIG_USB_CONFIGFS_NCM=y`: USB Ethernet gadget support.
* `CONFIG_USB_CONFIGFS_SERIAL=y`: USB CDC-ACM Serial console support.
