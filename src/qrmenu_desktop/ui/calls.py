"""Canlı garson çağrısı panosu (kasa / mutfak ekranı)."""

from datetime import UTC, datetime

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..api import SessionExpiredError
from ..tasks import run_async
from .common import button, error_text, label, show_error, table_name, time_ago
from .style import repolish, set_role

TILE_WIDTH = 280


class CallTile(QFrame):
    closed = Signal(dict, str)  # çağrı, "complete" | "cancel"

    def __init__(self, call: dict, fresh=False):
        super().__init__()
        self.call = call
        set_role(self, "call", fresh="true" if fresh else "false")
        self.setMinimumWidth(TILE_WIDTH - 20)
        name = table_name(call["table_label"])
        self.setAccessibleName(f"{name} garson çağırıyor")

        self.age = label("", "age")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)
        layout.addWidget(label(name, "table"))
        layout.addWidget(self.age)
        if call.get("note"):
            layout.addWidget(label(f"“{call['note']}”", "note", wrap=True))
        layout.addStretch()
        actions = QHBoxLayout()
        done = button("Tamamlandı", "big", lambda: self.closed.emit(self.call, "complete"))
        done.setAccessibleName(f"{name} çağrısını tamamla")
        cancel = button("İptal", "ghost", lambda: self.closed.emit(self.call, "cancel"))
        cancel.setAccessibleName(f"{name} çağrısını iptal et")
        actions.addWidget(done, 1)
        actions.addWidget(cancel)
        layout.addLayout(actions)
        self.refresh_age()

    def refresh_age(self, now=None):
        self.age.setText(time_ago(self.call["created_at"], now))

    def settle(self):
        """Yeni çağrı vurgusunu kaldır."""
        self.setProperty("fresh", "false")
        repolish(self)


class CallsView(QWidget):
    new_calls = Signal(list)  # yeni gelen çağrılar (bildirim ve ses için)
    count_changed = Signal(int)
    connection_changed = Signal(bool)
    session_expired = Signal()

    def __init__(self, api, poll_seconds=5, parent=None):
        super().__init__(parent)
        self.api = api
        self.slug = None
        self.calls: list[dict] = []
        self.known_ids: set | None = None  # ilk yüklemede "yeni" bildirimi yapılmaz
        self.tiles: dict[int, CallTile] = {}
        self._busy = False
        self._closing: set[int] = set()

        self.title = label("Bekleyen çağrılar", "title")
        self.banner = label("", "banner", wrap=True)
        self.banner.hide()
        self.empty = label(
            "Şu an bekleyen çağrı yok. Müşteri masadaki QR koddan “Garson çağır”a "
            "bastığında burada görünür ve bildirim gelir.",
            "muted",
            wrap=True,
        )

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setSpacing(14)
        self.grid.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.grid_host)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addWidget(self.banner)
        layout.addWidget(self.empty)
        layout.addWidget(scroll, 1)

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll)
        self.set_interval(poll_seconds)
        self.age_timer = QTimer(self)
        self.age_timer.timeout.connect(self._refresh_ages)
        self.age_timer.start(15_000)

    # --- Yükleme ---------------------------------------------------------

    def set_interval(self, seconds):
        self.poll_timer.setInterval(int(seconds) * 1000)

    def set_business(self, slug):
        self.slug = slug
        self.known_ids = None
        self.calls = []
        self._render()
        self.poll()
        self.poll_timer.start()

    def stop(self):
        self.poll_timer.stop()

    def poll(self):
        if not self.slug or self._busy:
            return  # önceki istek sürüyorsa üst üste binmesin
        self._busy = True
        slug = self.slug
        run_async(
            self.api.pending_calls,
            slug,
            on_done=lambda calls: self._loaded(slug, calls),
            on_error=self._failed,
        )

    def _loaded(self, slug, calls):
        self._busy = False
        if slug != self.slug:
            return  # bu arada işletme değişti
        self.banner.hide()
        self.connection_changed.emit(True)
        calls = [c for c in calls if c["id"] not in self._closing]
        ids = {c["id"] for c in calls}
        fresh = [] if self.known_ids is None else [c for c in calls if c["id"] not in self.known_ids]
        self.known_ids = ids
        self.calls = sorted(calls, key=lambda c: c["created_at"])  # en uzun bekleyen önce
        self._render(fresh_ids={c["id"] for c in fresh})
        if fresh:
            self.new_calls.emit(fresh)

    def _failed(self, exc):
        self._busy = False
        if isinstance(exc, SessionExpiredError):
            self.stop()
            self.session_expired.emit()
            return
        self.connection_changed.emit(False)
        seconds = self.poll_timer.interval() // 1000
        self.banner.setText(
            f"Çağrılar güncellenemiyor: {error_text(exc)} {seconds} sn sonra tekrar denenecek."
        )
        self.banner.show()

    # --- Çizim -----------------------------------------------------------

    def _render(self, fresh_ids=frozenset()):
        for call_id in list(self.tiles):
            if call_id not in {c["id"] for c in self.calls}:
                self.tiles.pop(call_id).deleteLater()
        for call in self.calls:
            if call["id"] not in self.tiles:
                tile = CallTile(call, fresh=call["id"] in fresh_ids)
                tile.closed.connect(self.close_call)
                self.tiles[call["id"]] = tile
                if call["id"] in fresh_ids:
                    QTimer.singleShot(6000, tile.settle)
        self._relayout()
        self.empty.setVisible(not self.calls)
        self.title.setText(f"Bekleyen çağrılar ({len(self.calls)})" if self.calls else "Bekleyen çağrılar")
        self.count_changed.emit(len(self.calls))

    def _relayout(self):
        while self.grid.count():
            self.grid.takeAt(0)
        columns = max(1, self.width() // TILE_WIDTH)
        for index, call in enumerate(self.calls):
            self.grid.addWidget(self.tiles[call["id"]], index // columns, index % columns)
        self.grid.setRowStretch(self.grid.rowCount(), 1)
        for col in range(columns):
            self.grid.setColumnStretch(col, 1)

    def resizeEvent(self, event):  # noqa: N802 - Qt adı
        super().resizeEvent(event)
        self._relayout()

    def _refresh_ages(self):
        now = datetime.now(UTC)
        for tile in self.tiles.values():
            tile.refresh_age(now)

    # --- Kapatma ---------------------------------------------------------

    def close_call(self, call, action):
        """İyimser güncelleme: kart hemen kalkar, istek başarısız olursa geri gelir."""
        self._closing.add(call["id"])
        self.calls = [c for c in self.calls if c["id"] != call["id"]]
        self._render()

        def done(_):
            self._closing.discard(call["id"])

        def failed(exc):
            self._closing.discard(call["id"])
            if getattr(exc, "status", None) == 409:
                return  # başka bir ekrandan zaten kapatılmış
            self.calls = sorted([*self.calls, call], key=lambda c: c["created_at"])
            self._render()
            show_error(self, exc)

        run_async(self.api.close_call, call["id"], action, on_done=done, on_error=failed)
