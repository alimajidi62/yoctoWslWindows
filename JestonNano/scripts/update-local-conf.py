f = "/home/ali/bitbake-builds/poky-kirkstone/build-jetson-nano/conf/local.conf"

additions = """
# ---- Custom additions (baked features) -------------------------------------

# 1) Override package format to IPK so opkg works on-device
PACKAGE_CLASSES = "package_ipk"

# 2) Install opkg package manager into the image
EXTRA_IMAGE_FEATURES += "package-management"

# 3) GCC + build tools on-device (gcc, g++, make, binutils, pkg-config)
EXTRA_IMAGE_FEATURES += "tools-sdk"

# 4) Python 3 with pip and standard library modules
IMAGE_INSTALL:append = " python3 python3-pip python3-misc python3-modules"

# 5a) VS Code SSH prerequisites baked in (getconf, libstdc++, libgcc_s)
IMAGE_INSTALL:append = " glibc-utils gcc-runtime"

# 5b) Tegra GPU user-space libraries (provides libcuda.so.1 for CUDA)
IMAGE_INSTALL:append = " tegra-libraries"
"""

content = open(f).read()

# Avoid appending twice if script is re-run
if "Custom additions (baked features)" in content:
    print("Already updated — no changes made.")
else:
    with open(f, "a") as fh:
        fh.write(additions)
    print("local.conf updated. Tail:")
    lines = open(f).readlines()
    print("".join(lines[-22:]))
