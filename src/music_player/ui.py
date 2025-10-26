#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Python Music Player (Tkinter + pygame)
File: ui.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Tkinter UI: menu, playlist view, transport controls, seekbar, volume, status bar.

===========================================================================
"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk, messagebox

from .config import TICK_MS
from .player import Player
from .playlist import Playlist, RepeatMode
from .utils import TrackMeta, hhmmss, scan_folder


class MusicPlayerApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=10)
        self.master.title("🎵 Music Player — Mobin Yousefi")
        self.master.minsize(900, 520)
        self.grid(sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Core
        self.player = Player()
        self.playlist = Playlist()

        # UI
        self._build_menu()
        self._build_main()
        self._bind_keys()

        self._tick()

    # -------------------- UI Builders --------------------
    def _build_menu(self) -> None:
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Open Folder…", command=self._open_folder)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        viewmenu = tk.Menu(menubar, tearoff=False)
        viewmenu.add_command(label="Shuffle", command=self._toggle_shuffle)
        viewmenu.add_command(label="Repeat", command=self._cycle_repeat)
        menubar.add_cascade(label="Playback", menu=viewmenu)

        self.master.config(menu=menubar)

    def _build_main(self) -> None:
        # Left: playlist
        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Playlist", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        self.tree = ttk.Treeview(left, columns=("title", "artist", "album", "dur"), show="headings")
        self.tree.heading("title", text="Title")
        self.tree.heading("artist", text="Artist")
        self.tree.heading("album", text="Album")
        self.tree.heading("dur", text="Duration")
        self.tree.column("title", width=320)
        self.tree.column("artist", width=150)
        self.tree.column("album", width=150)
        self.tree.column("dur", width=80, anchor="e")
        self.tree.grid(row=1, column=0, sticky="nsew")

        vs = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        vs.grid(row=1, column=1, sticky="ns")

        self.tree.bind("<Double-1>", self._on_tree_double_click)

        # Right: now playing + controls
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew")
        self.columnconfigure(1, weight=0)

        self.now_title = ttk.Label(right, text="Open a folder to start", font=("Segoe UI", 12, "bold"))
        self.now_title.grid(row=0, column=0, sticky="w")
        self.now_meta = ttk.Label(right, text="", foreground="#666")
        self.now_meta.grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Seek bar
        self.seek_var = tk.DoubleVar(value=0.0)
        self.seek = ttk.Scale(right, orient="horizontal", from_=0.0, to=100.0, variable=self.seek_var)
        self.seek.grid(row=2, column=0, sticky="ew")
        right.columnconfigure(0, weight=1)
        self.seek.bind("<ButtonRelease-1>", self._on_seek)

        self.time_label = ttk.Label(right, text="00:00 / 00:00")
        self.time_label.grid(row=3, column=0, sticky="w", pady=(2, 10))

        # Transport controls
        ctrl = ttk.Frame(right)
        ctrl.grid(row=4, column=0, pady=8, sticky="w")
        ttk.Button(ctrl, text="⏮ Prev", command=self._prev).grid(row=0, column=0, padx=2)
        self.play_btn = ttk.Button(ctrl, text="▶️ Play", command=self._play_pause)
        self.play_btn.grid(row=0, column=1, padx=2)
        ttk.Button(ctrl, text="⏭ Next", command=self._next).grid(row=0, column=2, padx=2)
        self.shuffle_btn = ttk.Button(ctrl, text="Shuffle: Off", command=self._toggle_shuffle)
        self.shuffle_btn.grid(row=0, column=3, padx=10)
        self.repeat_btn = ttk.Button(ctrl, text="Repeat: Off", command=self._cycle_repeat)
        self.repeat_btn.grid(row=0, column=4, padx=2)

        # Volume
        vol_frame = ttk.Frame(right)
        vol_frame.grid(row=5, column=0, sticky="ew", pady=8)
        ttk.Label(vol_frame, text="🔊 Volume").grid(row=0, column=0, padx=(0, 8))
        self.vol_var = tk.DoubleVar(value=70)
        self.vol = ttk.Scale(vol_frame, orient="horizontal", from_=0, to=100, variable=self.vol_var,
                             command=self._on_volume)
        self.vol.grid(row=0, column=1, sticky="ew")
        vol_frame.columnconfigure(1, weight=1)

        # Status bar
        self.status = ttk.Label(self, text="Ready", anchor="w")
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _bind_keys(self) -> None:
        self.master.bind("<space>", lambda e: self._play_pause())
        self.master.bind("<Left>", lambda e: self._nudge(-5))
        self.master.bind("<Right>", lambda e: self._nudge(+5))
        self.master.bind("n", lambda e: self._next())
        self.master.bind("p", lambda e: self._prev())
        self.master.bind("<Up>", lambda e: self._vol_delta(+5))
        self.master.bind("<Down>", lambda e: self._vol_delta(-5))

    # -------------------- Actions --------------------
    def _open_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Music Folder")
        if not folder:
            return
        paths = scan_folder(Path(folder))
        if not paths:
            messagebox.showinfo("No audio", "No supported audio files found in this folder.")
            return
        self.playlist.load_paths(paths)
        self._refresh_playlist_view()
        self.status.config(text=f"Loaded {len(paths)} tracks from {folder}")

    def _play_pause(self) -> None:
        cur = self.playlist.current()
        if cur is None:
            # nothing loaded; try first item
            if self.tree.get_children():
                self._play_tree_index(0)
            return

        if self.player.is_playing() and not self.player.is_paused():
            self.player.pause()
            self.play_btn.config(text="▶️ Play")
            return
        if self.player.is_paused():
            self.player.resume()
            self.play_btn.config(text="⏸ Pause")
            return

        # (re)start current
        self._load_and_play(cur)

    def _prev(self) -> None:
        prev_track = self.playlist.prev()
        if prev_track is not None:
            self._load_and_play(prev_track)

    def _next(self) -> None:
        next_track = self.playlist.next()
        if next_track is not None:
            self._load_and_play(next_track)

    def _toggle_shuffle(self) -> None:
        self.playlist.toggle_shuffle()
        self.shuffle_btn.config(text=f"Shuffle: {'On' if self.playlist.shuffle else 'Off'}")
        self._refresh_playlist_view()

    def _cycle_repeat(self) -> None:
        mode = self.playlist.cycle_repeat()
        label = {RepeatMode.OFF: "Off", RepeatMode.ONE: "One", RepeatMode.ALL: "All"}[mode]
        self.repeat_btn.config(text=f"Repeat: {label}")

    def _on_tree_double_click(self, _event=None) -> None:
        item = self.tree.selection()
        if not item:
            return
        idx = int(self.tree.index(item[0]))
        ord_idx = self.playlist.order[idx]
        track = self.playlist.at(ord_idx)
        if track is not None:
            self.playlist.set_cursor_by_index(ord_idx)
            self._load_and_play(track)

    def _on_seek(self, _event=None) -> None:
        dur = self.player.duration() or 0.0
        seek_to = (self.seek_var.get() / 100.0) * max(0.0, dur)
        self.player.seek(seek_to)

    def _on_volume(self, _value=None) -> None:
        self.player.set_volume(self.vol_var.get() / 100.0)

    def _nudge(self, delta: float) -> None:
        pos = self.player.position()
        self.player.seek(max(0.0, pos + delta))

    def _vol_delta(self, delta: float) -> None:
        v = min(100, max(0, self.vol_var.get() + delta))
        self.vol_var.set(v)
        self._on_volume()

    # -------------------- Helpers --------------------
    def _load_and_play(self, track: TrackMeta) -> None:
        meta = self.player.load(track.path)
        self.player.play()
        self.play_btn.config(text="⏸ Pause")
        self._update_now_playing(meta)
        self._highlight_current_in_tree()

    def _update_now_playing(self, meta: TrackMeta) -> None:
        self.now_title.config(text=meta.title)
        details = []
        if meta.artist:
            details.append(meta.artist)
        if meta.album:
            details.append(meta.album)
        self.now_meta.config(text=" • ".join(details))

    def _refresh_playlist_view(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx in self.playlist.order:
            t = self.playlist.tracks[idx]
            self.tree.insert("", "end", values=(t.title, t.artist or "", t.album or "", hhmmss(t.duration)))
        self._highlight_current_in_tree()

    def _highlight_current_in_tree(self) -> None:
        # highlight current row
        for item in self.tree.get_children():
            self.tree.item(item, tags=())
        cur = self.playlist.current()
        if not cur:
            return
        index_in_tracks = self.playlist.index_of_path(cur.path)
        for pos, ord_idx in enumerate(self.playlist.order):
            if ord_idx == index_in_tracks:
                item = self.tree.get_children()[pos]
                self.tree.selection_set(item)
                self.tree.see(item)
                break

    # -------------------- Main loop tick --------------------
    def _tick(self) -> None:
        # update progress and auto-advance when finished
        dur = self.player.duration() or 0.0
        pos = self.player.position()
        if dur > 0:
            self.seek_var.set(min(100.0, (pos / dur) * 100.0))
        self.time_label.config(text=f"{hhmmss(pos)} / {hhmmss(dur)}")

        # if finished playing naturally, advance
        if not self.player.is_paused() and not self.player.is_playing() and dur > 0 and pos > 0:
            nxt = self.playlist.next()
            if nxt is not None:
                self._load_and_play(nxt)

        self.after(TICK_MS, self._tick)

    # -------------------- Programmatic play from tree index --------------------
    def _play_tree_index(self, view_index: int) -> None:
        ord_idx = self.playlist.order[view_index]
        track = self.playlist.at(ord_idx)
        if track is not None:
            self.playlist.set_cursor_by_index(ord_idx)
            self._load_and_play(track)