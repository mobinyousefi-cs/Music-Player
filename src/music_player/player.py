#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Python Music Player (Tkinter + pygame)
File: player.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Thin wrapper over pygame.mixer.music providing play/pause/seek and position
tracking. Uses best-effort timing for progress bar.

Notes:
- pygame's `get_pos()` returns time since last `play()` in ms. We keep an
  internal offset to derive absolute position across pauses and seeks.
- Seeking is best-effort and may have codec limitations; MP3/OGG generally OK.

===========================================================================
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import pygame

from .config import DEFAULT_VOLUME
from .utils import read_metadata, TrackMeta


class Player:
    def __init__(self) -> None:
        pygame.mixer.init()
        self._current: Optional[TrackMeta] = None
        self._start_epoch: Optional[float] = None
        self._offset: float = 0.0
        self._paused: bool = False
        pygame.mixer.music.set_volume(DEFAULT_VOLUME)

    # ---------- control ----------
    def load(self, path: Path) -> TrackMeta:
        meta = read_metadata(path)
        pygame.mixer.music.load(str(path))
        self._current = meta
        self._start_epoch = None
        self._offset = 0.0
        self._paused = False
        return meta

    def play(self, start: float = 0.0) -> None:
        if self._current is None:
            return
        if start > 0:
            self._offset = start
        pygame.mixer.music.play(start=self._offset)
        self._start_epoch = time.time()
        self._paused = False

    def pause(self) -> None:
        if not self._paused:
            pygame.mixer.music.pause()
            self._paused = True
            if self._start_epoch is not None:
                self._offset += time.time() - self._start_epoch
                self._start_epoch = None

    def resume(self) -> None:
        if self._paused:
            pygame.mixer.music.unpause()
            self._paused = False
            self._start_epoch = time.time()

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self._paused = False
        self._start_epoch = None
        self._offset = 0.0

    def seek(self, position: float) -> None:
        """Seek to absolute position in seconds."""
        if self._current is None:
            return
        self._offset = max(0.0, position)
        pygame.mixer.music.play(start=self._offset)
        self._start_epoch = time.time()
        self._paused = False

    # ---------- state ----------
    def set_volume(self, vol01: float) -> None:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, vol01)))

    def get_volume(self) -> float:
        return float(pygame.mixer.music.get_volume())

    def position(self) -> float:
        if self._current is None:
            return 0.0
        if self._paused or self._start_epoch is None:
            return self._offset
        return self._offset + (time.time() - self._start_epoch)

    def duration(self) -> Optional[float]:
        return None if self._current is None else self._current.duration

    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()

    def is_paused(self) -> bool:
        return self._paused

    def current(self) -> Optional[TrackMeta]:
        return self._current