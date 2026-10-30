"""Yorum moderasyonu: onay bekleyenleri yayınla ya da reddet."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QScrollArea, QTabBar, QVBoxLayout, QWidget

from ..tasks import run_async
from .common import button, confirm, label, show_error
from .style import set_role

TABS = [("pending", "Onay bekleyen"), ("approved", "Yayında"), ("rejected", "Reddedilen")]


class CommentsView(QWidget):
    pending_changed = Signal(int)

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.slug = None
        self.status = "pending"

        self.tabs = QTabBar()
        for _, text in TABS:
            self.tabs.addTab(text)
        self.tabs.currentChanged.connect(self._tab_changed)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setSpacing(10)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.body)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.addWidget(label("Yorumlar", "title"))
        layout.addWidget(
            label(
                "Yorumlar siz yayınlayana kadar menüde görünmez; metinleri değiştirilemez.",
                "muted",
                wrap=True,
            )
        )
        layout.addWidget(self.tabs)
        layout.addWidget(scroll, 1)

    def set_business(self, slug):
        self.slug = slug
        self.reload()

    def _tab_changed(self, index):
        self.status = TABS[index][0]
        self.reload()

    def reload(self):
        if self.slug:
            status = self.status
            run_async(
                self.api.comments,
                self.slug,
                status,
                on_done=lambda items: self._loaded(status, items),
                on_error=lambda e: show_error(self, e),
            )

    def _loaded(self, status, items):
        if status != self.status:
            return
        if status == "pending":
            self.pending_changed.emit(len(items))
        while self.body_layout.count():
            w = self.body_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        if not items:
            self.body_layout.addWidget(label("Bu bölümde yorum yok.", "muted"))
        for c in items:
            self.body_layout.addWidget(self._card(c))
        self.body_layout.addStretch()

    def _card(self, c):
        card = set_role(QFrame(), "card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        stars = "★" * c["rating"] + "☆" * (5 - c["rating"])
        head = label(f"{c['author_name'] or 'Misafir'}    {stars}")
        head.setAccessibleName(f"{c['author_name'] or 'Misafir'}, {c['rating']} yıldız")
        lay.addWidget(head)
        lay.addWidget(label(c["text"], wrap=True))
        actions = QHBoxLayout()
        if c["status"] != "approved":
            actions.addWidget(button("Yayınla", "primary", lambda: self.act(c, "approve")))
        if c["status"] != "rejected":
            actions.addWidget(button("Reddet", None, lambda: self.act(c, "reject")))
        actions.addWidget(button("Sil", "danger", lambda: self.act(c, "delete")))
        actions.addStretch()
        lay.addLayout(actions)
        return card

    def act(self, comment, action):
        if action == "delete":
            if not confirm(self, "Yorumu sil", "Yorum kalıcı olarak silinsin mi?", "Sil"):
                return
            fn, args = self.api.delete_comment, (comment["id"],)
        else:
            fn, args = self.api.review_comment, (comment["id"], action)
        run_async(fn, *args, on_done=lambda _: self.reload(), on_error=lambda e: show_error(self, e))
