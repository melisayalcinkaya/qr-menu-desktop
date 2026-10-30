import sys

from PySide6.QtWidgets import QApplication, QDialog

from . import APP_NAME, ORG_NAME, __version__, token_store
from .api import ApiClient, SessionExpiredError
from .settings import AppSettings
from .ui.login import LoginDialog
from .ui.main_window import MainWindow
from .ui.style import app_icon, stylesheet


def try_resume(settings: AppSettings):
    """Anahtar zincirinde geçerli bir oturum varsa giriş ekranını atla."""
    if not (settings.remember and settings.username):
        return None
    token = token_store.load(settings.server, settings.username)
    if not token:
        return None
    try:
        client = ApiClient(settings.server)
        client.resume(token)
    except SessionExpiredError:
        token_store.save(settings.server, settings.username, None)
        return None
    except Exception:  # noqa: BLE001 - sunucuya ulaşılamazsa giriş ekranı açılır
        return None
    token_store.save(settings.server, settings.username, client.tokens.refresh)
    client.on_refresh_token_changed = lambda t: token_store.save(settings.server, settings.username, t)
    return client


class App:
    def __init__(self, qapp):
        self.qapp = qapp
        self.settings = AppSettings.load()
        self.window = None

    def start(self):
        client = try_resume(self.settings)
        if client is None:
            dialog = LoginDialog(self.settings)
            dialog.setWindowIcon(app_icon())
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return False
            client = dialog.client
        self.window = MainWindow(client, self.settings)
        self.window.logged_out.connect(self.restart)
        self.window.show()
        return True

    def restart(self):
        old = self.window
        token_store.save(self.settings.server, self.settings.username, None)
        old.quitting = old.restarting = True
        old.close()
        old.api.close()
        old.deleteLater()
        if not self.start():
            self.qapp.quit()


def main(argv=None):
    qapp = QApplication(argv or sys.argv)
    qapp.setOrganizationName(ORG_NAME)
    qapp.setApplicationName(APP_NAME)
    qapp.setApplicationVersion(__version__)
    qapp.setWindowIcon(app_icon())
    qapp.setStyle("Fusion")  # tüm platformlarda tutarlı görünüm, stil sayfası üzerine kurulur
    qapp.setStyleSheet(stylesheet())
    qapp.setQuitOnLastWindowClosed(False)  # pencere tepsiye gizlenince uygulama kapanmasın
    app = App(qapp)
    if not app.start():
        return 0
    return qapp.exec()
