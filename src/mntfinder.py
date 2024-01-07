# -*- encoding: utf-8 -*-
import os
from pathlib import PosixPath as Path
from typing import Iterator

import attrs

__all__ = ['MountPoint', 'findMountPointByTarget', 'listAllMountPoints', 'isMountPoint']

__version__ = '0.1.1'


@attrs.frozen(slots=True, kw_only=True)
class MountPoint(os.PathLike[str]):
    """
    Represents a mount point in the file system.

    Attributes:
        source (str): The source of the mount point (e.g., device or network location).
        target (Path): The target directory where the mount point is mounted.
        fstype (str): The file system type of the mount point.
        options (tuple[str, ...]): The options for the mount point (e.g., read-write, noatime).
        freq (int): The frequency of file system checks (0 for no checks).
        passno (int): The pass number for file system checks (0 for no checks).
    """

    source: str = attrs.field(validator=attrs.validators.instance_of(str))
    target: Path = attrs.field(validator=attrs.validators.instance_of(Path))
    fstype: str = attrs.field(validator=attrs.validators.instance_of(str))
    options: tuple[str, ...] = attrs.field(
        validator=attrs.validators.deep_iterable(
            attrs.validators.instance_of(str),
            attrs.validators.instance_of(tuple)
        )
    )
    freq: int = attrs.field(validator=attrs.validators.instance_of(int))
    passno: int = attrs.field(validator=attrs.validators.instance_of(int))

    def __fspath__(self) -> str:
        """
        Returns the target of the mount point as a string path.

        Returns:
            str: The target of the mount point as a string path.
        """
        return os.fspath(self.target)


def _parseLineOfMountInfoFile(line: str) -> MountPoint:
    line_parts = [s.replace('\\040', ' ').replace('\\012', '\n') for s in line.strip(' \n').split(' ')]
    if len(line_parts) != 6:
        raise ValueError(f'Not a valid line of mount info: {line!r}')

    source = line_parts[0]
    raw_target = line_parts[1]
    fstype = line_parts[2]
    options = tuple(line_parts[3].split(','))
    raw_freq = line_parts[4]
    if not raw_freq.isdigit():
        raise ValueError(f'Invalid value of fs_freq: {raw_freq!r}')
    freq = int(raw_freq)
    raw_passno = line_parts[5]
    if not raw_passno.isdigit():
        raise ValueError(f'Invalid value of fs_passno: {raw_passno!r}')
    passno = int(raw_passno)

    target = Path(str(bytes(raw_target, encoding='raw_unicode_escape'), encoding='unicode_escape')).resolve()

    return MountPoint(source=source, target=target, fstype=fstype, options=options, freq=freq, passno=passno)


def _iteratedParseMountInfoFile(*, pid: int | None = None) -> Iterator[MountPoint]:
    if pid is None:
        mount_info_file = Path('/proc/mounts')
    elif isinstance(pid, int):
        mount_info_file = Path('/proc') / str(int(pid)) / 'mounts'
    else:
        raise TypeError('{!r} must be int or None (got {!r})'.format('pid', type(pid)))

    with open(mount_info_file, mode='r', newline='') as f:
        mount_info_text = f.read()

    for line in mount_info_text.split('\n'):
        if line:
            yield _parseLineOfMountInfoFile(line)


def findMountPointByTarget(target: str | bytes | os.PathLike, *, pid: int | None = None) -> MountPoint | None:
    """
    Find the mount point object corresponding to the target path.

    Args:
        target (str, bytes or os.PathLike): The target path of the mount point to find.
        pid (int, optional): Optional process ID to filter mount points by. Defaults to None.

    Returns:
        MountPoint or None: The mount point object corresponding to the target path, or None if not found.
    """
    target_path = Path(os.fsdecode(target)).resolve()

    for mountpoint in _iteratedParseMountInfoFile(pid=pid):
        if mountpoint.target != target_path:
            continue

        return mountpoint


def listAllMountPoints(*, source: str | None = None,
                       target: str | bytes | os.PathLike | None = None,
                       fstype: str | None = None,
                       pid: int | None = None
                       ) -> list[MountPoint]:
    """
    Retrieves a list of mount points in the file system based on specified criteria.

    Args:
        source (str, optional): The source of the mount point (e.g., device or network location). Defaults to None.
        target (str | bytes | os.PathLike, optional): The target directory where the mount point is mounted. Defaults to None.
        fstype (str | None, optional): The file system type of the mount point. Defaults to None.
        pid (int | None, optional): The process ID for which to retrieve mount points. Defaults to None.

    Returns:
        list[MountPoint]: A list of MountPoint objects representing the mount points in the file system that match the specified criteria.
    """
    mountpoints: list[MountPoint] = []
    target_path = None if target is None else Path(os.fsdecode(target)).resolve()

    for mountpoint in _iteratedParseMountInfoFile(pid=pid):
        if source is not None and mountpoint.source != source:
            continue
        if target_path is not None and mountpoint.target != target_path:
            continue
        if fstype is not None and mountpoint.fstype != fstype:
            continue
        mountpoints.append(mountpoint)

    return mountpoints


def isMountPoint(target: str | bytes | os.PathLike,
                 *, source: str | None = None,
                 fstype: str | None = None,
                 pid: int | None = None
                 ) -> bool:
    """
    Check if a given target path is a mount point in the file system.

    Args:
        target (str, bytes or os.PathLike): The target path to check if it is a mount point.
        source (str, optional): Optional source of the mount point to filter by. Defaults to None.
        fstype (str, optional): Optional file system type of the mount point to filter by. Defaults to None.
        pid (int, optional): Optional process ID to filter mount points by. Defaults to None.

    Returns:
        bool: True if the target path is a mount point that matches the provided filters. False otherwise.
    """
    if mountpoint := findMountPointByTarget(target, pid=pid):
        if source is not None and mountpoint.source != source:
            return False
        if fstype is not None and mountpoint.fstype != fstype:
            return False
        return True
    else:
        return False
