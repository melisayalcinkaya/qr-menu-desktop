from qrmenu_desktop import token_store
from qrmenu_desktop.api import ApiError
from qrmenu_desktop.settings import AppSettings
from qrmenu_desktop.ui.login import LoginDialog


class FakeClient:
    def __init__(self, server, fail=None):
        self.server, self.fail = server, fail
        self.tokens = type("T", (), {"refresh": "r1"})()
        self.on_refresh_token_changed = None

    def login(self, username, password):
        if self.fail:
            raise self.fail
        return {"username": username}

    def close(self):
        pass


def test_rejects_plain_http_server(qtbot):
    d = LoginDialog(AppSettings(server="http://menu.example.com"))
    qtbot.addWidget(d)
    d.username.setText("demo")
    d.password.setText("x")
    d.try_login()
    assert "https" in d.error.text()


def test_successful_login_remembers_session(qtbot):
    settings = AppSettings(server="https://menu.example.com")
    d = LoginDialog(settings, client_factory=FakeClient)
    qtbot.addWidget(d)
    d.username.setText("demo")
    d.password.setText("pw")
    d.remember.setChecked(True)
    d.try_login()
    qtbot.waitUntil(lambda: d.client is not None)
    assert token_store.load("https://menu.example.com", "demo") == "r1"
    assert d.password.text() == ""  # şifre bellekte tutulmaz
    assert AppSettings.load().username == "demo"


def test_wrong_password_message(qtbot):
    d = LoginDialog(
        AppSettings(server="https://menu.example.com"),
        client_factory=lambda s: FakeClient(s, fail=ApiError(401, {"detail": "x"})),
    )
    qtbot.addWidget(d)
    d.username.setText("demo")
    d.password.setText("bad")
    d.try_login()
    qtbot.waitUntil(lambda: not d.error.isHidden())
    assert d.error.text() == "Kullanıcı adı ya da şifre hatalı."
    assert d.submit.isEnabled()
