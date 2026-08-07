#!/usr/bin/env python3
"""
Create meta-custom layer with a kernel config fragment that enables
CONFIG_VIRTIO_MMIO and CONFIG_VIRTIO_BLK, then update bblayers.conf.
Rebuilding just the kernel afterwards: bitbake linux-fslc
"""

import pathlib
import sys

HOME  = pathlib.Path.home()
BASE  = HOME / "imx6-yocto"
LAYER = BASE / "meta-custom"

# ── file content ────────────────────────────────────────────────────────────

LAYER_CONF = """\
BBPATH .= ":${LAYERDIR}"
BBFILES += "${LAYERDIR}/recipes-*/*/*.bb \\
            ${LAYERDIR}/recipes-*/*/*.bbappend"
BBFILE_COLLECTIONS += "custom"
BBFILE_PATTERN_custom = "^${LAYERDIR}/"
BBFILE_PRIORITY_custom = "10"
LAYERVERSION_custom = "1"
LAYERDEPENDS_custom = "core"
LAYERSERIES_COMPAT_custom = "scarthgap"
"""

BBAPPEND = """\
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://virtio-mmio.cfg"
"""

# Enable virtio MMIO transport + block device so QEMU virtio-blk-device works
KERNEL_CFG = """\
CONFIG_VIRTIO=y
CONFIG_VIRTIO_MMIO=y
CONFIG_VIRTIO_MMIO_CMDLINE_DEVICES=y
CONFIG_VIRTIO_BLK=y
CONFIG_VIRTIO_NET=y
"""

# ── helpers ─────────────────────────────────────────────────────────────────

def write(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"[OK] {path.relative_to(HOME)}")

def add_layer_to_bblayers(bblayers: pathlib.Path, layer_path: pathlib.Path):
    text = bblayers.read_text()
    marker = str(layer_path)
    if marker in text:
        print(f"[SKIP] meta-custom already in bblayers.conf")
        return
    # insert before closing quote
    text = text.rstrip()
    if text.endswith('"'):
        text = text[:-1] + f"  {marker} \\\n\""
    else:
        text += f"\n  {marker} \\\n"
    bblayers.write_text(text)
    print(f"[OK] Added meta-custom to bblayers.conf")

# ── main ────────────────────────────────────────────────────────────────────

write(LAYER / "conf" / "layer.conf",
      LAYER_CONF)

write(LAYER / "recipes-kernel" / "linux" / "linux-fslc_%.bbappend",
      BBAPPEND)

write(LAYER / "recipes-kernel" / "linux" / "files" / "virtio-mmio.cfg",
      KERNEL_CFG)

bblayers = BASE / "build" / "conf" / "bblayers.conf"
add_layer_to_bblayers(bblayers, LAYER)

print()
print("Done. Now rebuild the kernel and image:")
print("  cd ~/imx6-yocto && source poky/oe-init-build-env build")
print("  bitbake linux-fslc          # rebuild kernel only (~20-30 min)")
print("  bitbake core-image-minimal  # repackage image")
