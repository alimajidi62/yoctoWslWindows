#!/usr/bin/env python3
"""Boot the i.MX6 Quad SABRE SD Yocto image in QEMU sabrelite machine (initramfs)."""

import os
import pathlib
import sys

DEPLOY = pathlib.Path.home() / "imx6-yocto/build/tmp-glibc/deploy/images/imx6qdlsabresd"
KERNEL = DEPLOY / "zImage"
DTB    = DEPLOY / "imx6q-sabresd.dtb"
INITRD = DEPLOY / "core-image-minimal-imx6qdlsabresd.rootfs.cpio.gz"

SSH_PORT = 2222


def check_files():
    missing = [f for f in [KERNEL, DTB, INITRD] if not f.exists()]
    if missing:
        print("ERROR: Missing build output files:")
        for f in missing:
            print(f"  {f}")
        print("Run: bitbake core-image-minimal")
        sys.exit(1)
    print(f"[OK] kernel : {KERNEL.name}")
    print(f"[OK] dtb    : {DTB.name}")
    print(f"[OK] initrd : {INITRD.resolve().name}")


def boot(ssh=False):
    # resolve symlinks — QEMU needs real file paths
    initrd_path = INITRD.resolve()
    net_args = "user,hostfwd=tcp::2222-:22" if ssh else "user"
    # initramfs: rootfs lives entirely in RAM, no block device needed
    cmd = [
        "qemu-system-arm",
        "-M", "sabrelite",
        "-m", "1G",
        "-kernel", str(KERNEL),
        "-dtb", str(DTB),
        "-initrd", str(initrd_path),
        "-append", "console=ttymxc0,115200 root=/dev/ram rw",
        "-nographic",
        "-net", "nic,model=virtio",
        "-net", net_args,
    ]
    if ssh:
        print(f"[INFO] SSH forwarding on: ssh -p {SSH_PORT} root@localhost")
    print("[INFO] Exit QEMU with: Ctrl+A then X\n")
    print("Running:", " ".join(cmd), "\n")
    os.execvp("qemu-system-arm", cmd)


if __name__ == "__main__":
    ssh_mode = "--ssh" in sys.argv
    check_files()
    boot(ssh=ssh_mode)
