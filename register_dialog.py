from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFormLayout,
                            QCheckBox, QFrame, QWidget)
from PyQt5.QtCore import Qt


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Yeni Kullanıcı Kayıt')
        self.setModal(True)
        self.resize(700, 750)

        # Genel arka plan (login ile aynı gradient)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)

        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addStretch(1)

        # Kayıt kartı
        card = QFrame()
        card.setMinimumWidth(500)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Başlık
        title = QLabel('Yeni Kullanıcı Kayıt')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 10px;
            }
        """)
        card_layout.addWidget(title)

        subtitle = QLabel('Lütfen bilgilerinizi doldurun')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #718096;
                margin-bottom: 20px;
            }
        """)
        card_layout.addWidget(subtitle)

        # Form alanları
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('Kullanıcı adınızı girin')
        self.username_edit.setFixedHeight(45)
        self.username_edit.setStyleSheet(self.input_style())
        form_layout.addRow('Kullanıcı Adı (*)', self.username_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText('email@example.com (opsiyonel)')
        self.email_edit.setFixedHeight(45)
        self.email_edit.setStyleSheet(self.input_style())
        form_layout.addRow('E-mail', self.email_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText('Güçlü bir şifre seçin')
        self.password_edit.setFixedHeight(45)
        self.password_edit.setStyleSheet(self.input_style())
        form_layout.addRow('Şifre (*)', self.password_edit)

        self.password_confirm_edit = QLineEdit()
        self.password_confirm_edit.setEchoMode(QLineEdit.Password)
        self.password_confirm_edit.setPlaceholderText('Şifrenizi tekrar girin')
        self.password_confirm_edit.setFixedHeight(45)
        self.password_confirm_edit.setStyleSheet(self.input_style())
        form_layout.addRow('Şifre Tekrar (*)', self.password_confirm_edit)

        card_layout.addLayout(form_layout)

        # Şartlar checkbox
        self.terms_check = QCheckBox('Kullanım şartlarını kabul ediyorum')
        self.terms_check.setStyleSheet("""
            QCheckBox {
                color: #eee;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e0;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #667eea;
                border: 2px solid #667eea;
            }
            QCheckBox::indicator:hover {
                border-color: #667eea;
            }
        """)
        card_layout.addWidget(self.terms_check)

        # Bilgi metni
        info_label = QLabel("""
• Kullanıcı adı benzersiz olmalıdır  
• Şifre en az 6 karakter olmalıdır  
• E-mail adresi opsiyoneldir  
• Tüm kullanıcılar admin yetkisine sahip olacaktır
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                color: #718096;
                font-size: 13px;
                background-color: #f7fafc;
                padding: 12px;
                border-radius: 10px;
                line-height: 1.6;
            }
        """)
        card_layout.addWidget(info_label)

        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.cancel_button = QPushButton('İptal')
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFixedHeight(45)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #a0aec0;
                color: white;
                border-radius: 10px;
                font-weight: 600;
                padding: 10px 20px;                        
            }
            QPushButton:hover {
                background-color: #718096;
            }
        """)

        self.register_button = QPushButton('Kayıt Ol')
        self.register_button.clicked.connect(self.register)
        self.register_button.setFixedHeight(45)
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.register_button)
        card_layout.addLayout(button_layout)

        # Kartı ortala
        wrapper = QHBoxLayout()
        wrapper.addStretch(1)
        wrapper.addWidget(card)
        wrapper.addStretch(1)
        main_layout.addLayout(wrapper)

        main_layout.addStretch(1)

    def input_style(self):
        return """
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                background-color: #f7fafc;
                color: #2d3748;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #cbd5e0;
            }
        """

    def register(self):
        """Kayıt işlemi"""
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        password_confirm = self.password_confirm_edit.text().strip()
        
        if not username:
            QMessageBox.warning(self, 'Uyarı', 'Kullanıcı adı boş olamaz!')
            self.username_edit.setFocus()
            return
        if not password:
            QMessageBox.warning(self, 'Uyarı', 'Şifre boş olamaz!')
            self.password_edit.setFocus()
            return
        if len(password) < 6:
            QMessageBox.warning(self, 'Uyarı', 'Şifre en az 6 karakter olmalıdır!')
            self.password_edit.setFocus()
            return
        if password != password_confirm:
            QMessageBox.warning(self, 'Uyarı', 'Şifreler eşleşmiyor!')
            self.password_confirm_edit.clear()
            self.password_confirm_edit.setFocus()
            return
        if not self.terms_check.isChecked():
            QMessageBox.warning(self, 'Uyarı', 'Kullanım şartlarını kabul etmelisiniz!')
            return
        if not username.replace('_', '').isalnum():
            QMessageBox.warning(self, 'Uyarı', 'Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir!')
            self.username_edit.setFocus()
            return
        if email and '@' not in email:
            QMessageBox.warning(self, 'Uyarı', 'Geçerli bir e-mail adresi girin!')
            self.email_edit.setFocus()
            return

        try:
            user_id = self.parent.parent.db.register_user(username, password, email)
            if user_id:
                self.accept()
            else:
                QMessageBox.warning(self, 'Hata', 
                    'Bu kullanıcı adı zaten kullanılıyor!\nLütfen başka bir kullanıcı adı seçin.')
                self.username_edit.setFocus()
                self.username_edit.selectAll()
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kayıt işlemi sırasında hata oluştu: {str(e)}')
