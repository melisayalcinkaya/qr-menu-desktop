from PySide6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QVBoxLayout

from .common import label


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Ayarlar")
        self.poll = QSpinBox()
        self.poll.setRange(3, 60)
        self.poll.setSuffix(" sn")
        self.poll.setValue(settings.poll_seconds)
        self.sound = QCheckBox("Yeni çağrıda zil sesi çal")
        self.sound.setChecked(settings.sound)
        self.notify = QCheckBox("Yeni çağrıda masaüstü bildirimi göster")
        self.notify.setChecked(settings.notifications)

        form = QFormLayout()
        form.addRow("Çağrıları yenileme aralığı", self.poll)
        buttons = QDialogButtonBox()
        buttons.addButton("Kaydet", QDialogButtonBox.ButtonRole.AcceptRole).setProperty("kind", "primary")
        buttons.addButton("Vazgeç", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self.sound)
        layout.addWidget(self.notify)
        layout.addWidget(label(f"Sunucu: {settings.server}", "muted", wrap=True))
        layout.addWidget(buttons)

    def accept(self):
        self.settings.poll_seconds = self.poll.value()
        self.settings.sound = self.sound.isChecked()
        self.settings.notifications = self.notify.isChecked()
        self.settings.save()
        super().accept()
