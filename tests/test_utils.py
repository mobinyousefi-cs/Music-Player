from music_player.utils import hhmmss


def test_hhmmss_formats():
    assert hhmmss(0) == "0:00"
    assert hhmmss(59) == "0:59"
    assert hhmmss(60) == "1:00"
    assert hhmmss(61) == "1:01"
    assert hhmmss(3601) == "1:00:01"
    assert hhmmss(None) == "--:--"