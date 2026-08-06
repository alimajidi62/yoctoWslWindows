# Embedded Linux / Yocto — WSL Development Workspace

This repo contains notes, scripts, and setup guides for building embedded Linux images with Yocto, running on WSL2 (Windows).

---

## Repository Structure

```
├── JestonNano/                  # Yocto build setup for NVIDIA Jetson Nano
│   ├── README.md                #   Full setup and build guide
│   ├── docs/
│   │   └── custom-board-bsp.md  #   Notes on building a custom BSP
│   └── scripts/                 #   Helper scripts for build and board setup
│       ├── add-ssh-to-image.py       # Add SSH server to a Yocto image
│       ├── chart.py                  # Utility chart/plot script
│       ├── disable-tools-sdk.py      # Disable SDK tools in build config
│       ├── fix-bashrc.sh             # Fix .bashrc for Yocto environment
│       ├── fix-extlinux.py           # Fix extlinux.conf boot entries
│       ├── fix-local-conf-build.py   # Patch local.conf build settings
│       ├── fix-rootspec.py           # Fix rootfs spec issues
│       ├── flash-sdcard.ps1          # Flash image to SD card (PowerShell)
│       ├── getconf                   # Stub getconf binary for VS Code remote SSH
│       ├── gpu_stress.py             # GPU stress test for Jetson
│       ├── hello_jetson.py           # Basic Jetson hello-world script
│       ├── make-sdcard.sh            # Create bootable SD card image
│       ├── setup-jetson-local-conf.py# Configure local.conf for Jetson target
│       ├── test_gpu.py               # GPU functionality test
│       ├── update-local-conf.py      # Update local.conf values
│       └── wslcommand.md             # WSL command reference notes
│
├── imx_yocto/                   # Yocto build setup for NXP i.MX6 Quad (QEMU)
│   └── README.md                #   Full setup guide — builds and runs in QEMU sabrelite
│
└── notpush.txt                  # Files/paths to exclude from version control
```

---

## Projects

### `JestonNano/`
Yocto-based Linux image for the **NVIDIA Jetson Nano** development board.  
Covers BSP setup, SD card flashing, VS Code remote SSH configuration, and on-board GPU testing.  
→ See [JestonNano/README.md](JestonNano/README.md)

### `imx_yocto/`
Yocto-based Linux image for **NXP i.MX6 Quad**, emulated with **QEMU** (`sabrelite` machine).  
No physical hardware required — full build and boot runs inside WSL2.  
Includes on-target GCC and Python3 for running code inside the emulator.  
→ See [imx_yocto/README.md](imx_yocto/README.md)

---

## Host Environment

- **OS:** Windows with WSL2 (Ubuntu 22.04)
- **Build system:** Yocto / OpenEmbedded (Scarthgap 5.0 LTS)
- **Emulator:** QEMU (`qemu-system-arm`)
