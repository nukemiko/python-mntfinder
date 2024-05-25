# -*- encoding: utf-8 -*-
import os
from pathlib import PosixPath as Path
from typing import Iterator

import attrs

__all__ = ['MountPointInfo', 'getMountPoint', 'getAllMountPoints', 'isAMountPoint']

__version__ = '0.1.1'


@attrs.define(slots=True, kw_only=True, eq=False, order=False)
class MountPointInfo(os.PathLike[str]):
    """
    A class representing information about a mount point.

    The instance can be used as path-like objects by ``os.path.*``, ``pathlib.Path``, etc.
    When the instance is used as a path, it reflects the value of the attribute ``target``.

    Attributes:
        source (str): The source of the mount point.
        target (Path): The target path of the mount point.
        fstype (str): The file system type of the mount point.
        options (tuple[str, ...]): The options associated with the mount point.
        freq (int): The frequency of filesystem checks.
        passno (int): The pass number used by the filesystem checker.

    Methods:
        isStillMounted(self) -> bool:
            Returns ``False`` when called if attribute ``target`` is no longer a mount point; otherwise it returns ``True``.

            Once this method starts returning ``False``, it will not return ``True`` on any subsequent calls.
    """
    source: str = attrs.field(validator=attrs.validators.instance_of(str), on_setattr=attrs.setters.frozen)
    target: Path = attrs.field(validator=attrs.validators.instance_of(Path), on_setattr=attrs.setters.frozen)
    fstype: str = attrs.field(validator=attrs.validators.instance_of(str), on_setattr=attrs.setters.frozen)
    options: tuple[str, ...] = attrs.field(
        validator=attrs.validators.deep_iterable(
            attrs.validators.instance_of(str),
            attrs.validators.instance_of(tuple)
        ),
        on_setattr=attrs.setters.frozen
    )
    freq: int = attrs.field(validator=attrs.validators.instance_of(int), on_setattr=attrs.setters.frozen)
    passno: int = attrs.field(validator=attrs.validators.instance_of(int), on_setattr=attrs.setters.frozen)
    __mounted: bool = attrs.field(init=False, repr=False, default=True)

    def __eq__(self, other: 'MountPointInfo', /) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        if not self.isStillMounted():
            return NotImplemented
        if not other.isStillMounted():
            return NotImplemented
        return (
                other.source == self.source
                and other.target == self.target
                and other.fstype == self.fstype
                and other.options == self.options
                and other.freq == self.freq
                and other.passno == self.passno
        )

    def __fspath__(self) -> str:
        return os.fspath(self.target)

    def isStillMounted(self) -> bool:
        """
        Returns ``False`` when called if attribute ``target`` is no longer a mount point; otherwise it returns ``True``.

        Once this method starts returning ``False``, it will not return ``True`` on any subsequent calls.
        """
        if not self.__mounted:
            return self.__mounted

        mounted = self.target.is_mount()
        if not mounted:
            self.__mounted = mounted
        return mounted


def _mountsFileLineToMountPointInfo(line: str) -> MountPointInfo:
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

    return MountPointInfo(source=source, target=target, fstype=fstype, options=options, freq=freq, passno=passno)


def _iteratedParseMountInfoFile() -> Iterator[MountPointInfo]:
    mount_info_file = Path('/proc') / 'mounts'

    with open(mount_info_file, mode='r', newline='') as f:
        mount_info_text = f.read()

    for line in mount_info_text.split('\n'):
        if line:
            mount_point_info = _mountsFileLineToMountPointInfo(line)
            if mount_point_info.isStillMounted():
                yield mount_point_info


def getMountPoint(target: str | bytes | os.PathLike) -> MountPointInfo | None:
    """
    Get the ``MountPointInfo`` object corresponding to the given target path.

    Parameters:
        target (str | bytes | os.PathLike): The target path for which to retrieve the ``MountPointInfo`` object.

    Returns:
        MountPointInfo | None: The ``MountPointInfo`` object corresponding to the target path, or ``None`` if not found.
    """
    target_path = Path(os.fsdecode(target)).resolve()

    for mount_point_info in _iteratedParseMountInfoFile():
        if mount_point_info.target != target_path:
            continue

        return mount_point_info


def getAllMountPoints() -> list[MountPointInfo]:
    """
    Return a list of all current mount points on the system.

    Returns:
        list[MountPointInfo]: A list of ``MountPointInfo`` objects representing information about each mounted mount point.
    """
    return list(_iteratedParseMountInfoFile())


def isAMountPoint(target: str | bytes | os.PathLike | MountPointInfo) -> bool:
    """
    Check if the given ``target`` is a mount point or not.

    Parameters:
        target (str | bytes | os.PathLike | MountPointInfo): The target to check if it is a mount point or not.

    Returns:
        bool: ``True`` if the ``target`` is a mount point and still mounted, ``False`` otherwise.
    """
    if isinstance(target, MountPointInfo):
        return target.isStillMounted()
    return bool(getMountPoint(target))
