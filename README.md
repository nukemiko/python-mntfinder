# mntfinder

Parse /proc/mounts and find/list mountpoints.

This project **IS NOT** a wrapper of `findmnt`.

## Install

Just run the command: `pip install mntfinder`.

Or you can download and install the wheel file from release page manually.

## Examples

### List all mountpoints

```python
import mntfinder

for m in mntfinder.getAllMountPoints():
    print(f'{m.source!s} on {m.target!s} type {m.fstype!s} ({",".join(m.options)!s})')
```

Output:

```
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
sys on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
dev on /dev type devtmpfs (rw,nosuid,relatime,size=6915412k,nr_inodes=1728853,mode=755,inode64)
run on /run type tmpfs (rw,nosuid,nodev,relatime,mode=755,inode64)
efivarfs on /sys/firmware/efi/efivars type efivarfs (rw,nosuid,nodev,noexec,relatime)
/dev/nvme1n1p3 on / type btrfs (rw,relatime,ssd,discard=async,space_cache=v2,subvolid=5,subvol=/)
securityfs on /sys/kernel/security type securityfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev,inode64)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000)
tmpfs on /sys/fs/cgroup type tmpfs (ro,nosuid,nodev,noexec,size=4096k,nr_inodes=1024,mode=755,inode64)
cgroup2 on /sys/fs/cgroup/unified type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate)
cgroup on /sys/fs/cgroup/systemd type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,name=systemd)
pstore on /sys/fs/pstore type pstore (rw,nosuid,nodev,noexec,relatime)
bpf on /sys/fs/bpf type bpf (rw,nosuid,nodev,noexec,relatime,mode=700)
cgroup on /sys/fs/cgroup/hugetlb type cgroup (rw,nosuid,nodev,noexec,relatime,hugetlb)
cgroup on /sys/fs/cgroup/rdma type cgroup (rw,nosuid,nodev,noexec,relatime,rdma)
cgroup on /sys/fs/cgroup/memory type cgroup (rw,nosuid,nodev,noexec,relatime,memory)
cgroup on /sys/fs/cgroup/blkio type cgroup (rw,nosuid,nodev,noexec,relatime,blkio)
cgroup on /sys/fs/cgroup/cpuset type cgroup (rw,nosuid,nodev,noexec,relatime,cpuset)
cgroup on /sys/fs/cgroup/net_cls,net_prio type cgroup (rw,nosuid,nodev,noexec,relatime,net_cls,net_prio)
cgroup on /sys/fs/cgroup/misc type cgroup (rw,nosuid,nodev,noexec,relatime,misc)
cgroup on /sys/fs/cgroup/cpu,cpuacct type cgroup (rw,nosuid,nodev,noexec,relatime,cpu,cpuacct)
cgroup on /sys/fs/cgroup/perf_event type cgroup (rw,nosuid,nodev,noexec,relatime,perf_event)
cgroup on /sys/fs/cgroup/pids type cgroup (rw,nosuid,nodev,noexec,relatime,pids)
cgroup on /sys/fs/cgroup/devices type cgroup (rw,nosuid,nodev,noexec,relatime,devices)
cgroup on /sys/fs/cgroup/freezer type cgroup (rw,nosuid,nodev,noexec,relatime,freezer)
systemd-1 on /proc/sys/fs/binfmt_misc type autofs (rw,relatime,fd=37,pgrp=1,timeout=0,minproto=5,maxproto=5,direct,pipe_ino=4467)
debugfs on /sys/kernel/debug type debugfs (rw,nosuid,nodev,noexec,relatime)
mqueue on /dev/mqueue type mqueue (rw,nosuid,nodev,noexec,relatime)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,nosuid,nodev,relatime,pagesize=2M)
tracefs on /sys/kernel/tracing type tracefs (rw,nosuid,nodev,noexec,relatime)
configfs on /sys/kernel/config type configfs (rw,nosuid,nodev,noexec,relatime)
fusectl on /sys/fs/fuse/connections type fusectl (rw,nosuid,nodev,noexec,relatime)
tmpfs on /tmp type tmpfs (rw,nosuid,nodev,size=6947940k,nr_inodes=1048576,inode64)
/dev/nvme1n1p5 on /var/lib/libvirt/images type btrfs (rw,relatime,ssd,discard=async,space_cache=v2,subvolid=257,subvol=/var/lib/libvirt/@images)
/dev/nvme1n1p2 on /boot type ext4 (rw,relatime)
/dev/nvme1n1p1 on /boot/efi type vfat (rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro)
binfmt_misc on /proc/sys/fs/binfmt_misc type binfmt_misc (rw,nosuid,nodev,noexec,relatime)
tmpfs on /run/user/1000 type tmpfs (rw,nosuid,nodev,relatime,size=1389584k,nr_inodes=347396,mode=700,uid=1000,gid=1000,inode64)
portal on /run/user/1000/doc type fuse.portal (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000)
gvfsd-fuse on /run/user/1000/gvfs type fuse.gvfsd-fuse (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000)
```

## Get a single mountpoint info

```python
import mntfinder

mntinfo_proc = mntfinder.getMountPoint('/proc')
print(f'{mntinfo_proc.source!s} on {mntinfo_proc.target!s} type {mntinfo_proc.fstype!s} ({",".join(mntinfo_proc.options)!s})')
```

Output:

```
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
```

## Check if a path is mountpoint or not

```python
import mntfinder

print('/sys is a mountpoint:', mntfinder.isAMountPoint('/sys'))
print('/mnt/nonexist is a mountpoint:', mntfinder.isAMountPoint('/mnt/nonexist'))
```

Output:

```
/sys is a mountpoint: True
/mnt/nonexist is a mountpoint: False
```

## Check if a mountpoint is still mounted

```python
import mntfinder
import subprocess

mnt = mntfinder.getMountPoint('/run/media/user/WindowsData')
print(f'{mnt.source!s} on {mnt.target!s} type {mnt.fstype!s} ({",".join(mnt.options)!s})')
print(f'{mnt.target!s} is still mounted: {mnt.isStillMounted()!s}')
subprocess.run(['udisksctl', 'unmount', '--block-device', mnt.source])
print(f'{mnt.target!s} is still mounted: {mnt.isStillMounted()!s}')
```

Output:

```
/dev/nvme0n1p3 on /run/media/user/WindowsData type ntfs3 (ro,nosuid,nodev,relatime,uid=1000,gid=1000,iocharset=utf8)
/run/media/user/WindowsData is still mounted: True
Unmounted /dev/nvme0n1p3.
/run/media/user/WindowsData is still mounted: False
```
