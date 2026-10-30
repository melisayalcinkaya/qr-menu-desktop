"""Görünümlerde tekrar eden küçük yardımcılar."""

from datetime import UTC, datetime

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton

from ..api import ApiError, SessionExpiredError


def table_name(label: str) -> str:
    """'5' -> 'Masa 5', 'Bahçe 1' -> 'Bahçe 1' (web ile aynı kural)."""
    return f"Masa {label}" if str(label).strip().isdigit() else str(label)


def parse_time(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def time_ago(iso: str, now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    seconds = max(0, int((now - parse_time(iso)).total_seconds()))
    if seconds < 60:
        return "az önce"
    if seconds < 3600:
        return f"{seconds // 60} dk önce"
    if seconds < 86400:
        return f"{seconds // 3600} sa önce"
    return parse_time(iso).astimezone().strftime("%d.%m %H:%M")


def button(text, kind=None, on_click=None, tooltip=None) -> QPushButton:
    btn = QPushButton(text)
    if kind:
        btn.setProperty("kind", kind)
    if on_click:
        btn.clicked.connect(on_click)
    if tooltip:
        btn.setToolTip(tooltip)
        btn.setAccessibleDescription(tooltip)
    return btn


def label(text, role=None, wrap=False) -> QLabel:
    lbl = QLabel(text)
    if role:
        lbl.setProperty("role", role)
    lbl.setWordWrap(wrap)
    return lbl


def error_text(exc: Exception) -> str:
    if isinstance(exc, ApiError):
        return exc.message
    return f"Beklenmeyen hata: {exc}"


def show_error(parent, exc: Exception, title="İşlem tamamlanamadı"):
    if isinstance(exc, SessionExpiredError):
        return  # ana pencere oturum sonu sinyaliyle ilgilenir
    QMessageBox.warning(parent, title, error_text(exc))


def confirm(parent, title, text, yes="Evet") -> bool:
    box = QMessageBox(QMessageBox.Icon.Question, title, text, parent=parent)
    ok = box.addButton(yes, QMessageBox.ButtonRole.AcceptRole)
    box.addButton("Vazgeç", QMessageBox.ButtonRole.RejectRole)
    box.exec()
    return box.clickedButton() is ok
