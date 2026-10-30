"""Yeni çağrı için kısa iki tonlu zil sesi (ses dosyası gerekmeden üretilir)."""

import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


def _chime_wav() -> Path:
    path = Path(tempfile.gettempdir()) / "qr-menu-chime.wav"
    if path.exists():
        return path
    rate = 22050
    frames = bytearray()
    total = int(rate * 0.75)
    for i in range(total):
        t = i / rate
        sample = 0.0
        for freq, start in ((880, 0.0), (1175, 0.18)):
            if t >= start:
                local = t - start
                sample += math.sin(2 * math.pi * freq * local) * math.exp(-local * 6) * 0.35
        frames += struct.pack("<h", int(max(-1, min(1, sample)) * 32767))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(bytes(frames))
    return path


def play_chime():
    """Zil sesini çalar; çalamazsa sistem bip sesine düşer.

    Windows'ta standart kütüphanedeki winsound kullanılır. Böylece QtMultimedia
    (paketlenmiş uygulamaya yüzlerce MB ekleyen PySide6-Addons) gerekmez.
    """
    path = str(_chime_wav())
    try:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        player = next((p for p in ("afplay", "paplay", "aplay") if shutil.which(p)), None)
        if player:
            subprocess.Popen(  # noqa: S603 - sabit program adı ve kendi ürettiğimiz dosya
                [player, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return
    except OSError:
        pass
    from PySide6.QtWidgets import QApplication

    QApplication.beep()
