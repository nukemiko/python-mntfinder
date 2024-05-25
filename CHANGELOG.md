# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Simplified Chinese version at [here](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## 1.0.0 - 2024-05-25

This version has the following changes, some of which are disruptive and NOT compatible with previous versions:

- Class `MountPointInfo`:
    - Renamed from `MountInfo`.
    - Implemented `__eq__()`, and its instances can now be compared with each other.
    - Implemented `__fspath__()`, and its instances can now be used as path-like objects by `os.path.*`, `pathlib.Path`, etc.
        - When the instance is used as a path, it reflects the value of the attribute `target`.
    - Added method `isStillMounted()`. This method returns `False` when called if attribute `target` is no longer a mount point; otherwise it returns `True`.
        - Once this method starts returning `False`, it will not return `True` on any subsequent calls.
- Function `getMountPoint()`:
    - Renamed from `findMountPointByTarget()`.
    - Removed keyword-only argument `pid`.
- Function `getAllMountPoints()`:
    - Renamed from `listAllMountPoints()`.
    - Removed all arguments.
- Function `isAMountPoint()`:
    - Renamed from `isMountPoint()`.
    - Removed all arguments except the positional argument `target`.

## 0.1.1 - 2024-01-08

- Added bytestring path support for the `target` argument of these functions:
    - `mntfinder.getMountPoint()`
    - `mntfinder.getAllMountPoints()`
    - `mntfinder.isAMountPoint()`
- Removed unused dependency `typing-extensions`.

## 0.1.0 - 2024-01-07

Initial release.
