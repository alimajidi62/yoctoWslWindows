f = "/home/ali/bitbake-builds/poky-kirkstone/build-jetson-nano/conf/local.conf"
lines = open(f).readlines()
out = []
for l in lines:
    if "MACHINE ??=" in l:
        out.append('MACHINE = "jetson-nano-devkit"\n')
    else:
        out.append(l)
out.append('\nOEQA_BUILDPATHS_SKIP = "/home/ali"\n')
out.append('IMAGE_CLASSES += "image_types_tegra"\n')
out.append('LICENSE_FLAGS_ACCEPTED = "commercial"\n')
open(f, "w").writelines(out)
print("Done")
