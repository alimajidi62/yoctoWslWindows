#!/bin/bash
DEPLOYDIR=/home/ali/bitbake-builds/poky-kirkstone/build-jetson-nano/tmp/deploy/images/jetson-nano-devkit
WORKDIR=/home/ali/jetson-flash
cd "$WORKDIR"
tar -xzf "$DEPLOYDIR/core-image-minimal-jetson-nano-devkit.tegraflash.tar.gz"
# symlink so dosdcard.sh finds the ext4 rootfs in its working directory
ln -sf "$DEPLOYDIR/core-image-minimal-jetson-nano-devkit.ext4" core-image-minimal.ext4
bash dosdcard.sh
ls -lh core-image-minimal.sdcard
