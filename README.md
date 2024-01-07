# mntfinder

Parse /proc/mounts and find/list mountpoints.

This project **IS NOT** a wrapper of `findmnt`.

## Install

Just run the command: `pip install mntfinder`.

Or you can download and install the wheel file from release page manually.

## Examples

All functions shown below can search for mountpoints in `/proc/<pid>/mounts` via the keyword argument `pid`. If not specified `pid`, these functions will search in `/proc/mounts` (it is usually linked to `/proc/self/mounts`.)

### `mntfinder.findMountPointByTarget(target: str | bytes | os.PathLike, *, pid: int | None = None) -> MountPoint | None`

```python
import mntfinder

mountpoint = mntfinder.findMountPointByTarget('/mnt/data')
if mountpoint:
    print(f"Mount point found: {mountpoint.source} -> {mountpoint.target} (Filesystem type: {mountpoint.fstype})")
else:
    print("Mount point not found")
```

### `mntfinder.listAllMountPoints(*, source: str | None = None, target: str | bytes | os.PathLike | None = None, fstype: str | None = None, pid: int | None = None) -> list[MountPoint]`

#### Retrieve all mount points

```python
import mntfinder

mountpoints = mntfinder.listAllMountPoints()
```

#### Retrieve mount points with a specific source

```python
import mntfinder

mountpoints = mntfinder.listAllMountPoints(source='/dev/sda1')
```

#### Retrieve mount points with a specific target

```python
import mntfinder

mountpoints = mntfinder.listAllMountPoints(target='/mnt/data')
```

#### Retrieve mount points with a specific file system type

```python
import mntfinder

mountpoints = mntfinder.listAllMountPoints(fstype='ext4')
```

### `mntfinder.isMountPoint(target: str | bytes | os.PathLike, *, source: str | None = None, fstype: str | None = None, pid: int | None = None) -> bool`

```python
import mntfinder

is_mount = mntfinder.isMountPoint('/mnt/data', source='/dev/sdb1', fstype='ext4')
if is_mount:
    print('/mnt/data is a mountpoint')
else:
    print('/mnt/data is not a mountpoint')
```
