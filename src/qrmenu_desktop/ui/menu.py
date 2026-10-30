"""Menü: mutfakta en sık gereken işlem bir ürünü 'tükendi' diye menüden gizlemek."""

from decimal import Decimal, InvalidOperation

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..tasks import run_async
from .common import button, label, show_error


def format_price(value) -> str:
    amount = Decimal(str(value))
    text = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"₺{text.removesuffix(',00')}"


class MenuView(QWidget):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.slug = None
        self.meta = None
        self.categories: list[dict] = []
        self.products: list[dict] = []

        self.category_list = QListWidget()
        self.category_list.setAccessibleName("Kategoriler")
        self.category_list.currentRowChanged.connect(self._show_products)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Ürün", "Fiyat", "Menüde", "Sevilen"])
        self.table.setAccessibleName("Ürünler")
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(42)  # dokunmatik ekranda rahat basılsın
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(lambda row, _c: self.edit_product(row))

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        tools = QHBoxLayout()
        tools.addWidget(
            label("“Menüde” kutusunu kaldırınca ürün müşteri menüsünden anında kalkar.", "muted", wrap=True),
            1,
        )
        tools.addWidget(
            button("Seçili ürünü düzenle", None, lambda: self.edit_product(self.table.currentRow()))
        )
        right_layout.addLayout(tools)
        right_layout.addWidget(self.table, 1)

        splitter = QSplitter()
        splitter.addWidget(self.category_list)
        splitter.addWidget(right)
        splitter.setSizes([220, 700])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        head = QHBoxLayout()
        head.addWidget(label("Menü", "title"), 1)
        head.addWidget(button("Yenile", None, self.reload))
        layout.addLayout(head)
        layout.addWidget(splitter, 1)

    def set_business(self, slug):
        self.slug = slug
        self.reload()

    def reload(self):
        if not self.slug:
            return
        slug = self.slug

        def load():
            meta = self.meta or self.api.meta()
            return meta, self.api.categories(slug), self.api.products(slug)

        run_async(load, on_done=self._loaded, on_error=lambda e: show_error(self, e))

    def _loaded(self, result):
        self.meta, self.categories, self.products = result
        row = max(0, self.category_list.currentRow())
        self.category_list.blockSignals(True)
        self.category_list.clear()
        for c in self.categories:
            count = sum(1 for p in self.products if p["category"] == c["id"])
            item = QListWidgetItem(f"{c['name']}  ({count})")
            self.category_list.addItem(item)
        self.category_list.blockSignals(False)
        if self.categories:
            self.category_list.setCurrentRow(min(row, len(self.categories) - 1))
            self._show_products(self.category_list.currentRow())

    def _current_products(self):
        row = self.category_list.currentRow()
        if row < 0 or row >= len(self.categories):
            return []
        cid = self.categories[row]["id"]
        return [p for p in self.products if p["category"] == cid]

    def _show_products(self, _row=None):
        products = self._current_products()
        self.table.setRowCount(len(products))
        for r, p in enumerate(products):
            name = QTableWidgetItem(p["name"])
            name.setData(Qt.ItemDataRole.UserRole, p["id"])
            self.table.setItem(r, 0, name)
            price = QTableWidgetItem(format_price(p["price"]))
            price.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 1, price)
            self.table.setCellWidget(r, 2, self._check(p, "is_active", f"{p['name']} menüde görünsün"))
            self.table.setCellWidget(
                r, 3, self._check(p, "is_popular", f"{p['name']} sevilen olarak işaretlensin")
            )

    def _check(self, product, field, accessible):
        holder = QWidget()
        box = QCheckBox()
        box.setChecked(bool(product[field]))
        box.setAccessibleName(accessible)
        box.toggled.connect(lambda on: self.set_flag(product, field, on))
        lay = QHBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(box, alignment=Qt.AlignmentFlag.AlignCenter)
        return holder

    def set_flag(self, product, field, value):
        product[field] = value

        def failed(exc):
            product[field] = not value
            self._show_products()
            show_error(self, exc)

        run_async(self.api.update_product, product["id"], {field: value}, on_error=failed)

    def edit_product(self, row):
        products = self._current_products()
        if not 0 <= row < len(products):
            return
        product = products[row]
        dialog = ProductDialog(product, self.meta, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        run_async(
            self.api.update_product,
            product["id"],
            dialog.values(),
            on_done=lambda _: self.reload(),
            on_error=lambda e: show_error(self, e),
        )


class ProductDialog(QDialog):
    def __init__(self, product, meta, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{product['name']} düzenle")
        self.setMinimumWidth(520)
        self.name = QLineEdit(product["name"])
        self.name_en = QLineEdit(product.get("name_en", ""))
        self.price = QLineEdit(str(product["price"]))
        self.price.setAccessibleName("Fiyat")
        self.description = QPlainTextEdit(product.get("description", ""))
        self.description.setFixedHeight(70)
        self.active = QCheckBox("Menüde göster")
        self.active.setChecked(product["is_active"])
        self.popular = QCheckBox("“Sevilen” etiketi")
        self.popular.setChecked(product["is_popular"])
        self.error = label("", "error")
        self.error.hide()

        self.allergen_boxes = {}
        group = QGroupBox("Alerjenler")
        grid = QGridLayout(group)
        for i, item in enumerate((meta or {}).get("allergens", [])):
            box = QCheckBox(item["tr"])
            box.setChecked(item["code"] in product["allergens"])
            self.allergen_boxes[item["code"]] = box
            grid.addWidget(box, i // 3, i % 3)

        form = QFormLayout()
        form.addRow("Ad", self.name)
        form.addRow("İngilizce ad", self.name_en)
        form.addRow("Fiyat (₺)", self.price)
        form.addRow("Açıklama", self.description)
        buttons = QDialogButtonBox()
        buttons.addButton("Kaydet", QDialogButtonBox.ButtonRole.AcceptRole).setProperty("kind", "primary")
        buttons.addButton("Vazgeç", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        flags = QHBoxLayout()
        flags.addWidget(self.active)
        flags.addWidget(self.popular)
        flags.addStretch()
        layout.addLayout(flags)
        layout.addWidget(group)
        layout.addWidget(self.error)
        layout.addWidget(buttons)

    def _validate(self):
        try:
            price = Decimal(self.price.text().replace(",", ".").strip())
            if price < 0:
                raise InvalidOperation
        except InvalidOperation:
            self.error.setText("Geçerli bir fiyat girin (örn. 95 ya da 95,50).")
            self.error.show()
            return
        if not self.name.text().strip():
            self.error.setText("Ürün adı boş olamaz.")
            self.error.show()
            return
        self.accept()

    def values(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "name_en": self.name_en.text().strip(),
            "price": str(Decimal(self.price.text().replace(",", ".").strip())),
            "description": self.description.toPlainText().strip(),
            "is_active": self.active.isChecked(),
            "is_popular": self.popular.isChecked(),
            "allergens": [code for code, box in self.allergen_boxes.items() if box.isChecked()],
        }
