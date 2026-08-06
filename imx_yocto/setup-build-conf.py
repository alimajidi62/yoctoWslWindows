#!/usr/bin/env python3
"""Write bblayers.conf and local.conf for the imx6qsabrelite Yocto build."""

import os
import pathlib

HOME = pathlib.Path.home()
BUILD_CONF = HOME / "imx6-yocto" / "build" / "conf"
BASE = HOME / "imx6-yocto"

BBLAYERS = f"""\
BBLAYERS ?= " \\
  {BASE}/poky/meta \\
  {BASE}/poky/meta-poky \\
  {BASE}/poky/meta-yocto-bsp \\
  {BASE}/meta-openembedded/meta-oe \\
  {BASE}/meta-openembedded/meta-python \\
  {BASE}/meta-openembedded/meta-networking \\
  {BASE}/meta-freescale \\
  {BASE}/meta-freescale-distro \\
"
"""

LOCAL_CONF = f"""\
MACHINE = "imx6qdlsabresd"
ACCEPT_FSL_EULA = "1"

DL_DIR = "{HOME}/yocto-downloads"
SSTATE_DIR = "{HOME}/yocto-sstate"

BB_NUMBER_THREADS = "16"
PARALLEL_MAKE = "-j16"

INHERIT += "rm_work"

IMAGE_INSTALL:append = " gcc g++ binutils make python3 python3-modules openssh-sshd"
"""

def write(path, content, label):
    path.write_text(content)
    print(f"[OK] {label} -> {path}")

write(BUILD_CONF / "bblayers.conf", BBLAYERS, "bblayers.conf")
write(BUILD_CONF / "local.conf",    LOCAL_CONF, "local.conf")

print("\nDone. Verify with:")
print("  cd ~/imx6-yocto && source poky/oe-init-build-env build")
print("  bitbake-layers show-layers")
