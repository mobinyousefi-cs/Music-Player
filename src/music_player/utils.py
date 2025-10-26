#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Python Music Player (Tkinter + pygame)
File: utils.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Utility helpers for time formatting, path ops, and metadata extraction.

===========================================================================
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mutagen import File as MutagenFile


@dataclass
class TrackMeta:
    path: Path
    title: str
    artist: Optional[str]
    album: Optional[str]
    duration: Optional[float]  # seconds


def is_audio(path: Path) -> bool:
    from .config import SUPPORTED_EXTS

    return path.suffix.lower() in SUPPORTED_EXTS


def hhmmss(seconds: float | int | None) -> str:
    if seconds is None or seconds < 0:
        return "--:--"
    s = int(seconds)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def scan_folder(folder: Path) -> list[Path]:
    """Recursively list supported audio files."""
    files: list[Path] = []
    for p in folder.rglob("*"):
        if p.is_file() and is_audio(p):
            files.append(p)
    return sorted(files)


def read_metadata(path: Path) -> TrackMeta:
    """Read common metadata via mutagen; be resilient to missing tags."""
    title = path.stem
    artist = None
    album = None
    duration = None
    try:
        mf = MutagenFile(path)
        if mf is not None:
            duration = float(getattr(mf.info, "length", None) or 0) or None
            tags = getattr(mf, "tags", None)
            if tags:
                title = str(tags.get("TIT2", [title])[0]) if tags.get("TIT2") else title
                artist = (
                    str(tags.get("TPE1", [None])[0]) if tags.get("TPE1") else None
                )
                album = str(tags.get("TALB", [None])[0]) if tags.get("TALB") else None
    except Exception:
        # Best-effort: fall back to filename
        pass
    return TrackMeta(path=path, title=title, artist=artist, album=album, duration=duration)