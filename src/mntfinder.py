# -*- encoding: utf-8 -*-
import os
import warnings
from pathlib import PosixPath as Path
from typing import Iterator

import attrs

__all__ = ['MountPointInfo', 'getMountPoint', 'getAllMountPoints', 'isAMountPoint']

__version__ = '1.1.0'


@attrs.frozen(slots=True, kw_only=True, eq=False, order=False, hash=True)
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
        isAlive(self) -> bool:
            Returns ``False`` when called if attribute ``target`` is no longer a mount point; otherwise it returns ``True``.
        isStillMounted(self) -> bool:
            Deprecated. Use method ``isAlive()`` instead.
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

    def __eq(self, other: 'MountPointInfo', /) -> bool:
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in attrs.asdict(self)  # type:ignore
        )

    def __eq__(self, other: 'MountPointInfo', /) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.isAlive() and other.isAlive() and self.__eq(other)

    def __lt__(self, other: 'MountPointInfo', /) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.target < other.target

    def __le__(self, other: 'MountPointInfo', /) -> bool:
        return NotImplemented

    def __gt__(self, other: 'MountPointInfo', /) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.target > other.target

    def __ge__(self, other: 'MountPointInfo', /) -> bool:
        return NotImplemented

    def __fspath__(self) -> str:
        return os.fspath(self.target)

    def isStillMounted(self) -> bool:
        """
        Returns ``False`` when called if attribute ``target`` is no longer a mount point; otherwise it returns ``True``.

        Now this method is deprecated, please use method ``isAlive()`` instead.
        """
        warnings.warn(
            'Method isStillMounted() is deprecated. Please use method isAlive() instead.',
            DeprecationWarning
        )
        return self.isAlive()

    def isAlive(self) -> bool:
        """
        Returns ``False`` when called if attribute ``target`` is no longer a mount point; otherwise it returns ``True``.
        """
        if os.path.ismount(self.target):
            try:
                if mnt := getMountPoint(self.target):
                    return self.__eq(mnt)
            except ValueError:
                pass

        return False


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
    mount_info_file = Path('/proc/mounts')

    with open(mount_info_file, mode='r', newline='') as f:
        mount_info_text = f.read()

    for line in mount_info_text.split('\n'):
        if line:
            mount_point_info = _mountsFileLineToMountPointInfo(line)
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
        return target.isAlive()
    if mnt := getMountPoint(target):
        return mnt.isAlive()
    return False
