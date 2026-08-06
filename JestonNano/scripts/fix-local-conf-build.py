f = "/home/ali/bitbake-builds/poky-kirkstone/build-jetson-nano/conf/local.conf"
c = open(f).read()
c = c.replace('PACKAGE_CLASSES = "package_ipk"', 'PACKAGE_CLASSES = "package_rpm"')
c = c.replace(
    'IMAGE_INSTALL:append = " tegra-libraries-cuda"',
    '# tegra-libraries-cuda disabled (gcc-for-nvcc checksum mismatch, fix separately)'
)
open(f, 'w').write(c)
print("Fixed. Relevant lines:")
for l in open(f):
    if any(k in l for k in ['PACKAGE_CLASSES', 'tegra-lib', 'tools-sdk',
                             'package-management', 'python3', 'glibc-utils', 'libstdc']):
        print(" ", l.rstrip())
