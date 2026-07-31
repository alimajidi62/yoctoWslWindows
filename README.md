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
C:\Users\###\AppData\Local\wsl\{###}\ext4.vhdx
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
git config --global user.name  "### ###"
git config --global user.email "###@###.com"
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

Build directory: `/home/###/bitbake-builds/poky-master/build`

### 5b — Add meta-raspberrypi BSP layer

```bash
git clone -b master https://git.yoctoproject.org/meta-raspberrypi \
  /home/###/bitbake-builds/poky-master/layers/meta-raspberrypi

cd /home/###/bitbake-builds/poky-master/build
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
source /home/###/bitbake-builds/poky-master/build/init-build-env
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
cd /home/###/bitbake-builds/poky-master/build
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

**Cause:** `sed`'s upstream documentation contains the string `/home/###` as a literal example — it matches the WSL username by coincidence. Not a real host-path leak.

**Fix** — add to `conf/local.conf` before building:
```bitbake
OEQA_BUILDPATHS_SKIP = "/home/###"
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

## Step 9 — Flash and Run on Raspberry Pi 4

### Hardware Required

| Item | Notes |
|---|---|
| microSD card | 4 GB minimum, Class 10 / A1 recommended |
| microSD USB reader | For your PC |
| Raspberry Pi 4B | Any RAM variant |
| USB-C power supply | 5V / 3A |
| HDMI cable + monitor | **Or** USB-to-UART adapter (3.3V) for serial console |

---

### Flash the SD Card

**Option A — balenaEtcher (easiest, Windows)**
1. Download from [etcher.balena.io](https://etcher.balena.io)
2. Flash from file → select `images/core-image-minimal-raspberrypi4-64.rootfs.wic.bz2`
3. Select SD card → Flash (decompresses automatically)

**Option B — Raspberry Pi Imager (Windows)**
1. Download from [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Choose OS → **Use custom** → select the `.wic.bz2` file
3. Select SD card → Write

**Option C — WSL command line**
```bash
# Find your SD card device first (check sizes carefully, NOT sda = system disk)
lsblk

# Flash (replace sdX with your SD card device)
bzip2 -dc /mnt/c/dev/Green/linuxVM/yoctoWslWindows/images/core-image-minimal-raspberrypi4-64.rootfs.wic.bz2 \
  | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
```

---

### What the WIC Image Contains

The `.wic` image creates two partitions on the SD card automatically:

```
SD Card
├── Partition 1 (FAT32, ~50 MB)  — Boot partition
│   ├── start4.elf               — RPi GPU firmware (runs before kernel)
│   ├── bcm2711-rpi-4-b.dtb      — Device Tree
│   ├── Image                    — Linux kernel (6.18)
│   └── config.txt               — Boot configuration
└── Partition 2 (ext3, ~28 MB)   — Root filesystem
    └── /bin /lib /etc /home ...  — Yocto rootfs
```

No separate bootloader programming step is needed — everything is included.

---

### First Boot

1. Insert SD card into RPi4 (slot on underside of board)
2. Connect HDMI **or** UART serial adapter
3. Connect USB-C power — board boots immediately

**Via HDMI + keyboard** — login prompt appears on screen:
```
raspberrypi4-64 login: root
Password: (none — just press Enter)
```

**Via UART serial console** — connect a 3.3V USB-UART adapter to the GPIO header:

```
RPi 4 GPIO Header        USB-UART Adapter
Pin 6  (GND)      ──────  GND
Pin 8  (TX/GPIO14)──────  RX
Pin 10 (RX/GPIO15)──────  TX
                          (do NOT connect 5V/3.3V power pins)
```

Open in PuTTY on Windows: **Serial → COM port → 115200 baud**

---

### After Login

```bash
uname -a          # verify kernel version (should show aarch64 6.18.x)
df -h             # check disk space
ip addr           # check network interfaces
```

---

### Boot Flow Summary

```
Power on
    │
    ▼
RPi firmware (start4.elf) — reads SD card boot partition
    │
    ▼
Linux kernel + Device Tree loaded
    │
    ▼
Yocto rootfs mounted
    │
    ▼
Login as root (no password)
```

---

## Jetson Nano Developer Kit Build (NVIDIA Tegra X1)

> **Board:** NVIDIA Jetson Nano Developer Kit B01 (945-13450-0000-100)
> **SD Card:** SanDisk Ultra 32 GB A1 microSD
> **Build started:** 2026-07-31

The original Jetson Nano uses the **Tegra X1 (T210)** SoC running L4T 32.7.x.
This requires a separate Yocto stack (`kirkstone` release) because `meta-tegra` master
only supports newer Orin-based Jetson boards.

### Why a Separate Build Directory

| | RPi4 build | Jetson Nano build |
|---|---|---|
| Poky branch | `master` | `kirkstone` |
| meta-tegra branch | — | `kirkstone-l4t-r32.7.x` |
| Build dir | `poky-master/build` | `poky-kirkstone/build-jetson-nano` |
| Machine | `raspberrypi4-64` | `jetson-nano-devkit` |
| Architecture | Cortex-A72 (aarch64) | Cortex-A57 (aarch64) |

### Setup Steps Performed

```bash
# 1 — Clone Poky kirkstone
git clone -b kirkstone https://git.yoctoproject.org/poky \
  ~/bitbake-builds/poky-kirkstone

# 2 — Clone BSP layers on kirkstone
git clone -b kirkstone \
  https://github.com/openembedded/meta-openembedded \
  ~/bitbake-builds/poky-kirkstone/layers/meta-openembedded

git clone https://github.com/OE4T/meta-tegra \
  ~/bitbake-builds/poky-kirkstone/layers/meta-tegra
# then switch to the branch that supports the original Nano:
git -C ~/bitbake-builds/poky-kirkstone/layers/meta-tegra \
  checkout kirkstone-l4t-r32.7.x

# 3 — Initialize build environment
cd ~/bitbake-builds/poky-kirkstone
source oe-init-build-env build-jetson-nano

# 4 — Register layers
bitbake-layers add-layer \
  /home/###/bitbake-builds/poky-kirkstone/layers/meta-openembedded/meta-oe \
  /home/###/bitbake-builds/poky-kirkstone/layers/meta-openembedded/meta-python \
  /home/###/bitbake-builds/poky-kirkstone/layers/meta-openembedded/meta-networking \
  /home/###/bitbake-builds/poky-kirkstone/layers/meta-openembedded/meta-filesystems \
  /home/###/bitbake-builds/poky-kirkstone/layers/meta-tegra
```

### local.conf Settings

```bitbake
MACHINE = "jetson-nano-devkit"
IMAGE_CLASSES += "image_types_tegra"
LICENSE_FLAGS_ACCEPTED = "commercial"
OEQA_BUILDPATHS_SKIP = "/home/###"
IMAGE_INSTALL:append = " openssh openssh-sshd openssh-sftp-server"
EXTRA_IMAGE_FEATURES += "ssh-server-openssh debug-tweaks"

# CRITICAL: override the machine conf's partition variable so CBoot gets a
# literal device path — CBoot does not expand ${distro_bootpart} like U-Boot does.
KERNEL_ROOTSPEC_DEFAULT:forcevariable = "mmcblk0p1"
```

> **Why `:forcevariable`?** In Yocto, `local.conf` is parsed *before* machine
> conf. A plain `=` in local.conf is overwritten by a later `=` in
> `jetson-nano-devkit.conf`. The `:forcevariable` override has the highest
> priority and cannot be overwritten by any other conf file.

### Extra Package Required

```bash
# lz4c is needed by meta-tegra but not in the standard Yocto host requirements
sudo apt-get install -y liblz4-tool
```

### Build Command

> **Status: DONE** — Built on 2026-07-31, 3598 tasks, 0 errors.
> OpenSSH 8.9p1 included. Boot root device fix applied.

```bash
cd ~/bitbake-builds/poky-kirkstone
source oe-init-build-env build-jetson-nano
bitbake core-image-minimal 2>&1 | tee ~/yocto-jetson-build.log
```

> **Lesson learned:** Do not add `IMAGE_INSTALL:append` or `EXTRA_IMAGE_FEATURES`
> for packages that have not been compiled yet — DNF will fail at `do_rootfs`.
> Always let a base build complete first, then add packages and rebuild.

### Build Output

```
~/bitbake-builds/poky-kirkstone/build-jetson-nano/tmp/deploy/images/jetson-nano-devkit/
├── core-image-minimal-jetson-nano-devkit-*.tegraflash.tar.gz  ← flash package (44 MB)
├── core-image-minimal-jetson-nano-devkit-*.rootfs.ext4        ← rootfs image
├── extlinux.conf                                              ← boot config (verify this!)
├── Image--4.9.337+git*-jetson-nano-devkit-*.bin               ← kernel (37 MB)
├── tegra210-p3448-0000-p3449-0000-a02-*.dtb                   ← DTB for Nano A02
└── tegra210-p3448-0000-p3449-0000-b00-*.dtb                   ← DTB for Nano B01 ← yours
```

### Verify extlinux.conf Before Flashing

Always confirm the APPEND line contains a literal partition number, not `${distro_bootpart}`:

```bash
cat ~/bitbake-builds/poky-kirkstone/build-jetson-nano/tmp/deploy/images/jetson-nano-devkit/extlinux.conf
# Expected:
# APPEND ${cbootargs} root=/dev/mmcblk0p1 rw rootwait ${bootargs}
#                                       ^^— must be "1", not "${distro_bootpart}"
```

If it still shows `${distro_bootpart}`, the `u-boot-tegra` recipe was cached.
Force a rebuild:

```bash
source oe-init-build-env build-jetson-nano
bitbake u-boot-tegra -c cleansstate
bitbake core-image-minimal
```

### Create the SD Card Image

```bash
# Extract the tegraflash package into a working directory
mkdir -p ~/jetson-flash
tar xzf ~/bitbake-builds/poky-kirkstone/build-jetson-nano/tmp/deploy/images/jetson-nano-devkit/core-image-minimal-jetson-nano-devkit-*.tegraflash.tar.gz \
  -C ~/jetson-flash

# Generate the .sdcard image (writes ext4 rootfs into a GPT disk image)
cd ~/jetson-flash
bash dosdcard.sh
# Output: core-image-minimal.sdcard (~15 GB)

# Copy to Windows for flashing
cp ~/jetson-flash/core-image-minimal.sdcard \
  /mnt/c/dev/Green/linuxVM/yoctoWslWindows/images/jetson-nano/core-image-minimal.sdcard
```

### Flash to SD Card (Windows — admin PowerShell)

`wsl --mount` is blocked by company policy, so flashing is done directly from
Windows using the .NET FileStream API. Run in **admin PowerShell**:

```powershell
# Check disk number first — Disk 1 should be your SD card (~29.7 GB, Realtek PCIE CardReader)
Get-Disk | Select-Object Number, FriendlyName, Size, BusType

Set-Disk -Number 1 -IsOffline $true
$src = [System.IO.File]::OpenRead("C:\dev\Green\linuxVM\yoctoWslWindows\images\jetson-nano\core-image-minimal.sdcard")
$dst = [System.IO.File]::Open("\\.\PhysicalDrive1", [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
$buf = New-Object byte[] 4194304
$written = 0
while (($read = $src.Read($buf, 0, $buf.Length)) -gt 0) {
    $dst.Write($buf, 0, $read)
    $written += $read
    Write-Host -NoNewline "`rWritten: $([math]::Round($written/1GB,2)) GB   "
}
$dst.Flush(); $dst.Close(); $src.Close()
Set-Disk -Number 1 -IsOffline $false
Write-Host "`nDone - SD card ready"
```

This writes ~14.75 GB at ~150 MB/s. Takes about 2 minutes.

> **Note:** The Jetson Nano uses NVIDIA's CBoot bootloader stored in the module's
> internal eMMC. The SD card only holds the kernel and rootfs (single GPT
> partition `APP` = `/dev/mmcblk0p1`). No bootloader flashing is needed.

### SD Card Slot Location

The microSD slot is on the **underside** of the carrier board, directly below
the Jetson module. Insert the card with contacts facing the board (label facing down).

### Boot Sequence

```
Power on
    │
    ▼
CBoot (NVIDIA bootloader in internal eMMC)
    │  reads /boot/extlinux/extlinux.conf from SD card APP partition
    │  expands ${cbootargs} → hardware-specific params (tegraid, ddr, etc.)
    │  passes root=/dev/mmcblk0p1 to kernel
    ▼
Linux kernel 4.9.337-l4t-r32.7.6 (aarch64)
    │
    ▼
EXT4-fs mounts /dev/mmcblk0p1 as rootfs
    │
    ▼
Yocto rootfs — login: root / password: (none)
```

### Boot Troubleshooting — Root Mount Failure

**Symptom:** Board shows CBoot output on HDMI then goes to boot loop. Kernel
panics with `VFS: Unable to mount root fs`.

**Root cause:** `meta-tegra` kirkstone generates `extlinux.conf` with:
```
APPEND ${cbootargs} root=/dev/mmcblk0p${distro_bootpart} ...
```
CBoot only expands `${cbootargs}`. It does **not** expand `${distro_bootpart}`
(a U-Boot environment variable). The kernel receives `root=/dev/mmcblk0p` with
no partition number — mount fails.

**Fix:** Add to `local.conf`:
```bitbake
KERNEL_ROOTSPEC_DEFAULT:forcevariable = "mmcblk0p1"
```
Then force-rebuild the recipe that generates extlinux.conf and reflash.

### Headless SSH Access

The image includes **OpenSSH 8.9p1** with `debug-tweaks` (no root password).

1. Connect Ethernet to your router (192.168.0.x network)
2. Power on — board gets DHCP. Previous lease: `192.168.0.204`
3. Find IP from Windows:
   ```powershell
   # Quick ARP scan
   1..254 | ForEach-Object { $null = ping -n 1 -w 300 "192.168.0.$_" }
   arp -a | Select-String "dynamic"
   ```
4. SSH in:
   ```powershell
   ssh root@192.168.0.204    # no password
   ```

### Installing Python 3 (live, no reflash)

The minimal image has no package manager. Install a standalone Python binary:

```bash
# On the Windows/WSL host — download and SCP to board
wsl -- bash -c "wget -q -O ~/python3.tar.gz \
  https://github.com/indygreg/python-build-standalone/releases/download/20241016/cpython-3.12.7+20241016-aarch64-unknown-linux-gnu-install_only.tar.gz \
  && scp ~/python3.tar.gz root@192.168.0.204:/opt/"

# On the board (via SSH) — extract and symlink
ssh root@192.168.0.204 "cd /opt && tar xzf python3.tar.gz && rm python3.tar.gz"
ssh root@192.168.0.204 "ln -sf /opt/python/bin/python3 /usr/bin/python3 \
  && ln -sf /opt/python/bin/python3.12 /usr/bin/python3.12 \
  && ln -sf /opt/python/bin/pip3 /usr/bin/pip3"

# Verify
ssh root@192.168.0.204 "python3 --version && pip3 --version"
# Python 3.12.7
# pip 24.1.2
```

Files survive reboot — stored on the SD card's ext4 rootfs at `/opt/python/`.

### Installing Packages on a Minimal Yocto Image

| Method | How | When to use |
|---|---|---|
| Bake into image | Add to `IMAGE_INSTALL:append` in `local.conf`, rebuild + reflash | Production / permanent |
| opkg (live) | Add `EXTRA_IMAGE_FEATURES += "package-management"` + rebuild once; then `opkg install <pkg>` on board | Development iteration |
| SCP binary | Build/download on host, copy with `scp` | One-off, no reflash |

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

Yocto builds are large. After a successful build the biggest consumer is `tmp/work`:

```
tmp/work      ~42 GB   ← safe to delete after build (sources + intermediate artifacts)
sstate-cache  ~4 GB    ← keep (future rebuilds use this instead of recompiling)
tmp/deploy    ~2.5 GB  ← keep (your final images)
tmp/cache     ~244 MB  ← keep (dependency cache)
```

```bash
# Delete work dirs after a successful build — sstate-cache means next rebuild is still fast
rm -rf ~/bitbake-builds/poky-kirkstone/build-jetson-nano/tmp/work

# Or auto-clean during builds (adds some overhead per-task)
echo 'INHERIT += "rm_work"' >> conf/local.conf
```

The WSL2 `ext4.vhdx` grows but does not automatically shrink on Windows.
To reclaim space on the Windows filesystem after cleanup, run in **admin PowerShell**:

```powershell
wsl --shutdown
Optimize-VHD -Path "C:\Users\###\AppData\Local\wsl\{###}\ext4.vhdx" -Mode Full
```

---

## Useful References

- [Yocto Project Quick Build](https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html)
- [System Requirements](https://docs.yoctoproject.org/ref-manual/system-requirements.html)
- [WSL2 Setup Guide](https://docs.yoctoproject.org/dev-manual/start.html#setting-up-to-use-windows-subsystem-for-linux-wsl-2)
- [Layer Index](https://layers.openembedded.org/)
- [Yocto Project Wiki](https://wiki.yoctoproject.org/wiki)
