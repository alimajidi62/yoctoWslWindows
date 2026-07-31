# Yocto Project Build Setup on Ubuntu 24.04 (WSL2)

This guide covers everything needed to build a Yocto Project image inside
Ubuntu 24.04 running on Windows Subsystem for Linux 2 (WSL2).

---

## Prerequisites

### Windows Host Requirements

| Requirement | Minimum |
|---|---|
| Windows Version | Windows 10 (21H2) or Windows 11 |
| WSL Version | WSL2 |
| Disk Space (WSL volume) | **140 GB** free (more is better) |
| RAM | **32 GB** (more = faster builds) |
| CPU Cores | 4+ (more cores = faster builds) |

> **Note:** WSL2 is confirmed installed and running on this machine
> (`Ubuntu-24.04`, WSL2, Running).

### Increase WSL2 Memory/CPU (Recommended)

Create or edit `%USERPROFILE%\.wslconfig` on Windows:

```ini
[wsl2]
memory=16GB       # adjust to ~50% of your physical RAM
processors=8      # adjust to your CPU core count
swap=8GB
```

Then restart WSL:

```powershell
wsl --shutdown
wsl
```

---

## Step 1 — Install Required Host Packages

> **Status: DONE** — All packages were installed on 2026-07-30 inside `Ubuntu-24.04` (WSL2).

The following command was run from PowerShell:

```powershell
wsl -- sudo apt-get update
wsl -- sudo apt-get install -y build-essential chrpath cpio debianutils diffstat file gawk gcc git \
  iputils-ping libacl1 libcrypt-dev locales python3 python3-git \
  python3-jinja2 python3-pexpect python3-pip python3-subunit python3-websockets \
  socat texinfo unzip wget xz-utils zstd
```

### Verified Installed Packages

| Package | Installed Version | Status |
|---|---|---|
| `build-essential` | 12.10ubuntu1 | ✅ |
| `chrpath` | 0.16-2build1 | ✅ |
| `cpio` | 2.15+dfsg-1ubuntu2 | ✅ |
| `gawk` | 5.2.1-2ubuntu0.1 | ✅ |
| `gcc` | 13.2.0 (v13) | ✅ |
| `git` | 2.43.0-1ubuntu7.3 | ✅ |
| `python3` | 3.12.3-0ubuntu2.1 | ✅ |
| `python3-git` | 3.1.37-3 | ✅ |
| `python3-jinja2` | 3.1.2-1ubuntu1.3 | ✅ |
| `python3-pexpect` | 4.9-2 | ✅ |
| `python3-websockets` | 10.4-1 | ✅ |
| `socat` | 1.8.0.0-4ubuntu0.1 | ✅ |
| `texinfo` | 7.1-3build2 | ✅ |
| `zstd` | 1.5.5+dfsg2-2build1.1 | ✅ |

All versions exceed the Yocto Project minimum requirements.

### WSL2 Storage Location

The Ubuntu-24.04 virtual disk (`ext4.vhdx`) is stored at:

```
C:\Users\220666118\AppData\Local\wsl\{44a99a32-e46e-4815-9c1a-881d2176880c}\ext4.vhdx
```

Keep all Yocto build files **inside the WSL filesystem** (e.g. `~/yocto/`), not under `/mnt/c/`.

---

## Step 2 — Configure Locale

> **Status: DONE** — `en_US.UTF-8` locale enabled on 2026-07-30.

```bash
echo 'en_US.UTF-8 UTF-8' | sudo tee -a /etc/locale.gen
sudo locale-gen
# Output: en_US.UTF-8... done
```

Verified with:
```bash
locale --all-locales | grep en_US.utf8
# Output: en_US.utf8
```

---

## Step 3 — Configure Git

> **Status: DONE** — Git configured on 2026-07-30.

```bash
git config --global user.name  "ali majidi"
git config --global user.email "a.m.majidi.62@gmoil.com"
```

---

## Step 4 — Verify Tool Versions

> **Status: DONE** — All tools verified on 2026-07-30.

| Tool | Minimum Required | Installed | Status |
|---|---|---|---|
| Git | 1.8.3.1 | **2.43.0** | ✅ |
| tar | 1.28 | **1.35** | ✅ |
| Python | 3.9.0 | **3.12.3** | ✅ |
| gcc | 10.1 | **13.3.0** | ✅ |
| GNU make | 4.0 | **4.3** | ✅ |

---

## Step 5 — Get Poky + Raspberry Pi 4 BSP

> **Status: DONE** — Completed on 2026-07-30.

### 5a — Clone bitbake and init Poky

```bash
cd ~
git clone https://git.openembedded.org/bitbake
./bitbake/bin/bitbake-setup init --non-interactive poky-master poky distro/poky machine/qemux86-64
```

Build directory: `/home/ali/bitbake-builds/poky-master/build`

### 5b — Add meta-raspberrypi BSP layer

```bash
git clone -b master https://git.yoctoproject.org/meta-raspberrypi \
  /home/ali/bitbake-builds/poky-master/layers/meta-raspberrypi

cd /home/ali/bitbake-builds/poky-master/build
source init-build-env
bitbake-layers add-layer ../layers/meta-raspberrypi
```

### 5c — Switch target machine to Raspberry Pi 4 (64-bit)

```bash
bitbake-config-build enable-fragment machine/raspberrypi4-64
```

### 5d — Accept Synaptics non-free firmware license

Added to `conf/local.conf`:
```
LICENSE_FLAGS_ACCEPTED = "synaptics-killswitch"
```

### Active Configuration (verified)

| Setting | Value |
|---|---|
| DISTRO | `poky` |
| MACHINE | `raspberrypi4-64` ✅ |
| BSP layer | `meta-raspberrypi` ✅ |
| License | `synaptics-killswitch` accepted ✅ |

---

## Step 6 — Initialize the Build Environment

> **Status: DONE** — Environment sourced as part of Step 5.

```bash
source /home/ali/bitbake-builds/poky-master/build/init-build-env
```

---

## Step 7 — (Optional) Speed Up Builds with Shared State Cache

Enable the upstream sstate mirror to download pre-built artifacts:

```bash
bitbake-config-build enable-fragment core/yocto/sstate-mirror-cdn
```

---

## Step 8 — Build an Image

> **Status: DONE** — `core-image-minimal` built successfully on 2026-07-31 (4022 tasks).

```bash
cd /home/ali/bitbake-builds/poky-master/build
source init-build-env
bitbake core-image-minimal 2>&1 | tee ~/yocto-build.log
```

Monitor progress in a second WSL terminal:
```bash
tail -f ~/yocto-build.log
```

### Known Issue — `sed` QA buildpaths failure

**Error:**
```
ERROR: sed-4.10-r0 do_package_qa: QA Issue: File /usr/share/info/sed.info
contains a reference to the build host HOME directory.
```

**Cause:** `sed`'s upstream documentation contains the string `/home/ali` as a literal example — it matches the WSL username by coincidence. Not a real host-path leak.

**Fix** — add to `conf/local.conf` before building:
```bitbake
OEQA_BUILDPATHS_SKIP = "/home/ali"
```

After adding the fix, resume with `bitbake core-image-minimal` — all previously completed tasks are cached and will not re-run.

### Build Output — Raspberry Pi 4 (64-bit)

Build completed **2026-07-31** — 4076 tasks, 0 errors.

```
~/bitbake-builds/poky-master/build/tmp/deploy/images/raspberrypi4-64/
```

| File | Size | Purpose |
|---|---|---|
| `core-image-minimal-raspberrypi4-64.rootfs-*.wic.bz2` | 29 MB | **Flash this to SD card** |
| `core-image-minimal-raspberrypi4-64.rootfs-*.wic.bmap` | 3 KB | Block map for fast flashing with `bmaptool` |
| `core-image-minimal-raspberrypi4-64.rootfs-*.ext3` | 28 MB | Raw ext3 rootfs partition |
| `Image-*-raspberrypi4-64-*.bin` | 26 MB | Kernel image |
| `bcm2711-rpi-4-b.dtb` | 56 KB | Device Tree for RPi 4B |
| `bcm2711-rpi-cm4.dtb` | 56 KB | Device Tree for Compute Module 4 |
| `*.dtbo` | various | Device Tree overlays |

### Flash to SD Card

From Linux/WSL:
```bash
# Decompress first
bzip2 -d core-image-minimal-raspberrypi4-64.rootfs-*.wic.bz2

# Flash (replace /dev/sdX with your SD card)
sudo dd if=core-image-minimal-raspberrypi4-64.rootfs-*.wic of=/dev/sdX bs=4M status=progress

# Or faster with bmaptool:
sudo bmaptool copy core-image-minimal-raspberrypi4-64.rootfs-*.wic.bz2 /dev/sdX
```

From Windows, use **Raspberry Pi Imager** or **balenaEtcher** and point it at the `.wic.bz2` file.
---

## Step 9 — Run the Image in QEMU

```bash
runqemu snapshot
```

Exit QEMU with `Ctrl-C` or the shutdown icon.

---

## Adding a BSP Layer for Real Hardware (Example: Raspberry Pi)

```bash
# Clone the BSP layer next to other layers
git clone -b wrynose https://git.yoctoproject.org/meta-raspberrypi ../layers/meta-raspberrypi

# Register it with BitBake
bitbake-layers add-layer ../layers/meta-raspberrypi

# Switch the target machine
bitbake-config-build enable-fragment machine/raspberrypi5

# Accept non-free Synaptics firmware license (required for RPi)
echo 'LICENSE_FLAGS_ACCEPTED = "synaptics-killswitch"' >> conf/local.conf

# Build
bitbake core-image-sato
```

---

## WSL2-Specific Notes

| Topic | Detail |
|---|---|
| Filesystem | Keep all build files **inside** the WSL2 filesystem (`~/`) — not on `/mnt/c/`. Cross-filesystem I/O is very slow and can cause build failures. |
| Disk growth | The WSL2 virtual disk (`ext4.vhdx`) grows automatically but does not shrink. Monitor space with `df -h`. |
| Path length | Windows has a 260-character path limit; WSL2 builds are not affected inside the Linux filesystem. |
| Proxy | If behind a corporate proxy, export `http_proxy` / `https_proxy` before building. |
| Validation | Yocto officially supports WSL2 but does not validate every release against it. Most builds work without issues. |

---

## Disk Space Tips

To conserve disk space during or after a build:

```bash
# Remove work directories after a successful build
bitbake -c cleanall <recipe-name>

# Or set INHERIT in local.conf to auto-clean
echo 'INHERIT += "rm_work"' >> conf/local.conf
```

---

## Useful References

- [Yocto Project Quick Build](https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html)
- [System Requirements](https://docs.yoctoproject.org/ref-manual/system-requirements.html)
- [WSL2 Setup Guide](https://docs.yoctoproject.org/dev-manual/start.html#setting-up-to-use-windows-subsystem-for-linux-wsl-2)
- [Layer Index](https://layers.openembedded.org/)
- [Yocto Project Wiki](https://wiki.yoctoproject.org/wiki)
