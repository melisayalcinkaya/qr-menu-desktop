"""Uygulama ayarları (QSettings: Windows'ta kayıt defteri, diğerlerinde .ini)."""

from dataclasses import dataclass

from PySide6.QtCore import QSettings

DEFAULT_SERVER = "https://qr-menus.onrender.com"


@dataclass
class AppSettings:
    server: str = DEFAULT_SERVER
    username: str = ""
    remember: bool = True
    business: str = ""
    poll_seconds: int = 5
    sound: bool = True
    notifications: bool = True

    @classmethod
    def load(cls, store: QSettings | None = None) -> "AppSettings":
        store = store or QSettings()
        defaults = cls()
        return cls(
            server=str(store.value("server", defaults.server)),
            username=str(store.value("username", "")),
            remember=_bool(store.value("remember", True)),
            business=str(store.value("business", "")),
            poll_seconds=max(3, min(60, int(store.value("poll_seconds", 5)))),
            sound=_bool(store.value("sound", True)),
            notifications=_bool(store.value("notifications", True)),
        )

    def save(self, store: QSettings | None = None) -> None:
        store = store or QSettings()
        for key, value in self.__dict__.items():
            store.setValue(key, value)
        store.sync()


def _bool(value) -> bool:
    # QSettings .ini dosyasında boolean'ları "true"/"false" metni olarak döndürebilir
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)
