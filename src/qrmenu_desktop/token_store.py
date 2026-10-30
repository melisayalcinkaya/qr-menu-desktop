"""Yenileme belirtecini işletim sisteminin anahtar zincirinde saklar.

Windows'ta Kimlik Bilgisi Yöneticisi, macOS'ta Anahtar Zinciri, Linux'ta Secret
Service kullanılır. Belirteç düz metin bir dosyaya ya da ayarlara yazılmaz. Anahtar
zinciri yoksa "beni hatırla" devre dışı kalır; uygulama yine çalışır.
"""

import keyring
from keyring.errors import KeyringError

SERVICE = "qr-menu-desktop"


def _key(server: str, username: str) -> str:
    return f"{server}|{username}"


def available() -> bool:
    try:
        backend = keyring.get_keyring()
    except KeyringError:
        return False
    return getattr(backend, "priority", 0) > 0


def load(server: str, username: str) -> str | None:
    try:
        return keyring.get_password(SERVICE, _key(server, username))
    except KeyringError:
        return None


def save(server: str, username: str, token: str | None) -> None:
    try:
        if token:
            keyring.set_password(SERVICE, _key(server, username), token)
        else:
            keyring.delete_password(SERVICE, _key(server, username))
    except KeyringError:
        pass
