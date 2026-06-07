from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class DirEntry:
    name: str
    path: str
    is_dir: bool
    size: int  # bytes


def get_size(path: str) -> int:
    """Recursively compute the total size of a path in bytes.

    Returns 0 if any PermissionError is encountered.
    """
    if os.path.islink(path):
        try:
            return os.lstat(path).st_size
        except OSError:
            return 0

    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0

    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        total += get_size(entry.path)
                    else:
                        total += entry.stat(follow_symlinks=False).st_size
                except OSError:
                    pass
    except PermissionError:
        pass
    return total


def list_entries_fast(
    path: str,
    show_hidden: bool = False,
) -> list[DirEntry]:
    """List directory contents without recursion.

    Files receive their real size from ``os.stat``; directories start at 0
    so the listing appears instantly.  Use :func:`get_size` afterwards to
    fill in directory sizes.
    """
    entries: list[DirEntry] = []
    try:
        with os.scandir(path) as it:
            for raw in it:
                if not show_hidden and raw.name.startswith("."):
                    continue
                try:
                    is_dir = raw.is_dir(follow_symlinks=False)
                    size = 0 if is_dir else raw.stat(follow_symlinks=False).st_size
                except OSError:
                    is_dir = False
                    size = 0
                entries.append(
                    DirEntry(name=raw.name, path=raw.path, is_dir=is_dir, size=size)
                )
    except PermissionError:
        pass
    return entries


def scan_dir(
    path: str,
    show_hidden: bool = False,
    sort_by: str = "size",
) -> list[DirEntry]:
    """List the contents of *path* as DirEntry objects.

    Entries are sorted by size (desc) or name (asc) depending on *sort_by*.
    Hidden entries (names starting with '.') are omitted unless *show_hidden*
    is True.
    """
    entries: list[DirEntry] = []

    try:
        with os.scandir(path) as it:
            for raw in it:
                if not show_hidden and raw.name.startswith("."):
                    continue
                try:
                    is_dir = raw.is_dir(follow_symlinks=False)
                except OSError:
                    is_dir = False
                size = get_size(raw.path)
                entries.append(
                    DirEntry(
                        name=raw.name,
                        path=raw.path,
                        is_dir=is_dir,
                        size=size,
                    )
                )
    except PermissionError:
        pass

    if sort_by == "size":
        entries.sort(key=lambda e: e.size, reverse=True)
    else:
        entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))

    return entries


def format_size(num_bytes: int) -> str:
    """Return a human-readable size string (e.g. '1.4 MB')."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:6.1f} {unit}"
        num_bytes /= 1024.0  # type: ignore[assignment]
    return f"{num_bytes:.1f} PB"


def make_bar(size: int, max_size: int, width: int = 20) -> str:
    """Return a proportional block-character bar."""
    if max_size == 0:
        return " " * width
    filled = round(width * size / max_size)
    return "█" * filled + "░" * (width - filled)
