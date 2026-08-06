f = "/home/ali/bitbake-builds/poky-kirkstone/build-jetson-nano/conf/local.conf"
content = open(f).read()
if "openssh" not in content:
    content += '\nIMAGE_INSTALL:append = " openssh openssh-sshd openssh-sftp-server"\n'
    content += 'EXTRA_IMAGE_FEATURES += "ssh-server-openssh"\n'
    open(f, "w").write(content)
    print("Added SSH to image")
else:
    print("SSH already present")
