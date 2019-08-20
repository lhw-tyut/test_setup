import os
a = "/dev/sda1"
tmpdir = "/tmp/tmpAdsfewr"
path = "proc"
print(os.path.join(tmpdir, path))
print(a[-1])
boot_partition_label = "mkfs_esp"
print(boot_partition_label.upper())
device = "/dev/sda"
boot_part = '1'
sys_type = "centos"
print('chroot %s /bin/sh -c '
                                          '"efibootmgr -c -d %s -p %s -l '
                                          '\\\\\EFI\\\\\%s\\\\em\grubx64.efi"' %
                                          (tmpdir, device, boot_part, sys_type))

