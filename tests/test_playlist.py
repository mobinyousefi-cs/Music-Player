from pathlib import Path

from music_player.playlist import Playlist, RepeatMode
from music_player.utils import TrackMeta


def fake_track(i: int) -> TrackMeta:
    return TrackMeta(path=Path(f"/tmp/t{i}.mp3"), title=f"T{i}", artist=None, album=None, duration=60)


def test_basic_navigation():
    pl = Playlist()
    pl._tracks = [fake_track(i) for i in range(3)]
    pl._reset_order()

    assert pl.current().title == "T0"
    assert pl.next().title == "T1"
    assert pl.next().title == "T2"
    assert pl.next() is None  # end with repeat off


def test_repeat_all_cycles():
    pl = Playlist()
    pl._tracks = [fake_track(i) for i in range(2)]
    pl.repeat = RepeatMode.ALL
    pl._reset_order()

    assert pl.current().title == "T0"
    assert pl.next().title == "T1"
    assert pl.next().title == "T0"  # loops


def test_shuffle_toggle_keeps_current():
    pl = Playlist()
    pl._tracks = [fake_track(i) for i in range(5)]
    pl._reset_order()
    current_path = pl.current().path
    pl.toggle_shuffle()
    assert pl.current().path == current_path