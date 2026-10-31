"""Uygulama stili. Web panelinin renkleriyle aynı aile: petrol yeşili ve kehribar.

Çağrı ekranı genellikle uzaktan, ayakta bakılan bir ekrandır; bu yüzden masa adları
iri, düğmeler büyük ve dokunmatik ekranda rahat basılacak boyuttadır.
"""

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPixmap

LIGHT = {
    "bg": "#f4f5f3",
    "surface": "#ffffff",
    "ink": "#16191d",
    "muted": "#5d6570",
    "line": "#dfe3e5",
    "primary": "#0f6e6e",
    "primary_ink": "#ffffff",
    "primary_soft": "#dcefed",
    "amber": "#b86e00",
    "amber_soft": "#fdf0d9",
    "danger": "#b42318",
}
DARK = {
    "bg": "#131618",
    "surface": "#1b1f22",
    "ink": "#e9ecee",
    "muted": "#9aa3ad",
    "line": "#2c3236",
    "primary": "#3fb5ae",
    "primary_ink": "#0b1a19",
    "primary_soft": "#173533",
    "amber": "#f2b552",
    "amber_soft": "#3a2c14",
    "danger": "#f97066",
}


def is_dark() -> bool:
    hints = QGuiApplication.styleHints()
    return hasattr(hints, "colorScheme") and hints.colorScheme() == Qt.ColorScheme.Dark


def palette() -> dict:
    return DARK if is_dark() else LIGHT


def stylesheet(c: dict | None = None) -> str:
    c = c or palette()
    return f"""
    QWidget {{ background: {c["bg"]}; color: {c["ink"]}; font-size: 14px; }}
    QMainWindow, QDialog {{ background: {c["bg"]}; }}
    QLabel {{ background: transparent; }}
    QLabel[role="title"] {{ font-size: 24px; font-weight: 700; }}
    QLabel[role="muted"] {{ color: {c["muted"]}; }}
    QLabel[role="error"] {{ color: {c["danger"]}; font-weight: 600; }}
    QLabel[role="banner"] {{ background: {c["amber_soft"]}; border: 1px solid {c["amber"]};
        border-radius: 8px; padding: 8px 12px; font-weight: 600; }}

    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit {{
        background: {c["surface"]}; border: 1px solid {c["line"]}; border-radius: 8px;
        padding: 7px 10px; min-height: 22px; }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QPlainTextEdit:focus {{
        border: 2px solid {c["primary"]}; }}

    QPushButton {{ background: {c["surface"]}; border: 1px solid {c["line"]}; border-radius: 8px;
        padding: 8px 14px; font-weight: 600; }}
    QPushButton:hover {{ border-color: {c["muted"]}; }}
    QPushButton:focus {{ border: 2px solid {c["primary"]}; }}
    QPushButton:disabled {{ color: {c["muted"]}; }}
    QPushButton[kind="primary"] {{ background: {c["primary"]}; color: {c["primary_ink"]};
        border-color: {c["primary"]}; }}
    QPushButton[kind="danger"] {{ color: {c["danger"]}; }}
    QPushButton[kind="big"] {{ background: {c["primary"]}; color: {c["primary_ink"]};
        border: 0; font-size: 18px; padding: 14px 18px; border-radius: 12px; }}
    QPushButton[kind="ghost"] {{ background: transparent; border-color: transparent; }}
    QPushButton:checked {{ background: {c["primary_soft"]}; border-color: {c["primary"]}; }}

    QListWidget#nav {{ background: {c["surface"]}; border: 0; border-right: 1px solid {c["line"]};
        padding: 8px; font-size: 15px; outline: 0; }}
    QListWidget#nav::item {{ padding: 12px 10px; border-radius: 8px; margin: 1px 0; }}
    QListWidget#nav::item:selected {{ background: {c["primary_soft"]}; color: {c["ink"]}; }}
    QListWidget#nav::item:hover:!selected {{ background: {c["bg"]}; }}

    QFrame[role="card"] {{ background: {c["surface"]}; border: 1px solid {c["line"]};
        border-radius: 12px; }}
    QFrame[role="call"] {{ background: {c["amber_soft"]}; border: 2px solid {c["amber"]};
        border-radius: 16px; }}
    QFrame[role="call"][fresh="true"] {{ border: 4px solid {c["amber"]}; }}
    QFrame[role="call"][kind="bill"] {{ background: {c["primary_soft"]}; border-color: {c["primary"]}; }}
    QFrame[role="call"][kind="bill"][fresh="true"] {{ border: 4px solid {c["primary"]}; }}
    QLabel[role="kind"] {{ color: {c["amber"]}; font-size: 14px; font-weight: 800; }}
    QFrame[role="call"][kind="bill"] QLabel[role="kind"] {{ color: {c["primary"]}; }}
    QLabel[role="table"] {{ font-size: 40px; font-weight: 800; }}
    QLabel[role="note"] {{ font-size: 18px; }}
    QLabel[role="age"] {{ color: {c["muted"]}; font-size: 15px; font-weight: 600; }}

    QTableWidget {{ background: {c["surface"]}; border: 1px solid {c["line"]}; border-radius: 10px;
        gridline-color: {c["line"]}; selection-background-color: {c["primary_soft"]};
        selection-color: {c["ink"]}; }}
    QHeaderView::section {{ background: {c["surface"]}; color: {c["muted"]}; border: 0;
        border-bottom: 1px solid {c["line"]}; padding: 8px; font-weight: 600; }}
    QListWidget {{ background: {c["surface"]}; border: 1px solid {c["line"]}; border-radius: 10px; }}
    QListWidget::item {{ padding: 8px; }}
    QListWidget::item:selected {{ background: {c["primary_soft"]}; color: {c["ink"]}; }}
    QTabBar::tab {{ padding: 8px 16px; border: 0; border-bottom: 3px solid transparent;
        color: {c["muted"]}; font-weight: 600; background: transparent; }}
    QTabBar::tab:selected {{ border-bottom-color: {c["primary"]}; color: {c["ink"]}; }}
    QTabWidget::pane {{ border: 0; }}
    QToolBar {{ background: {c["surface"]}; border: 0; border-bottom: 1px solid {c["line"]};
        padding: 6px; spacing: 8px; }}
    QStatusBar {{ background: {c["surface"]}; color: {c["muted"]}; }}
    QScrollArea {{ border: 0; }}
    QCheckBox {{ spacing: 8px; background: transparent; }}
    QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid {c["muted"]};
        border-radius: 5px; background: {c["surface"]}; }}
    QCheckBox::indicator:checked {{ background: {c["primary"]}; border-color: {c["primary"]}; }}
    QCheckBox::indicator:focus {{ border-color: {c["primary"]}; }}
    QToolButton {{ background: {c["surface"]}; border: 1px solid {c["line"]}; border-radius: 8px;
        padding: 6px 12px; font-weight: 600; }}
    QToolButton:hover {{ border-color: {c["muted"]}; }}
    QToolButton:checked {{ background: {c["primary_soft"]}; border-color: {c["primary"]}; }}
    """


def app_icon() -> QIcon:
    """Uygulama simgesi: petrol yeşili kare içinde sade bir QR deseni (dosya gerekmez)."""
    icon = QIcon()
    for size in (16, 32, 64, 128, 256):
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(LIGHT["primary"]))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRect(0, 0, size, size), size * 0.22, size * 0.22)
        p.setBrush(QColor("#ffffff"))
        u = size / 8
        for x, y in ((1.2, 1.2), (4.8, 1.2), (1.2, 4.8)):
            p.drawRect(QRect(QPoint(int(x * u), int(y * u)), QPoint(int((x + 2) * u), int((y + 2) * u))))
        p.drawRect(QRect(QPoint(int(5 * u), int(5 * u)), QPoint(int(6.8 * u), int(6.8 * u))))
        p.end()
        icon.addPixmap(pix)
    return icon


def set_role(widget, role, **props):
    widget.setProperty("role", role)
    for key, value in props.items():
        widget.setProperty(key, value)
    return widget


def repolish(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)
