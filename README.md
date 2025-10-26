# 🎵 Python Music Player (Tkinter + pygame)

A lightweight, cross-platform music player built with **Tkinter** for UI, **pygame** for audio
playback, and **mutagen** for metadata. Clean architecture, friendly UX, and your preferred
`src/` repo layout.

## ✨ Features
- Open a **folder** of music; auto-build playlist
- **Play / Pause / Next / Previous**
- **Seek bar** with current time & duration
- **Volume** slider with mute toggle
- **Shuffle** & **Repeat (off / one / all)**
- Displays **track title, artist, album** (when available)
- Keyboard shortcuts: `Space` (play/pause), `←/→` (seek), `↑/↓` (volume), `N/P` (next/prev)

## 🧰 Tech Stack
- Python 3.9+
- Tkinter (stdlib)
- pygame (audio backend)
- mutagen (MP3/FLAC/WAV metadata)

## 📦 Installation
```bash
# clone
git clone https://github.com/mobinyousefi-cs/python-music-player.git
cd python-music-player

# create venv (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# install
pip install -e .
```

> On Linux you may need SDL dependencies for `pygame` (e.g., `sudo apt install libsdl2-mixer-2.0-0`).

## ▶️ Run
```bash
python -m music_player
# or
python src/music_player/main.py
```

Then click **File → Open Folder** and select your music directory.

## 🧪 Tests
```bash
pytest
```

## 📁 Project Layout
```
.
├── src/
│   └── music_player/
│       ├── __init__.py
│       ├── main.py
│       ├── ui.py
│       ├── player.py
│       ├── playlist.py
│       ├── utils.py
│       ├── config.py
│       └── version.py
├── tests/
│   ├── test_playlist.py
│   └── test_utils.py
├── .github/workflows/ci.yml
├── .editorconfig
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## 📝 License
MIT © 2025 [Mobin Yousefi](https://github.com/mobinyousefi-cs)