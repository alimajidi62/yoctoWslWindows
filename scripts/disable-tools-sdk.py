path = '/home/ali/bitbake-builds/poky-kirkstone/build-jetson-nano/conf/local.conf'
with open(path) as f:
    lines = f.readlines()
with open(path, 'w') as f:
    for line in lines:
        if line.strip() == 'EXTRA_IMAGE_FEATURES += "tools-sdk"':
            f.write('# EXTRA_IMAGE_FEATURES += "tools-sdk"  # disabled: triggers gcc-for-nvcc; install gcc post-boot via rpm\n')
        else:
            f.write(line)
print('Done - tools-sdk disabled in local.conf')
