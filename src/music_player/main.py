#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Python Music Player (Tkinter + pygame)
File: main.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
App entrypoint. Launches Tkinter UI.

Usage:
python -m music_player
# or
python src/music_player/main.py

===========================================================================
"""
from __future__ import annotations

import tkinter as tk

from .ui import MusicPlayerApp


def main() -> None:
    root = tk.Tk()
    # Native look
    try:
        root.call("tk", "scaling", 1.2)
    except Exception:
        pass
    app = MusicPlayerApp(root)
    app.mainloop()


if __name__ == "__main__":
    main()