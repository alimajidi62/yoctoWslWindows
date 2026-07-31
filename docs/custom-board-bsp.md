# Adding a Custom Board BSP to Yocto

This guide covers how to add a non-evaluation custom ARM board (e.g. TI AM62x/AM64x/J721E)
to the Yocto build system — including machine config, Device Tree, RAM/Flash declarations,
and custom drivers.

---

## Concepts First

| Term | What it means |
|---|---|
| **BSP** | Board Support Package — all software specific to your hardware |
| **meta-layer** | A directory of recipes and configs that Yocto reads |
| **Machine config** | A `.conf` file that describes your SoC and board to BitBake |
| **Device Tree (DTS)** | A text file describing physical hardware to the Linux kernel |
| **bbappend** | A file that extends/overrides an existing recipe without copying it |

---

## Repository Structure

```
meta-myboard/
├── conf/
│   ├── layer.conf                          ← layer registration
│   └── machine/
│       └── myboard.conf                    ← machine definition (key file)
├── recipes-bsp/
│   └── u-boot/
│       ├── u-boot-ti-staging_%.bbappend    ← bootloader patches/config
│       └── files/
│           └── myboard_defconfig           ← U-Boot defconfig for your board
├── recipes-kernel/
│   └── linux/
│       ├── linux-ti-staging_%.bbappend     ← kernel patches/config
│       └── files/
│           ├── k3-myboard.dts              ← Device Tree (your board layout)
│           ├── myboard.cfg                 ← kernel Kconfig fragment
│           └── 0001-my-driver.patch        ← optional out-of-tree driver patch
└── recipes-modules/
    └── my-driver/
        └── my-driver.bb                    ← out-of-tree kernel module recipe
```

---

## Step 1 — Create the BSP Layer

```bash
cd /home/ali/bitbake-builds/poky-master/build
source init-build-env

# Create skeleton layer
bitbake-layers create-layer ../../layers/meta-myboard

# Register it with BitBake
bitbake-layers add-layer ../../layers/meta-myboard
```

If your board is TI-based, also add `meta-ti` as a dependency:

```bash
git clone https://git.ti.com/git/arago-project/meta-ti.git \
  ../../layers/meta-ti

bitbake-layers add-layer ../../layers/meta-ti/meta-ti-bsp
bitbake-layers add-layer ../../layers/meta-ti/meta-ti-extras
```

---

## Step 2 — Layer Configuration

`meta-myboard/conf/layer.conf`:

```bitbake
BBPATH .= ":${LAYERDIR}"
BBFILES += "${LAYERDIR}/recipes-*/*/*.bb ${LAYERDIR}/recipes-*/*/*.bbappend"
BBFILE_COLLECTIONS += "myboard"
BBFILE_PATTERN_myboard = "^${LAYERDIR}/"
BBFILE_PRIORITY_myboard = "10"         # higher than meta-ti (6) to override it

LAYERDEPENDS_myboard = "core ti-bsp"   # depends on OE-core and meta-ti-bsp
LAYERSERIES_COMPAT_myboard = "styhead scarthgap"
```

---

## Step 3 — Machine Configuration File

`meta-myboard/conf/machine/myboard.conf` is the central file that defines your board.

```bitbake
# ── SoC / CPU Architecture ──────────────────────────────────────
# Match your exact TI SoC below:
#   AM62x / AM64x (Cortex-A53)  → cortexa53
#   AM57x         (Cortex-A15)  → cortexa15-neon
#   AM335x        (Cortex-A8)   → cortexa8hf-neon
#   J721E / J784S (Cortex-A72)  → cortexa72
DEFAULTTUNE = "cortexa53"
require conf/machine/include/arm/armv8a/tune-cortexa53.inc

# ── Kernel ──────────────────────────────────────────────────────
PREFERRED_PROVIDER_virtual/kernel = "linux-ti-staging"
PREFERRED_VERSION_linux-ti-staging = "6.1%"
KMACHINE = "myboard"

# ── Bootloader ──────────────────────────────────────────────────
PREFERRED_PROVIDER_virtual/bootloader = "u-boot-ti-staging"
UBOOT_MACHINE = "myboard_defconfig"
UBOOT_ENTRYPOINT = "0x80008000"
UBOOT_LOADADDRESS = "0x80008000"

# ── Device Tree ─────────────────────────────────────────────────
KERNEL_DEVICETREE = "ti/k3-myboard.dtb"

# ── Serial Console ──────────────────────────────────────────────
SERIAL_CONSOLES = "115200;ttyS2"      # match the UART wired to your debug port

# ── Image Format ────────────────────────────────────────────────
IMAGE_FSTYPES = "wic wic.bz2 tar.gz"
WKS_FILE = "sdimage-bootpart.wks"

# ── Extra machine features ──────────────────────────────────────
MACHINE_FEATURES = "usbhost usbgadget alsa screen"
```

---

## Step 4 — Declaring RAM in the Device Tree

The kernel learns RAM size **exclusively from the Device Tree**.

```c
// meta-myboard/recipes-kernel/linux/files/k3-myboard.dts

/dts-v1/;
#include "k3-am625.dtsi"          // include TI SoC base — provides all SoC nodes

/ {
    model = "My Custom AM625 Board";
    compatible = "mycompany,myboard", "ti,am625";

    // ── RAM Declaration ─────────────────────────────────────────
    // Format: reg = <high-addr low-addr high-size low-size>
    memory@80000000 {
        device_type = "memory";
        reg = <0x00000000 0x80000000 0x00000000 0x80000000>; // 2 GB
    };
    // For 4 GB (crosses 32-bit boundary):
    // reg = <0x00000000 0x80000000 0x00000001 0x00000000>;
};
```

### RAM size reference

| RAM | `size` hex value |
|---|---|
| 512 MB | `0x20000000` |
| 1 GB | `0x40000000` |
| 2 GB | `0x80000000` |
| 4 GB | `0x00000001 0x00000000` |

### Two RAM chips on different address ranges

```c
memory@80000000 {
    device_type = "memory";
    reg = <0x00000000 0x80000000 0x00000000 0x80000000>,  // chip 0: 2 GB at 0x80000000
          <0x00000008 0x80000000 0x00000000 0x80000000>;  // chip 1: 2 GB at high addr
};
```

---

## Step 5 — Declaring Flash Memory in the Device Tree

Flash type determines how you declare it. The kernel auto-detects size for eMMC/SD.

### eMMC (auto-detected size)

```c
&sdhci1 {
    status = "okay";
    bus-width = <8>;
    non-removable;          // marks this as eMMC, not removable SD
    mmc-ddr-1_8v;
    mmc-hs200-1_8v;
};
```

### NAND Flash (declare size + partition map)

```c
&gpmc {
    status = "okay";
    nand@0 {
        compatible = "ti,omap2-nand";
        reg = <0>;
        nand-bus-width = <16>;

        partitions {
            compatible = "fixed-partitions";
            #address-cells = <1>;
            #size-cells = <1>;

            partition@0 {
                label = "SPL";
                reg = <0x00000000 0x00200000>;  // 2 MB
            };
            partition@200000 {
                label = "u-boot";
                reg = <0x00200000 0x00400000>;  // 4 MB
            };
            partition@600000 {
                label = "kernel";
                reg = <0x00600000 0x00800000>;  // 8 MB
            };
            partition@e00000 {
                label = "rootfs";
                reg = <0x00e00000 0x0f200000>;  // remaining flash
            };
        };
    };
};
```

### SPI NOR Flash (JEDEC auto-detects chip, you declare partitions)

```c
&main_spi0 {
    status = "okay";
    flash@0 {
        compatible = "jedec,spi-nor";   // chip ID read automatically at boot
        reg = <0>;
        spi-max-frequency = <50000000>;
        #address-cells = <1>;
        #size-cells = <1>;

        partition@0 {
            label = "bootloader";
            reg = <0x000000 0x100000>;  // 1 MB
        };
        partition@100000 {
            label = "data";
            reg = <0x100000 0x700000>;  // 7 MB
        };
    };
};
```

---

## Step 6 — Enabling Peripherals in the Device Tree

Every peripheral on your board must be explicitly enabled. Disabled by default in the SoC base DTS.

```c
// ── UART (debug console) ────────────────────────────────────────
&main_uart2 {
    status = "okay";
    pinctrl-names = "default";
    pinctrl-0 = <&main_uart2_pins>;
};

// ── I2C with EEPROM and temperature sensor ──────────────────────
&main_i2c0 {
    status = "okay";
    clock-frequency = <400000>;

    eeprom@50 {
        compatible = "atmel,24c256";
        reg = <0x50>;
    };

    temp-sensor@48 {
        compatible = "national,lm75";
        reg = <0x48>;
    };
};

// ── SPI with custom sensor ──────────────────────────────────────
&main_spi0 {
    status = "okay";
    my-sensor@0 {
        compatible = "mycompany,my-sensor";  // must match driver's .compatible
        reg = <0>;
        spi-max-frequency = <1000000>;
    };
};

// ── GPIO (example: button and LED) ─────────────────────────────
/ {
    gpio-keys {
        compatible = "gpio-keys";
        button0 {
            label = "USER_BTN";
            gpios = <&main_gpio0 14 GPIO_ACTIVE_LOW>;
            linux,code = <KEY_ENTER>;
        };
    };

    leds {
        compatible = "gpio-leds";
        led0 {
            label = "USER_LED";
            gpios = <&main_gpio0 22 GPIO_ACTIVE_HIGH>;
            default-state = "off";
        };
    };
};
```

---

## Step 7 — U-Boot RAM Declaration

U-Boot runs before the kernel, so it needs its own RAM declaration in its `defconfig`:

```makefile
# meta-myboard/recipes-bsp/u-boot/files/myboard_defconfig

CONFIG_SYS_SDRAM_BASE=0x80000000
CONFIG_SYS_SDRAM_SIZE=0x80000000    # 2 GB
CONFIG_SYS_MALLOC_LEN=0x2000000     # heap (keep ~1-2% of RAM)
CONFIG_SYS_LOAD_ADDR=0x82000000     # where U-Boot loads kernel
```

Hook it in via a bbappend:

```bitbake
# meta-myboard/recipes-bsp/u-boot/u-boot-ti-staging_%.bbappend
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://myboard_defconfig \
                   file://0001-myboard-ddr-init.patch "
```

---

## Step 8 — Adding a Custom Driver

### Option A — Driver exists in kernel, just enable it

`meta-myboard/recipes-kernel/linux/files/myboard.cfg`:

```
CONFIG_SPI_SPIDEV=y
CONFIG_I2C_CHARDEV=y
CONFIG_SENSORS_LM75=y
CONFIG_MY_SENSOR=m          # build as loadable module
```

### Option B — Out-of-tree driver (separate source repo)

`meta-myboard/recipes-modules/my-driver/my-driver.bb`:

```bitbake
SUMMARY = "My custom sensor kernel module"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://LICENSE;md5=<checksum>"

inherit module                # handles cross-compilation and install automatically

SRC_URI = "git://github.com/mycompany/my-driver.git;branch=main;protocol=https"
SRCREV = "<git-commit-hash>"

S = "${WORKDIR}/git"

# No need to set CC, ARCH, CROSS_COMPILE — Yocto injects them automatically
```

### Option C — Patch an existing in-tree driver

```bitbake
# meta-myboard/recipes-kernel/linux/linux-ti-staging_%.bbappend
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " \
    file://k3-myboard.dts \
    file://myboard.cfg \
    file://0001-add-myboard-support.patch \
"

# Tell the kernel build system about your DTS file
KERNEL_DEVICETREE:append = " ti/k3-myboard.dtb"
```

---

## Step 9 — Build Your Custom Board Image

```bash
cd /home/ali/bitbake-builds/poky-master/build
source init-build-env

# Switch to your custom machine
bitbake-config-build enable-fragment machine/myboard

# Build
bitbake core-image-minimal
```

Output image:
```
tmp/deploy/images/myboard/core-image-minimal-myboard.wic.bz2
```

---

## Boot Flow Summary

```
Power on
    │
    ▼
ROM Bootloader (inside TI SoC)
    │  reads SPL from flash/SD
    ▼
SPL (Secondary Program Loader)
    │  initializes DDR using U-Boot defconfig values (RAM size/base)
    ▼
U-Boot
    │  loads kernel (Image) + Device Tree (.dtb) into RAM
    ▼
Linux Kernel
    │  reads Device Tree → discovers RAM, flash partitions, peripherals
    ▼
rootfs / your application
```

---

## Quick Reference — What to Change for Common Hardware Differences

| Hardware change | File to edit | What to change |
|---|---|---|
| More/less RAM | `k3-myboard.dts` | `memory@` → `reg` size |
| RAM on different address | `k3-myboard.dts` + `myboard_defconfig` | `reg` base + `CONFIG_SYS_SDRAM_BASE` |
| Different flash chip | `k3-myboard.dts` | partition sizes in flash node |
| Different console UART | `myboard.conf` + DTS | `SERIAL_CONSOLES` + `&uartX { status = "okay" }` |
| Extra I2C device | `k3-myboard.dts` | add child node under `&i2cX` |
| Extra SPI device | `k3-myboard.dts` | add child node under `&spiX` |
| Enable in-tree driver | `myboard.cfg` | `CONFIG_XXX=y` or `=m` |
| Add out-of-tree driver | new `my-driver.bb` | `inherit module` recipe |
| Patch kernel driver | `.patch` + `.bbappend` | `SRC_URI:append` |
| Different CPU core count | auto-detected | no change needed |
| Custom board name in `/proc` | `k3-myboard.dts` | `model = "..."` string |
