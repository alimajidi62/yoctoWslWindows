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

Open an Ubuntu WSL2 terminal and run:

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential chrpath cpio debianutils diffstat file gawk gcc git \
  iputils-ping libacl1 libcrypt-dev locales python3 python3-git \
  python3-jinja2 python3-pexpect python3-pip python3-subunit python3-websockets \
  socat texinfo unzip wget xz-utils zstd
```

---

## Step 2 — Configure Locale

Yocto requires the `en_US.UTF-8` locale. Check if it is already enabled:

```bash
locale --all-locales | grep en_US.utf8
```

If nothing is returned, enable it:

```bash
echo "en_US.UTF-8 UTF-8" | sudo tee -a /etc/locale.gen
sudo locale-gen
```

---

## Step 3 — Configure Git

```bash
git config --global user.name  "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Step 4 — Verify Tool Versions

Yocto requires minimum versions for several tools:

| Tool | Minimum Version |
|---|---|
| Git | 1.8.3.1 |
| tar | 1.28 |
| Python | 3.9.0 |
| gcc | 10.1 |
| GNU make | 4.0 |

Check your versions:

```bash
git --version
tar --version
python3 --version
gcc --version
make --version
```

Ubuntu 24.04 ships versions that satisfy all requirements.

---

## Step 5 — Get Poky (Yocto Reference Distribution)

### Option A — Using bitbake-setup (Recommended, modern approach)

```bash
# Clone the bitbake tool
git clone https://git.openembedded.org/bitbake

# Initialize a Poky build environment interactively
./bitbake/bin/bitbake-setup init
```

When prompted, select:
1. **Configuration** → `poky-master` (or a numbered release like `poky-scarthgap`)
2. **BitBake config** → `poky`
3. **Machine** → e.g. `qemux86-64` (QEMU) or your target board
4. **Distro** → `poky`

For a non-interactive setup:

```bash
./bitbake/bin/bitbake-setup init --non-interactive poky-master poky distro/poky machine/qemux86-64
```

### Option B — Manual Poky Clone (Classic approach)

```bash
git clone -b scarthgap https://git.yoctoproject.org/poky
cd poky
source oe-init-build-env build
```

---

## Step 6 — Initialize the Build Environment

```bash
# If using bitbake-setup:
source poky-master/build/init-build-env

# If using manual clone:
source oe-init-build-env build
```

This drops you into the `build/` directory with all BitBake environment
variables set.

---

## Step 7 — (Optional) Speed Up Builds with Shared State Cache

Enable the upstream sstate mirror to download pre-built artifacts:

```bash
bitbake-config-build enable-fragment core/yocto/sstate-mirror-cdn
```

---

## Step 8 — Build an Image

```bash
# Build the full Sato reference image (takes 1–6 hours on first run)
bitbake core-image-sato

# Or a minimal image for faster testing:
bitbake core-image-minimal
```

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
