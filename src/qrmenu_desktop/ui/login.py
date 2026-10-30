from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from .. import token_store
from ..api import ApiClient, validate_server_url
from ..tasks import run_async
from .common import button, error_text, label


class LoginDialog(QDialog):
    """Web paneliyle aynı hesapla giriş. Başarılı olursa `self.client` dolu olur."""

    def __init__(self, settings, parent=None, client_factory=ApiClient):
        super().__init__(parent)
        self.settings = settings
        self.client_factory = client_factory
        self.client = None
        self.setWindowTitle("Giriş")
        self.setMinimumWidth(420)

        self.server = QLineEdit(settings.server)
        self.server.setPlaceholderText("https://ornek.onrender.com")
        self.username = QLineEdit(settings.username)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.remember = QCheckBox("Bu bilgisayarda oturumu hatırla")
        keyring_ok = token_store.available()
        self.remember.setChecked(settings.remember and keyring_ok)
        self.remember.setEnabled(keyring_ok)
        if not keyring_ok:
            self.remember.setToolTip("Bu sistemde güvenli anahtar zinciri bulunamadı.")

        self.error = label("", "error", wrap=True)
        self.error.hide()
        self.submit = button("Giriş yap", "primary", self.try_login)
        self.submit.setDefault(True)

        form = QFormLayout()
        form.addRow("Sunucu adresi", self.server)
        form.addRow("Kullanıcı adı", self.username)
        form.addRow("Şifre", self.password)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(label("Çağrı ekranına giriş", "title"))
        layout.addWidget(label("Web panelindeki işletme hesabınızla giriş yapın.", "muted", wrap=True))
        layout.addLayout(form)
        layout.addWidget(self.remember)
        layout.addWidget(self.error)
        layout.addWidget(self.submit)
        register = button("Hesabınız yok mu? Web'den kayıt olun", "ghost", self.open_register)
        layout.addWidget(register, alignment=Qt.AlignmentFlag.AlignLeft)

        (self.password if settings.username else self.username).setFocus()

    def show_error(self, text):
        self.error.setText(text)
        self.error.show()

    def open_register(self):
        try:
            url = validate_server_url(self.server.text())
        except ValueError as exc:
            self.show_error(str(exc))
            return
        QDesktopServices.openUrl(QUrl(f"{url}/panel/kayit"))

    def try_login(self):
        try:
            server = validate_server_url(self.server.text())
        except ValueError as exc:
            self.show_error(str(exc))
            return
        username = self.username.text().strip()
        if not username or not self.password.text():
            self.show_error("Kullanıcı adı ve şifre gerekli.")
            return

        self.error.hide()
        self.submit.setEnabled(False)
        self.submit.setText("Giriş yapılıyor…")
        client = self.client_factory(server)
        password = self.password.text()

        def done(_user):
            self.password.clear()
            self.settings.server, self.settings.username = server, username
            self.settings.remember = self.remember.isChecked()
            self.settings.save()
            if self.settings.remember:
                token_store.save(server, username, client.tokens.refresh)
                client.on_refresh_token_changed = lambda t: token_store.save(server, username, t)
            else:
                token_store.save(server, username, None)
            self.client = client
            self.accept()

        def failed(exc):
            client.close()
            self.submit.setEnabled(True)
            self.submit.setText("Giriş yap")
            status = getattr(exc, "status", None)
            self.show_error("Kullanıcı adı ya da şifre hatalı." if status == 401 else error_text(exc))

        run_async(client.login, username, password, on_done=done, on_error=failed)
