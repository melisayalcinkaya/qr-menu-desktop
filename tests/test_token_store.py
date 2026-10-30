from qrmenu_desktop import token_store


def test_save_load_delete(memory_keyring):
    assert token_store.available()
    token_store.save("https://a", "demo", "r1")
    assert token_store.load("https://a", "demo") == "r1"
    assert token_store.load("https://b", "demo") is None  # sunucuya göre ayrı
    token_store.save("https://a", "demo", None)
    assert token_store.load("https://a", "demo") is None


def test_settings_round_trip():
    from qrmenu_desktop.settings import AppSettings

    s = AppSettings(server="https://x", username="demo", poll_seconds=12, sound=False)
    s.save()
    loaded = AppSettings.load()
    assert (loaded.server, loaded.username, loaded.poll_seconds, loaded.sound) == (
        "https://x",
        "demo",
        12,
        False,
    )


def test_chime_is_a_valid_wav():
    import wave

    from qrmenu_desktop.sound import _chime_wav

    with wave.open(str(_chime_wav())) as wav:
        assert wav.getframerate() == 22050
        assert 0.5 < wav.getnframes() / wav.getframerate() < 1
