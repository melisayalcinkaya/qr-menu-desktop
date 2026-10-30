from PySide6.QtCore import QSize, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QStackedWidget,
    QSystemTrayIcon,
    QWidget,
)

from .. import APP_NAME, sound
from ..tasks import run_async
from .calls import CallsView
from .comments import CommentsView
from .common import show_error, table_name
from .menu import MenuView
from .settings_dialog import SettingsDialog
from .style import app_icon
from .tables import TablesView

PAGES = ["Garson çağrıları", "Menü", "Masalar ve QR", "Yorumlar"]


class MainWindow(QMainWindow):
    logged_out = Signal()

    def __init__(self, api, settings, parent=None):
        super().__init__(parent)
        self.api = api
        self.settings = settings
        self.quitting = False
        self.restarting = False  # çıkış yapıp giriş ekranına dönerken uygulama kapanmasın
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(app_icon())
        self.resize(1200, 780)

        self.calls = CallsView(api, settings.poll_seconds)
        self.menu = MenuView(api)
        self.tables = TablesView(api)
        self.comments = CommentsView(api)
        self.views = [self.calls, self.menu, self.tables, self.comments]

        self.nav = QListWidget()
        self.nav.setObjectName("nav")
        self.nav.setFixedWidth(230)
        self.nav.setAccessibleName("Bölümler")
        for title in PAGES:
            self.nav.addItem(QListWidgetItem(title))
        self.stack = QStackedWidget()
        for view in self.views:
            self.stack.addWidget(view)
        self.nav.currentRowChanged.connect(self._switch)

        central = QWidget()
        row = QHBoxLayout(central)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(self.nav)
        row.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self._build_toolbar()
        self._build_tray()

        self.calls.new_calls.connect(self.announce)
        self.calls.count_changed.connect(lambda n: self._set_badge(0, n))
        self.calls.connection_changed.connect(self._connection)
        self.calls.session_expired.connect(self.session_expired)
        self.comments.pending_changed.connect(lambda n: self._set_badge(3, n))

        self.statusBar().showMessage(f"{api.tokens.user.get('username', '')} olarak bağlı: {api.base_url}")
        self.nav.setCurrentRow(0)
        self.load_businesses()

    # --- Kurulum ---------------------------------------------------------

    def _build_toolbar(self):
        bar = self.addToolBar("Araçlar")
        bar.setMovable(False)
        bar.setIconSize(QSize(18, 18))
        self.business_box = QComboBox()
        self.business_box.setMinimumWidth(240)
        self.business_box.setAccessibleName("İşletme")
        self.business_box.currentIndexChanged.connect(self._business_changed)
        bar.addWidget(self.business_box)
        bar.addSeparator()

        self.sound_action = QAction("Zil sesi", self, checkable=True, checked=self.settings.sound)
        self.sound_action.toggled.connect(self._toggle_sound)
        bar.addAction(self.sound_action)

        full = QAction("Tam ekran", self, shortcut=QKeySequence(Qt.Key.Key_F11))
        full.triggered.connect(self.toggle_fullscreen)
        bar.addAction(full)
        refresh = QAction("Yenile", self, shortcut=QKeySequence.StandardKey.Refresh)
        refresh.triggered.connect(self.refresh_current)
        bar.addAction(refresh)
        web = QAction("Web paneli", self)
        web.triggered.connect(self.open_web)
        bar.addAction(web)
        settings = QAction("Ayarlar", self)
        settings.triggered.connect(self.open_settings)
        bar.addAction(settings)
        logout = QAction("Çıkış", self)
        logout.triggered.connect(self.logout)
        bar.addAction(logout)

    def _build_tray(self):
        self.tray = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(app_icon(), self)
        self.tray.setToolTip(APP_NAME)
        menu = QMenu()
        menu.addAction("Göster", self.bring_to_front)
        menu.addAction("Kapat", self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: reason == QSystemTrayIcon.ActivationReason.Trigger and self.bring_to_front()
        )
        self.tray.messageClicked.connect(self.bring_to_front)
        self.tray.show()

    # --- İşletme ---------------------------------------------------------

    def load_businesses(self):
        run_async(self.api.businesses, on_done=self._businesses_loaded, on_error=self._load_failed)

    def _load_failed(self, exc):
        show_error(self, exc, "İşletmeler yüklenemedi")

    def _businesses_loaded(self, items):
        self.business_box.blockSignals(True)
        self.business_box.clear()
        for b in items:
            self.business_box.addItem(b["name"], b["slug"])
        self.business_box.blockSignals(False)
        if not items:
            self.statusBar().showMessage("Bu hesapta işletme yok. Web panelinden bir işletme oluşturun.")
            return
        index = max(0, self.business_box.findData(self.settings.business))
        self.business_box.setCurrentIndex(index)
        self._business_changed(index)

    def _business_changed(self, index):
        slug = self.business_box.itemData(index)
        if not slug:
            return
        self.settings.business = slug
        self.settings.save()
        for view in self.views:
            view.set_business(slug)

    # --- Bildirimler -------------------------------------------------------

    def announce(self, calls):
        names = ", ".join(table_name(c["table_label"]) for c in calls)
        text = f"{names} garson çağırıyor"
        note = next((c["note"] for c in calls if c.get("note")), "")
        if self.settings.sound:
            sound.play_chime()
        if self.settings.notifications and self.tray:
            self.tray.showMessage(
                "Garson çağrısı", f"{text}\n{note}".strip(), QSystemTrayIcon.MessageIcon.Information, 8000
            )
        QApplication.alert(self, 0)  # görev çubuğunda yanıp sönsün
        self.statusBar().showMessage(text, 10000)

    def _set_badge(self, row, count):
        title = PAGES[row]
        self.nav.item(row).setText(f"{title}  ({count})" if count else title)
        if row == 0:
            self.setWindowTitle(f"({count}) {APP_NAME}" if count else APP_NAME)
            if self.tray:
                self.tray.setToolTip(f"{APP_NAME}: {count} bekleyen çağrı" if count else APP_NAME)

    def _connection(self, ok):
        if not ok:
            self.statusBar().showMessage("Sunucuya ulaşılamıyor, yeniden deneniyor…")

    # --- Eylemler ----------------------------------------------------------

    def _switch(self, row):
        self.stack.setCurrentIndex(row)
        if row > 0:
            self.views[row].reload()

    def refresh_current(self):
        view = self.views[self.stack.currentIndex()]
        (view.poll if view is self.calls else view.reload)()

    def _toggle_sound(self, on):
        self.settings.sound = on
        self.settings.save()
        if on:
            sound.play_chime()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def open_web(self):
        slug = self.business_box.currentData() or ""
        QDesktopServices.openUrl(QUrl(f"{self.api.base_url}/panel/{slug}"))

    def open_settings(self):
        if SettingsDialog(self.settings, self).exec():
            self.calls.set_interval(self.settings.poll_seconds)
            self.sound_action.setChecked(self.settings.sound)

    def bring_to_front(self):
        self.showNormal() if self.isMinimized() or not self.isVisible() else None
        self.raise_()
        self.activateWindow()

    def session_expired(self):
        self.calls.stop()
        self.logged_out.emit()

    def logout(self):
        self.calls.stop()
        run_async(
            self.api.logout,
            on_done=lambda _: self.logged_out.emit(),
            on_error=lambda _: self.logged_out.emit(),
        )

    def quit_app(self):
        self.quitting = True
        self.close()
        QApplication.quit()

    def closeEvent(self, event):  # noqa: N802 - Qt adı
        # Kasa ekranında pencere kapatılsa bile çağrılar kaçmasın: tepside çalışmaya devam et
        if self.tray and not self.quitting:
            event.ignore()
            self.hide()
            self.tray.showMessage(
                APP_NAME, "Çağrı ekranı arka planda çalışıyor. Kapatmak için tepsi simgesine sağ tıklayın."
            )
            return
        self.calls.stop()
        if self.tray:
            self.tray.hide()
        super().closeEvent(event)
        if not self.restarting:
            QApplication.quit()
