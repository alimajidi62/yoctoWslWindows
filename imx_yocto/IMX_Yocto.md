# Yocto for NXP i.MX6 Quad — QEMU Setup from Scratch

Target: **i.MX6 Quad SABRE Lite** emulated with QEMU `sabrelite` machine  
Yocto Release: **Scarthgap 5.0 LTS**  
Host: WSL2 Ubuntu 22.04

---

## Step 0 — WSL2 Disk & Swap Check

Yocto builds are large. Make sure you have enough resources before starting.

```bash
# Check free disk space — need at least 60 GB free
df -h ~

# Check available RAM + swap — need at least 8 GB total
free -h
```

> If your WSL2 virtual disk is too small, expand it from PowerShell (Windows side):
> ```powershell
> # In Windows PowerShell (not WSL)
> wsl --shutdown
> # Find your VHDX path, then:
> Resize-VHD -Path "C:\Users\<user>\AppData\Local\Packages\<Ubuntu>\LocalState\ext4.vhdx" -SizeBytes 100GB
> # Then inside WSL: sudo resize2fs /dev/sdb
> ```

---

## Step 1 — Install WSL2 Host Dependencies

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

## Step 2 — Create Project Directory Structure

```bash
# All work goes here — change the path if you prefer somewhere else
export IMX_YOCTO_BASE=$HOME/imx6-yocto
mkdir -p $IMX_YOCTO_BASE
cd $IMX_YOCTO_BASE
```

---

## Step 3 — Clone Yocto Layers (Scarthgap branch)

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

## Step 4 — Initialize the Build Environment

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

## Step 6 — Configure `local.conf`

Edit `$IMX_YOCTO_BASE/build/conf/local.conf` — add/change these key lines:

```bash
# Target machine — i.MX6 Quad SABRE Lite (matches QEMU 'sabrelite' machine)
MACHINE = "imx6qsabrelite"

# Accept NXP EULA (required to build any i.MX recipe)
ACCEPT_FSL_EULA = "1"

# Shared download cache — avoids re-downloading sources across builds
DL_DIR = "${HOME}/yocto-downloads"

# Shared state cache — speeds up rebuilds
SSTATE_DIR = "${HOME}/yocto-sstate"

# Parallel build tuning — set to number of CPU cores in WSL
BB_NUMBER_THREADS = "4"
PARALLEL_MAKE = "-j4"

# Keep tmp small — rm_work removes build artifacts after packaging
INHERIT += "rm_work"

# On-target development tools — gcc to compile C, python3 to run Python scripts
IMAGE_INSTALL:append = " gcc g++ binutils make python3 python3-modules"
```

> Check your WSL CPU count with: `nproc`  
> Adjust `BB_NUMBER_THREADS` and `PARALLEL_MAKE` to match.

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

## Step 7 — Build a Minimal Image

```bash
# Make sure you are in the build environment first
cd $IMX_YOCTO_BASE
source poky/oe-init-build-env build

# Build — this will take 2-4 hours on first run (downloads + compiles everything)
bitbake core-image-minimal
```

Build output lands in:
```
build/tmp/deploy/images/imx6qsabrelite/
```

Key files produced:
```
zImage                                          # Kernel
imx6q-sabrelite.dtb                             # Device tree blob
core-image-minimal-imx6qsabrelite.ext4          # Root filesystem
```

---

## Step 8 — Run the Image in QEMU

```bash
# Convert the ext4 image to a raw disk QEMU can use
cd $IMX_YOCTO_BASE/build/tmp/deploy/images/imx6qsabrelite

qemu-img convert -f raw -O raw \
  core-image-minimal-imx6qsabrelite.ext4 \
  rootfs.img

# Boot in QEMU — no window, serial console only
qemu-system-arm \
  -M sabrelite \
  -m 1G \
  -kernel zImage \
  -dtb imx6q-sabrelite.dtb \
  -drive file=rootfs.img,format=raw,id=sd,if=none \
  -device sdhci-pci,id=sdhci \
  -device sd-card,drive=sd \
  -append "console=ttymxc0,115200 root=/dev/mmcblk0 rootwait rw" \
  -serial stdio \
  -nographic \
  -net nic,model=virtio \
  -net user
```

> Exit QEMU with: `Ctrl+A` then `X`

---

## Step 9 — Add SSH to the Image (Optional)

To SSH into the running QEMU machine, add `openssh-server` to the image.

In `local.conf`, add:
```
IMAGE_INSTALL:append = " openssh-server"
```

Then rebuild:
```bash
bitbake core-image-minimal
```

QEMU command — add port forwarding:
```bash
-net user,hostfwd=tcp::2222-:22
```

Then from WSL:
```bash
ssh -p 2222 root@localhost
```

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
| QEMU kernel panic on boot | Verify DTB filename matches what was built in `deploy/images/` |
| `locale` errors from bitbake | Run `sudo locale-gen en_US.UTF-8` and re-source environment |
| Build hangs in WSL | Reduce `BB_NUMBER_THREADS` and `PARALLEL_MAKE` to avoid OOM |
| WSL2 networking slow downloads | Set `BB_NO_NETWORK = "0"` and check WSL DNS (`/etc/resolv.conf`) |

---

## What You Will Learn with This Setup

- Yocto layer architecture (`meta-*` layers, `bblayers.conf`)
- NXP BSP structure (`meta-freescale` — kernel config, u-boot, device trees)
- i.MX6 device tree and boot flow (U-Boot → kernel → rootfs)
- BitBake recipes (`.bb`), append files (`.bbappend`), classes (`.bbclass`)
- Image customization (`IMAGE_INSTALL`, `EXTRA_IMAGE_FEATURES`)
- Cross-compilation workflow (Yocto SDK generation with `bitbake -c populate_sdk`)
