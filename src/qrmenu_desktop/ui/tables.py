"""Masalar: ekle, QR'ı kaydet, sızan bir kodu yenile, tüm kartları PDF olarak kaydet."""

from pathlib import Path

from PySide6.QtCore import QStandardPaths, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..tasks import run_async
from .common import button, confirm, label, show_error, table_name


def documents_dir() -> str:
    return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)


class TablesView(QWidget):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.slug = None
        self.tables: list[dict] = []

        self.list = QListWidget()
        self.list.setAccessibleName("Masalar")
        self.list.currentRowChanged.connect(self._select)
        self.preview = label("")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(240, 240)
        self.preview.setAccessibleName("Seçili masanın QR kodu")
        self.selected_title = label("", "title")

        self.new_label = QLineEdit()
        self.new_label.setPlaceholderText("Yeni masa: örn. 12 ya da Bahçe 3")
        self.new_label.setMaxLength(20)
        self.new_label.returnPressed.connect(self.add_table)

        self.save_png = button("QR'ı kaydet (PNG)", None, self.save_qr)
        self.regenerate = button(
            "Yeni QR üret", None, self.regenerate_token, "Basılı eski kod artık çalışmaz"
        )
        self.remove = button("Masayı sil", "danger", self.delete_table)

        add_row = QHBoxLayout()
        add_row.addWidget(self.new_label, 1)
        add_row.addWidget(button("Ekle", None, self.add_table))

        left = QVBoxLayout()
        left.addLayout(add_row)
        left.addWidget(self.list, 1)

        right = QVBoxLayout()
        right.addWidget(self.selected_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        right.addWidget(self.preview, 1)
        actions = QHBoxLayout()
        for b in (self.save_png, self.regenerate, self.remove):
            actions.addWidget(b)
        right.addLayout(actions)

        body = QHBoxLayout()
        body.addLayout(left, 2)
        body.addLayout(right, 3)

        head = QHBoxLayout()
        head.addWidget(label("Masalar ve QR kodlar", "title"), 1)
        head.addWidget(button("Tüm masa kartlarını PDF kaydet", "primary", self.save_pdf))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        layout.addLayout(head)
        layout.addWidget(
            label(
                "Her masanın kodu menüyü o masaya özel açar; müşteri garson çağırdığında masa adı bu ekrana gelir.",
                "muted",
                wrap=True,
            )
        )
        layout.addLayout(body, 1)
        self._update_buttons()

    def set_business(self, slug):
        self.slug = slug
        self.reload()

    def reload(self, select_id=None):
        if self.slug:
            run_async(
                self.api.tables,
                self.slug,
                on_done=lambda t: self._loaded(t, select_id),
                on_error=lambda e: show_error(self, e),
            )

    def _loaded(self, tables, select_id=None):
        self.tables = tables
        self.list.clear()
        for t in tables:
            item = QListWidgetItem(table_name(t["label"]))
            item.setData(Qt.ItemDataRole.UserRole, t["id"])
            self.list.addItem(item)
        index = next((i for i, t in enumerate(tables) if t["id"] == select_id), 0 if tables else -1)
        self.list.setCurrentRow(index)
        self._update_buttons()

    def current(self):
        row = self.list.currentRow()
        return self.tables[row] if 0 <= row < len(self.tables) else None

    def _update_buttons(self):
        has = self.current() is not None
        for b in (self.save_png, self.regenerate, self.remove):
            b.setEnabled(has)
        if not has:
            self.preview.clear()
            self.selected_title.setText("")

    def _select(self, _row):
        table = self.current()
        self._update_buttons()
        if not table:
            return
        self.selected_title.setText(table_name(table["label"]))
        self.preview.setText("QR yükleniyor…")
        run_async(
            self.api.table_qr_png,
            table["id"],
            on_done=lambda data, tid=table["id"]: self._show_qr(tid, data),
            on_error=lambda e: self.preview.setText("QR yüklenemedi."),
        )

    def _show_qr(self, table_id, data):
        if (self.current() or {}).get("id") != table_id:
            return
        pix = QPixmap()
        pix.loadFromData(data, "PNG")
        self.preview.setPixmap(pix.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio))

    def add_table(self):
        text = self.new_label.text().strip()
        if not text or not self.slug:
            return
        self.new_label.clear()
        run_async(
            self.api.create_table,
            self.slug,
            text,
            len(self.tables),
            on_done=lambda t: self.reload(t["id"]),
            on_error=lambda e: show_error(self, e),
        )

    def regenerate_token(self):
        table = self.current()
        if table and confirm(
            self,
            "Yeni QR üret",
            f"{table_name(table['label'])} için yeni QR kod üretilsin mi? Basılı eski kod artık çalışmaz.",
            "Yeni kod üret",
        ):
            run_async(
                self.api.regenerate_table,
                table["id"],
                on_done=lambda t: self.reload(t["id"]),
                on_error=lambda e: show_error(self, e),
            )

    def delete_table(self):
        table = self.current()
        if table and confirm(self, "Masayı sil", f"{table_name(table['label'])} silinsin mi?", "Sil"):
            run_async(
                self.api.delete_table,
                table["id"],
                on_done=lambda _: self.reload(),
                on_error=lambda e: show_error(self, e),
            )

    def _save(self, title, default_name, file_filter, fetch, *args):
        path, _ = QFileDialog.getSaveFileName(
            self, title, str(Path(documents_dir()) / default_name), file_filter
        )
        if not path:
            return

        def write(data):
            Path(path).write_bytes(data)
            self.window().statusBar().showMessage(f"Kaydedildi: {path}", 6000)

        run_async(fetch, *args, on_done=write, on_error=lambda e: show_error(self, e))

    def save_qr(self):
        table = self.current()
        if table:
            name = f"{self.slug}-{table_name(table['label']).lower().replace(' ', '-')}.png"
            self._save("QR kodunu kaydet", name, "PNG (*.png)", self.api.table_qr_png, table["id"])

    def save_pdf(self):
        if self.slug:
            self._save(
                "Masa kartlarını kaydet",
                f"{self.slug}-masalar.pdf",
                "PDF (*.pdf)",
                self.api.table_cards_pdf,
                self.slug,
            )
