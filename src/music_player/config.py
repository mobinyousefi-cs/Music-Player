#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Python Music Player (Tkinter + pygame)
File: config.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Centralized configuration and constants.

===========================================================================
"""
from __future__ import annotations

SUPPORTED_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a"}
DEFAULT_VOLUME = 0.7  # 0..1
TICK_MS = 500  # UI refresh rate for progress/position