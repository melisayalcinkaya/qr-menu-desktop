import json
import threading

import httpx
import pytest
import respx

from qrmenu_desktop.api import ApiClient, ApiError, SessionExpiredError, validate_server_url

BASE = "https://menu.example.com"


def login_response(access="a1", refresh="r1"):
    return httpx.Response(
        200,
        json={"access": access, "user": {"id": 1, "username": "demo"}},
        headers={"set-cookie": f"qrmenu_refresh={refresh}; Path=/api/auth/; HttpOnly; Secure"},
    )


@pytest.mark.parametrize(
    "url",
    ["https://menu.example.com/", "http://localhost:8000", "http://127.0.0.1:8000", "http://192.168.1.20"],
)
def test_accepts_https_and_local_http(url):
    assert not validate_server_url(url).endswith("/")


@pytest.mark.parametrize("url", ["http://menu.example.com", "ftp://x", "menu.example.com", ""])
def test_rejects_plain_http_to_internet_and_junk(url):
    # Şifre internet üzerinden şifrelenmemiş gitmesin
    with pytest.raises(ValueError):
        validate_server_url(url)


@respx.mock
def test_login_reads_refresh_from_cookie_and_reports_it():
    respx.post(f"{BASE}/api/auth/login/").mock(return_value=login_response())
    api = ApiClient(BASE)
    seen = []
    api.on_refresh_token_changed = seen.append
    user = api.login("demo", "pw")
    assert user["username"] == "demo"
    assert api.tokens.access == "a1"
    assert api.tokens.refresh == "r1"
    assert seen == ["r1"]
    assert not api._http.cookies  # belirteç çerez kavanozunda bırakılmaz


@respx.mock
def test_expired_access_is_refreshed_once_and_request_retried():
    respx.post(f"{BASE}/api/auth/login/").mock(return_value=login_response())
    refresh = respx.post(f"{BASE}/api/auth/refresh/").mock(
        return_value=httpx.Response(
            200,
            json={"access": "a2"},
            headers={"set-cookie": "qrmenu_refresh=r2; Path=/api/auth/; HttpOnly"},
        )
    )
    route = respx.get(f"{BASE}/api/businesses/").mock(
        side_effect=lambda req: (
            httpx.Response(200, json={"results": [], "next": None})
            if req.headers["Authorization"] == "Bearer a2"
            else httpx.Response(401, json={"detail": "expired"})
        )
    )
    api = ApiClient(BASE)
    api.login("demo", "pw")
    assert api.businesses() == []
    assert route.call_count == 2
    assert json.loads(refresh.calls[0].request.content) == {"refresh": "r1"}
    assert api.tokens.refresh == "r2"  # rotasyon


@respx.mock
def test_failed_refresh_ends_session():
    respx.post(f"{BASE}/api/auth/login/").mock(return_value=login_response())
    respx.post(f"{BASE}/api/auth/refresh/").mock(return_value=httpx.Response(401, json={"detail": "x"}))
    respx.get(f"{BASE}/api/businesses/").mock(return_value=httpx.Response(401, json={"detail": "x"}))
    api = ApiClient(BASE)
    api.login("demo", "pw")
    with pytest.raises(SessionExpiredError):
        api.businesses()
    assert api.tokens.refresh is None


@respx.mock
def test_concurrent_requests_share_one_refresh():
    """Yoklama ve kullanıcı işlemi aynı anda 401 alırsa tek yenileme yapılmalı;
    yoksa rotasyon nedeniyle ikinci yenileme eski belirteçle başarısız olur."""
    respx.post(f"{BASE}/api/auth/login/").mock(return_value=login_response())
    refresh = respx.post(f"{BASE}/api/auth/refresh/").mock(
        return_value=httpx.Response(
            200, json={"access": "a2"}, headers={"set-cookie": "qrmenu_refresh=r2; Path=/"}
        )
    )
    respx.get(f"{BASE}/api/meta/").mock(
        side_effect=lambda req: (
            httpx.Response(200, json={"ok": True})
            if req.headers.get("Authorization") == "Bearer a2"
            else httpx.Response(401, json={"detail": "expired"})
        )
    )
    api = ApiClient(BASE)
    api.login("demo", "pw")
    results, barrier = [], threading.Barrier(5)

    def worker():
        barrier.wait()
        results.append(api.meta())

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results == [{"ok": True}] * 5
    assert refresh.call_count == 1


@respx.mock
def test_pagination_collects_every_page():
    def page(request):
        n = int(request.url.params.get("page", 1))
        return httpx.Response(200, json={"results": [n], "next": "x" if n < 3 else None})

    respx.get(f"{BASE}/api/tables/").mock(side_effect=page)
    api = ApiClient(BASE)
    assert api.tables("cafe") == [1, 2, 3]


@respx.mock
def test_errors_are_human_readable():
    respx.post(f"{BASE}/api/tables/").mock(
        return_value=httpx.Response(400, json={"label": ["Bu işletmede aynı adlı bir masa var."]})
    )
    respx.get(f"{BASE}/api/meta/").mock(side_effect=httpx.ConnectError("down"))
    api = ApiClient(BASE)
    with pytest.raises(ApiError) as err:
        api.create_table("cafe", "5")
    assert err.value.message == "Bu işletmede aynı adlı bir masa var."
    assert err.value.field_errors["label"]
    with pytest.raises(ApiError) as err:
        api.meta()
    assert err.value.status == 0
    assert "ulaşılamadı" in err.value.message


@respx.mock
def test_binary_responses_are_bytes():
    respx.get(f"{BASE}/api/tables/7/qr/").mock(
        return_value=httpx.Response(200, content=b"\x89PNG...", headers={"content-type": "image/png"})
    )
    assert ApiClient(BASE).table_qr_png(7).startswith(b"\x89PNG")
