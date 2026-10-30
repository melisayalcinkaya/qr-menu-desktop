"""QR Menü API istemcisi.

Web paneliyle aynı uç noktaları kullanır. Tarayıcı yenileme belirtecini HttpOnly
çerezde tutar; masaüstü uygulamasında JavaScript olmadığı için belirteci çerezden
okuyup işletim sisteminin anahtar zincirine (bkz. token_store.py) kaydederiz.

İstemci birden çok iş parçacığından (arka plan yoklaması + kullanıcı işlemleri)
kullanılır; belirteç yenileme bir kilitle korunur.
"""

from __future__ import annotations

import ipaddress
import threading
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import httpx

REFRESH_COOKIE = "qrmenu_refresh"
USER_AGENT = "qr-menu-desktop"


class ApiError(Exception):
    """Sunucunun döndürdüğü hata; `message` kullanıcıya gösterilebilir."""

    def __init__(self, status: int, data: Any = None):
        self.status = status
        self.data = data
        self.field_errors = data if isinstance(data, dict) and "detail" not in data else {}
        super().__init__(_message(status, data))

    @property
    def message(self) -> str:
        return str(self)


class SessionExpiredError(ApiError):
    """Yenileme belirteci geçersiz; kullanıcı yeniden giriş yapmalı."""

    def __init__(self):
        super().__init__(401, {"detail": "Oturumun süresi doldu. Lütfen yeniden giriş yapın."})


def _message(status: int, data: Any) -> str:
    if status == 0:
        return "Sunucuya ulaşılamadı. İnternet bağlantısını ve sunucu adresini kontrol edin."
    if status == 429:
        return "Çok fazla istek gönderildi. Biraz bekleyip tekrar deneyin."
    if isinstance(data, dict):
        if data.get("detail"):
            return str(data["detail"])
        for value in data.values():
            if isinstance(value, list) and value:
                return str(value[0])
            if isinstance(value, str):
                return value
    if status >= 500:
        return "Sunucuda bir hata oluştu. Biraz sonra tekrar deneyin."
    return f"İstek tamamlanamadı (HTTP {status})."


def validate_server_url(url: str) -> str:
    """Sunucu adresini doğrular ve sonundaki '/' işaretini atar.

    Şifre ağ üzerinden gideceği için yerel ağ dışındaki adreslerde HTTPS zorunludur.
    """
    url = url.strip().rstrip("/")
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Adres http:// ya da https:// ile başlamalı (örn. https://ornek.onrender.com).")
    if parsed.scheme == "http" and not _is_local(parsed.hostname):
        raise ValueError("Güvenlik için yerel ağ dışındaki sunuculara yalnızca https:// ile bağlanılabilir.")
    return url


def _is_local(host: str) -> bool:
    if host == "localhost" or host.endswith(".local"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_loopback or ip.is_private


@dataclass
class Tokens:
    access: str | None = None
    refresh: str | None = None
    user: dict = field(default_factory=dict)


class ApiClient:
    def __init__(self, base_url: str, *, transport: httpx.BaseTransport | None = None, timeout=10.0):
        self.base_url = validate_server_url(base_url)
        self.tokens = Tokens()
        self._lock = threading.Lock()
        self._http = httpx.Client(
            base_url=f"{self.base_url}/api",
            timeout=timeout,
            transport=transport,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=False,
        )
        # Belirteç değiştiğinde (ör. anahtar zincirine kaydetmek için) çağrılır
        self.on_refresh_token_changed = lambda token: None

    def close(self):
        self._http.close()

    # --- Oturum ----------------------------------------------------------

    def login(self, username: str, password: str) -> dict:
        res = self._send("POST", "/auth/login/", json={"username": username, "password": password})
        data = self._json_or_raise(res)
        self._store_tokens(data["access"], self._take_refresh_cookie(res), data["user"])
        return data["user"]

    def resume(self, refresh_token: str) -> dict:
        """Kayıtlı yenileme belirteciyle oturumu sürdürür (uygulama yeniden açıldığında)."""
        self.tokens.refresh = refresh_token
        self._refresh()
        self.tokens.user = self.get("/auth/me/")
        return self.tokens.user

    def logout(self):
        if self.tokens.refresh:
            try:
                self._send("POST", "/auth/logout/", json={"refresh": self.tokens.refresh})
            except ApiError:
                pass  # sunucuya ulaşılamasa da yerel oturum kapanır
        self._store_tokens(None, None, {})

    def _store_tokens(self, access, refresh, user):
        changed = refresh != self.tokens.refresh
        self.tokens = Tokens(access, refresh, user)
        if changed:
            self.on_refresh_token_changed(refresh)

    def _take_refresh_cookie(self, res: httpx.Response) -> str | None:
        token = res.cookies.get(REFRESH_COOKIE)
        # Çerezi istemcinin deposundan sil: belirteci yalnızca gövdede, bilinçli olarak gönderiyoruz
        self._http.cookies.clear()
        return token

    def _refresh(self):
        """Yeni erişim belirteci al. Kilit, iki iş parçacığının aynı anda yenilemesini önler;
        rotasyon nedeniyle ikinci yenileme eski belirteçle başarısız olurdu."""
        used = self.tokens.refresh
        with self._lock:
            if self.tokens.refresh != used and self.tokens.access:
                return  # başka bir iş parçacığı biz beklerken yeniledi
            if not self.tokens.refresh:
                raise SessionExpiredError()
            res = self._send("POST", "/auth/refresh/", json={"refresh": self.tokens.refresh})
            if res.status_code != 200:
                self._store_tokens(None, None, {})
                raise SessionExpiredError()
            new_refresh = self._take_refresh_cookie(res) or self.tokens.refresh
            self._store_tokens(res.json()["access"], new_refresh, self.tokens.user)

    # --- Genel istek ---------------------------------------------------------

    def _send(self, method, path, **kwargs) -> httpx.Response:
        try:
            return self._http.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise ApiError(0) from exc

    @staticmethod
    def _json_or_raise(res: httpx.Response):
        if res.status_code >= 400:
            try:
                data = res.json()
            except ValueError:
                data = None
            raise ApiError(res.status_code, data)
        if res.status_code == 204 or not res.content:
            return None
        if "application/json" in res.headers.get("content-type", ""):
            return res.json()
        return res.content

    def request(self, method: str, path: str, **kwargs):
        for attempt in (1, 2):
            headers = kwargs.pop("headers", {})
            if self.tokens.access:
                headers["Authorization"] = f"Bearer {self.tokens.access}"
            res = self._send(method, path, headers=headers, **kwargs)
            if res.status_code == 401 and attempt == 1:
                self._refresh()
                continue
            return self._json_or_raise(res)
        raise SessionExpiredError()  # pragma: no cover

    def get(self, path, **params):
        return self.request("GET", path, params=params or None)

    def post(self, path, json=None):
        return self.request("POST", path, json=json)

    def patch(self, path, json=None, files=None, data=None):
        return self.request("PATCH", path, json=json, files=files, data=data)

    def delete(self, path):
        return self.request("DELETE", path)

    def get_all(self, path, **params) -> list:
        """Sayfalı listenin tüm sayfalarını toplar."""
        params = {k: v for k, v in params.items() if v is not None}
        items, page = [], 1
        while True:
            data = self.get(path, page=page, **params)
            items.extend(data["results"])
            if not data.get("next"):
                return items
            page += 1

    # --- Uç noktalar ---------------------------------------------------------

    def meta(self):
        return self.get("/meta/")

    def businesses(self):
        return self.get_all("/businesses/")

    def pending_calls(self, slug):
        return self.get_all("/waiter-calls/", business=slug, status="pending")

    def close_call(self, call_id, action):
        assert action in {"complete", "cancel"}
        return self.post(f"/waiter-calls/{call_id}/{action}/")

    def categories(self, slug):
        return self.get_all("/categories/", business=slug)

    def products(self, slug):
        return self.get_all("/products/", business=slug)

    def update_product(self, product_id, data):
        return self.patch(f"/products/{product_id}/", json=data)

    def tables(self, slug):
        return self.get_all("/tables/", business=slug)

    def create_table(self, slug, label, position=0):
        return self.post("/tables/", {"business": slug, "label": label, "position": position})

    def regenerate_table(self, table_id):
        return self.post(f"/tables/{table_id}/regenerate-token/")

    def delete_table(self, table_id):
        return self.delete(f"/tables/{table_id}/")

    def table_qr_png(self, table_id) -> bytes:
        return self.get(f"/tables/{table_id}/qr/")

    def table_cards_pdf(self, slug) -> bytes:
        return self.get(f"/businesses/{slug}/table-cards/")

    def comments(self, slug, status):
        return self.get_all("/comments/", business=slug, status=status)

    def review_comment(self, comment_id, action):
        assert action in {"approve", "reject"}
        return self.post(f"/comments/{comment_id}/{action}/")

    def delete_comment(self, comment_id):
        return self.delete(f"/comments/{comment_id}/")

    def stats(self, slug, days=7):
        return self.get(f"/businesses/{slug}/stats/", days=days)
