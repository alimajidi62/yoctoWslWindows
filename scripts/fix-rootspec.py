f = "/home/ali/bitbake-builds/poky-kirkstone/build-jetson-nano/conf/local.conf"
content = open(f).read()

old = 'KERNEL_ROOTSPEC_DEFAULT = "mmcblk0p1"'
new = 'KERNEL_ROOTSPEC_DEFAULT:forcevariable = "mmcblk0p1"'

if new in content:
    print("Already set with :forcevariable")
elif old in content:
    content = content.replace(old, new)
    open(f, "w").write(content)
    print("Updated to :forcevariable")
elif "KERNEL_ROOTSPEC" not in content:
    content += '\n' + new + '\n'
    open(f, "w").write(content)
    print("Added KERNEL_ROOTSPEC_DEFAULT:forcevariable = mmcblk0p1")
else:
    print("Unexpected state, check manually")
