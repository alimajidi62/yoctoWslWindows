# Yocto for NXP i.MX6 Quad — QEMU Setup from Scratch

Target: **i.MX6 Quad SABRE SD** (`imx6qdlsabresd`) emulated with QEMU `sabrelite` machine (same Cortex-A9 CPU)  
Yocto Release: **Scarthgap 5.0 LTS**  
Host: WSL2 Ubuntu 24.04

---

## Step 0 — WSL2 Disk & Swap Check ✅

Yocto builds are large. Make sure you have enough resources before starting.

```bash
# Check free disk space — need at least 60 GB free
df -h ~

# Check available RAM + swap — need at least 8 GB total
free -h
```

> **Actual results on this machine:** 938 GB free, 15 GB RAM + 4 GB swap, 22 CPU cores.

> If your WSL2 virtual disk is too small, expand it from PowerShell (Windows side):
> ```powershell
> # In Windows PowerShell (not WSL)
> wsl --shutdown
> # Find your VHDX path, then:
> Resize-VHD -Path "C:\Users\<user>\AppData\Local\Packages\<Ubuntu>\LocalState\ext4.vhdx" -SizeBytes 100GB
> # Then inside WSL: sudo resize2fs /dev/sdb
> ```

---

## Step 1 — Install WSL2 Host Dependencies ✅

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    gawk wget git diffstat unzip texinfo gcc build-essential \
    chrpath socat cpio python3 python3-pip python3-pexpect \
    xz-utils debianutils iputils-ping python3-git python3-jinja2 \
    python3-subunit zstd liblz4-tool file locales libacl1 \
    qemu-system-arm qemu-utils

# Set locale (required by Yocto)
sudo locale-gen en_US.UTF-8
sudo update-locale LANG=en_US.UTF-8
```

---

## Step 2 — Create Project Directory Structure ✅

```bash
# All work goes here — change the path if you prefer somewhere else
export IMX_YOCTO_BASE=$HOME/imx6-yocto
mkdir -p $IMX_YOCTO_BASE
cd $IMX_YOCTO_BASE
```

---

## Step 3 — Clone Yocto Layers (Scarthgap branch) ✅

```bash
cd $IMX_YOCTO_BASE

# Core Yocto (Poky = poky + meta-poky + meta-yocto-bsp)
git clone -b scarthgap https://git.yoctoproject.org/poky

# Extra OpenEmbedded layers (meta-freescale depends on some of these)
git clone -b scarthgap https://github.com/openembedded/meta-openembedded

# NXP / Freescale BSP layer (i.MX6 machine definitions, recipes, kernel)
git clone -b scarthgap https://github.com/Freescale/meta-freescale

# Freescale distro layer (optional but useful — provides fsl-framebuffer distro)
git clone -b scarthgap https://github.com/Freescale/meta-freescale-distro
```

After cloning, your directory should look like:
```
$HOME/imx6-yocto/
├── poky/
├── meta-openembedded/
├── meta-freescale/
└── meta-freescale-distro/
```

---

## Step 4 — Initialize the Build Environment ✅

```bash
cd $IMX_YOCTO_BASE

# Source the Yocto environment setup script
# This creates the 'build/' directory and sets up shell variables
source poky/oe-init-build-env build
```

> You will be placed inside `$IMX_YOCTO_BASE/build/` after this.  
> Every time you open a new terminal you must re-run this `source` command.

---

## Step 5 — Configure `bblayers.conf`

Edit `$IMX_YOCTO_BASE/build/conf/bblayers.conf` — replace its content with:

```
# bblayers.conf

BBLAYERS ?= " \
  ${HOME}/imx6-yocto/poky/meta \
  ${HOME}/imx6-yocto/poky/meta-poky \
  ${HOME}/imx6-yocto/poky/meta-yocto-bsp \
  ${HOME}/imx6-yocto/meta-openembedded/meta-oe \
  ${HOME}/imx6-yocto/meta-openembedded/meta-python \
  ${HOME}/imx6-yocto/meta-openembedded/meta-networking \
  ${HOME}/imx6-yocto/meta-freescale \
  ${HOME}/imx6-yocto/meta-freescale-distro \
"
```

> Use the full absolute path — `${HOME}` might not expand here, replace with `/home/<your-username>` if needed.

You can verify layers are found correctly with:
```bash
bitbake-layers show-layers
```

---

## Step 6 — Configure `local.conf` ✅

Handled by `setup-build-conf.py` (see Step 5). Generated content:

```bash
# imx6qsabrelite was removed from meta-freescale scarthgap; imx6qdlsabresd is the same i.MX6 Quad Cortex-A9
MACHINE = "imx6qdlsabresd"

ACCEPT_FSL_EULA = "1"

DL_DIR = "${HOME}/yocto-downloads"
SSTATE_DIR = "${HOME}/yocto-sstate"

# Set to your core count — this machine uses 16 of 22 cores
BB_NUMBER_THREADS = "16"
PARALLEL_MAKE = "-j16"

INHERIT += "rm_work"

# required — without this, Yocto locks the root account and login is impossible
IMAGE_FEATURES += "debug-tweaks"

# On-target dev tools and SSH — note: Yocto package is openssh-sshd, not openssh-server
IMAGE_INSTALL:append = " gcc g++ binutils make python3 python3-modules openssh-sshd"
```

> Check your WSL CPU count with: `nproc` and adjust the thread values in `setup-build-conf.py` before running it.

**What each package gives you inside the running QEMU:**

| Package | What you can do |
|---|---|
| `gcc` | Compile C code directly on the board: `gcc hello.c -o hello` |
| `g++` | Compile C++ code: `g++ hello.cpp -o hello` |
| `binutils` | `objdump`, `nm`, `readelf` — inspect compiled binaries |
| `make` | Run Makefiles on the board |
| `python3` | Run Python scripts: `python3 script.py` |
| `python3-modules` | Full Python standard library (os, sys, json, socket, etc.) |

> **One thing to be aware of:** `INHERIT += "rm_work"` is already set to save disk space during build, but it will remove the intermediate build files. If you see a conflict with any dev package, just remove that line temporarily.

---

## Step 7 — Build a Minimal Image ✅

```bash
cd ~/imx6-yocto
source poky/oe-init-build-env build
bitbake core-image-minimal
```

Build output lands in:
```
build/tmp-glibc/deploy/images/imx6qdlsabresd/
```

> Note: Yocto uses `tmp-glibc/` (not `tmp/`) when building with the default glibc toolchain.

Key files produced:
```
zImage                                              # Kernel (symlink)
imx6q-sabresd.dtb                                  # Device tree blob for i.MX6 Quad
core-image-minimal-imx6qdlsabresd.rootfs.wic.gz    # Full SD card image (compressed)
SPL                                                # Secondary Program Loader
u-boot.img                                         # U-Boot bootloader
```

To monitor build progress from another terminal:
```bash
tail -f ~/imx6-yocto/build/tmp-glibc/log/cooker/imx6qdlsabresd/console-latest.log
```

---

## Step 8 — Run the Image in QEMU

Use the boot script in this repo — it decompresses the WIC image and launches QEMU:

```bash
cp /mnt/c/dev/Green/linuxVM/yoctoWslWindows/imx_yocto/qemu-boot.py ~/imx6-yocto/
python3 ~/imx6-yocto/qemu-boot.py
```

Or manually:

```bash
cd ~/imx6-yocto/build/tmp-glibc/deploy/images/imx6qdlsabresd

# Decompress the WIC SD card image (only needed once)
gunzip -k core-image-minimal-imx6qdlsabresd.rootfs.wic.gz

# Boot — serial console, no display window
# Note: rootfs is on partition 2 (mmcblk0p2) inside the WIC image
qemu-system-arm \
  -M sabrelite \
  -m 1G \
  -kernel zImage \
  -dtb imx6q-sabresd.dtb \
  -drive file=core-image-minimal-imx6qdlsabresd.rootfs.wic,format=raw,id=sd,if=none \
  -device sdhci-pci,id=sdhci \
  -device sd-card,drive=sd \
  -append "console=ttymxc0,115200 root=/dev/mmcblk0p2 rootwait rw" \
  -serial stdio \
  -nographic \
  -net nic,model=virtio \
  -net user
```

> Exit QEMU with: `Ctrl+A` then `X`

---

## Step 9 — Connect via SSH into QEMU

`openssh-sshd` is already included in the image from Step 6. Add port forwarding to the QEMU command:

```bash
qemu-system-arm \
  -M sabrelite \
  -m 1G \
  -kernel zImage \
  -dtb imx6q-sabresd.dtb \
  -drive file=core-image-minimal-imx6qdlsabresd.rootfs.wic,format=raw,id=sd,if=none \
  -device sdhci-pci,id=sdhci \
  -device sd-card,drive=sd \
  -append "console=ttymxc0,115200 root=/dev/mmcblk0p2 rootwait rw" \
  -serial stdio \
  -nographic \
  -net nic,model=virtio \
  -net user,hostfwd=tcp::2222-:22
```

Once the board has booted (you see a login prompt on the serial console), open a second WSL terminal and connect:

```bash
ssh -p 2222 root@localhost
```

> Root has no password when `IMAGE_FEATURES += "debug-tweaks"` is set in `local.conf`. Press Enter when prompted for a password.

---

## Useful Commands Reference

```bash
# Re-enter build environment after a new terminal session
source ~/imx6-yocto/poky/oe-init-build-env ~/imx6-yocto/build

# Show all layers
bitbake-layers show-layers

# Show all available machines
ls meta-freescale/conf/machine/

# Search for a recipe
bitbake-layers show-recipes | grep <name>

# Inspect a recipe variables
bitbake -e <recipe-name> | grep ^<VARIABLE>

# Build only a specific recipe
bitbake <recipe-name>

# Clean a recipe (force rebuild)
bitbake -c cleanall <recipe-name>

# Check which layer provides a recipe
bitbake-layers find-recipes <recipe-name>
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ACCEPT_FSL_EULA` error | Add `ACCEPT_FSL_EULA = "1"` to `local.conf` |
| Out of disk during build | Free up space or move `DL_DIR`/`SSTATE_DIR` to a larger partition |
| `locale` errors from bitbake | Run `sudo locale-gen en_US.UTF-8` and re-source environment |
| Build hangs in WSL | Reduce `BB_NUMBER_THREADS` and `PARALLEL_MAKE` to avoid OOM |
| WSL2 networking slow downloads | Set `BB_NO_NETWORK = "0"` and check WSL DNS (`/etc/resolv.conf`) |
| `MACHINE=imx6qsabrelite is invalid` | Machine was removed in scarthgap — use `imx6qdlsabresd` instead |
| `Nothing RPROVIDES 'openssh-server'` | Wrong package name — use `openssh-sshd` in `IMAGE_INSTALL` |
| Images not found in `tmp/` | Yocto with glibc puts output in `tmp-glibc/` not `tmp/` |
| `root` login rejected / password not accepted | `debug-tweaks` missing from `local.conf` — add `IMAGE_FEATURES += "debug-tweaks"` and rebuild |

---

## QEMU Boot — Known Issues (QEMU 8.2 + sabrelite)

These issues were hit during actual boot attempts. Do not repeat them.

### ❌ Do NOT use `-serial stdio` with `-nographic`

```bash
# WRONG — causes "cannot use stdio by multiple character devices"
qemu-system-arm -M sabrelite -nographic -serial stdio ...
```

`-nographic` already routes the first UART to stdio. Adding `-serial stdio` conflicts.  
**Fix:** remove `-serial stdio` entirely when using `-nographic`.

---

### ❌ Do NOT use `sdhci-pci` — sabrelite has no PCI bus

```bash
# WRONG — causes "No 'PCI' bus found for device 'sdhci-pci'"
-device sdhci-pci,id=sdhci -device sd-card,drive=sd
```

The i.MX6 sabrelite QEMU machine has no PCI bus.  
**Fix:** use `virtio-blk-device` (see below).

---

### ❌ Do NOT use `-sd` or `if=sd`

```bash
# WRONG — causes "machine type does not support if=sd,bus=0,unit=0"
qemu-system-arm -M sabrelite -sd image.wic ...
```

QEMU 8.2 `sabrelite` dropped legacy SD card attachment via `-sd`.  
**Fix:** use `virtio-blk-device` (see below).

---

### ✅ Correct storage attachment — virtio-blk-device

The sabrelite machine exposes a `virtio-bus` (MMIO-based). Use it:

```bash
-drive file=image.wic,format=raw,if=none,id=blk0 \
-device virtio-blk-device,drive=blk0 \
-append "... root=/dev/vda2 ..."
```

**Requirement:** kernel must have `CONFIG_VIRTIO_MMIO=y` and `CONFIG_VIRTIO_BLK=y`.  
The default imx6qdlsabresd kernel does NOT have these. Enable them via `meta-custom` layer:

```bash
# Run once to create the layer and rebuild the kernel
python3 ~/imx6-yocto/add-virtio-layer.py
cd ~/imx6-yocto && source poky/oe-init-build-env build
bitbake linux-fslc
bitbake core-image-minimal
```

The `add-virtio-layer.py` script in this repo handles this automatically.

---

### ❌ `.wic.gz` is a symlink — gunzip fails

```bash
# WRONG — causes "Too many levels of symbolic links"
gunzip -k core-image-minimal-imx6qdlsabresd.rootfs.wic.gz
```

Yocto's deploy directory uses symlinks pointing to timestamped files.  
**Fix:** resolve the real file before decompressing, or use the `qemu-boot.py` script which handles this automatically.

---

## What You Will Learn with This Setup

- Yocto layer architecture (`meta-*` layers, `bblayers.conf`)
- NXP BSP structure (`meta-freescale` — kernel config, u-boot, device trees)
- i.MX6 device tree and boot flow (U-Boot → kernel → rootfs)
- BitBake recipes (`.bb`), append files (`.bbappend`), classes (`.bbclass`)
- Image customization (`IMAGE_INSTALL`, `EXTRA_IMAGE_FEATURES`)
- Cross-compilation workflow (Yocto SDK generation with `bitbake -c populate_sdk`)
