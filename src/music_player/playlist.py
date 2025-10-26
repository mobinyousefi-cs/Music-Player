#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Python Music Player (Tkinter + pygame)
File: playlist.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Playlist model with cursor, shuffle and repeat modes.

===========================================================================
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .utils import read_metadata, TrackMeta


@dataclass
class RepeatMode:
    OFF: str = "off"
    ONE: str = "one"
    ALL: str = "all"


class Playlist:
    def __init__(self) -> None:
        self._tracks: List[TrackMeta] = []
        self._order: List[int] = []  # playback order indices into _tracks
        self._cursor: int = 0
        self.shuffle: bool = False
        self.repeat: str = RepeatMode.OFF

    # ---------- building ----------
    def load_paths(self, paths: list[Path]) -> None:
        self._tracks = [read_metadata(p) for p in paths]
        self._reset_order()

    def _reset_order(self) -> None:
        self._order = list(range(len(self._tracks)))
        if self.shuffle:
            random.shuffle(self._order)
        self._cursor = 0

    # ---------- querying ----------
    def __len__(self) -> int:
        return len(self._tracks)

    def current(self) -> Optional[TrackMeta]:
        if not self._tracks:
            return None
        return self._tracks[self._order[self._cursor]]

    def at(self, idx: int) -> Optional[TrackMeta]:
        if 0 <= idx < len(self._tracks):
            return self._tracks[idx]
        return None

    def index_of_path(self, path: Path) -> int:
        for i, t in enumerate(self._tracks):
            if t.path == path:
                return i
        return -1

    def set_cursor_by_index(self, idx: int) -> None:
        # place cursor to position in order that references idx
        for pos, ord_idx in enumerate(self._order):
            if ord_idx == idx:
                self._cursor = pos
                return

    # ---------- navigation ----------
    def next(self) -> Optional[TrackMeta]:
        if not self._tracks:
            return None
        if self.repeat == RepeatMode.ONE:
            return self.current()
        if self._cursor + 1 < len(self._order):
            self._cursor += 1
        else:
            if self.repeat == RepeatMode.ALL:
                self._cursor = 0
            else:
                return None
        return self.current()

    def prev(self) -> Optional[TrackMeta]:
        if not self._tracks:
            return None
        if self.repeat == RepeatMode.ONE:
            return self.current()
        if self._cursor > 0:
            self._cursor -= 1
        else:
            if self.repeat == RepeatMode.ALL:
                self._cursor = len(self._order) - 1
            else:
                return None
        return self.current()

    # ---------- modes ----------
    def toggle_shuffle(self) -> None:
        self.shuffle = not self.shuffle
        current = self.current()
        self._reset_order()
        if current is not None:
            # keep current track as active
            idx = self.index_of_path(current.path)
            self.set_cursor_by_index(idx)

    def cycle_repeat(self) -> str:
        order = [RepeatMode.OFF, RepeatMode.ONE, RepeatMode.ALL]
        self.repeat = order[(order.index(self.repeat) + 1) % len(order)]
        return self.repeat

    # ---------- exposure ----------
    @property
    def tracks(self) -> List[TrackMeta]:
        return list(self._tracks)

    @property
    def order(self) -> List[int]:
        return list(self._order)