f = "/mnt/boot/extlinux/extlinux.conf"
content = open(f).read()
content = content.replace("mmcblk0p${distro_bootpart}", "mmcblk0p1")
open(f, "w").write(content)
print(open(f).read())
