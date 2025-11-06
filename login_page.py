from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame,
                            QFormLayout, QCheckBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette

class LoginPage(QWidget):
    login_success = pyqtSignal(tuple)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Üst spacer
        main_layout.addStretch(1)
        
        # Başlık container
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(15)
        title_layout.setContentsMargins(0, 0, 0, 30)
        
        # Logo/Başlık
        title = QLabel('QR MENU')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: 700;
                color: white;
                letter-spacing: 6px;
                background: transparent;
                margin: 0px;
                padding: 0px;
            }
        """)
        title_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel('Admin Panel')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: rgba(255, 255, 255, 0.9);
                letter-spacing: 2px;
                font-weight: 300;
                background: transparent;
                margin: 0px;
                padding: 0px;
            }
        """)
        title_layout.addWidget(subtitle)
        
        main_layout.addWidget(title_container)
        
        # Login card container
        card_container = QWidget()
        card_container.setStyleSheet("background: transparent;")
        card_layout = QHBoxLayout(card_container)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # Centering için spacers
        card_layout.addStretch(1)
        
        # Login card
        login_card = QFrame()
        login_card.setMinimumWidth(450)
        login_card.setMaximumWidth(500)
        login_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        card_content = QVBoxLayout(login_card)
        card_content.setContentsMargins(40, 40, 40, 40)
        card_content.setSpacing(20)
        
        # Form başlığı
        form_title = QLabel('Hoş Geldiniz')
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: 600;
                color: #2d3748;
                margin: 0px;
                padding: 0px;
            }
        """)
        card_content.addWidget(form_title)
        
        # Form açıklaması
        form_subtitle = QLabel('Devam etmek için giriş yapın')
        form_subtitle.setAlignment(Qt.AlignCenter)
        form_subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #718096;
                margin: 0px;
                padding: 0px;
            }
        """)
        card_content.addWidget(form_subtitle)
        
        card_content.addSpacing(10)
        
        # Kullanıcı adı
        username_label = QLabel('Kullanıcı Adı')
        username_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #4a5568;
                margin: 0px;
                padding: 0px;
            }
        """)
        card_content.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Kullanıcı adınızı girin')
        self.username_input.setText('admin')
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                background-color: #f7fafc;
                color: #2d3748;
                margin: 0px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #cbd5e0;
            }
        """)
        card_content.addWidget(self.username_input)
        
        # Şifre
        password_label = QLabel('Şifre')
        password_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #4a5568;
                margin: 0px;
                padding: 0px;
            }
        """)
        card_content.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Şifrenizi girin')
        self.password_input.setText('admin123')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                background-color: #f7fafc;
                color: #2d3748;
                margin: 0px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #cbd5e0;
            }
        """)
        card_content.addWidget(self.password_input)
        
        # Beni hatırla
        remember_layout = QHBoxLayout()
        remember_layout.setContentsMargins(0, 5, 0, 5)
        
        self.remember_checkbox = QCheckBox('Beni Hatırla')
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #4a5568;
                font-size: 14px;
                margin: 0px;
                padding: 0px;
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
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        card_content.addLayout(remember_layout)
        
        # Giriş butonu
        login_btn = QPushButton('Giriş Yap')
        login_btn.clicked.connect(self.login)
        login_btn.setFixedHeight(45)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 0.5px;
                margin: 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c51bf, stop:1 #553c9a);
            }
        """)
        card_content.addWidget(login_btn)
        
        # Ayırıcı çizgi
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("""
            QFrame {
                background-color: #e2e8f0;
                max-height: 1px;
                margin: 15px 0px;
            }
        """)
        card_content.addWidget(divider)
        
        # Kayıt ol alanı
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)
        register_layout.setSpacing(5)
        
        register_label = QLabel('Hesabınız yok mu?')
        register_label.setStyleSheet("""
            QLabel {
                color: #718096;
                font-size: 14px;
                margin: 0px;
                padding: 0px;
            }
        """)
        register_layout.addWidget(register_label)
        
        register_btn = QPushButton('Kayıt Ol')
        register_btn.clicked.connect(self.show_register)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #667eea;
                font-size: 14px;
                font-weight: 600;
                padding: 2px 8px;
                margin: 0px;
            }
            QPushButton:hover {
                color: #5a67d8;
                text-decoration: underline;
            }
        """)
        register_layout.addWidget(register_btn)
        
        card_content.addLayout(register_layout)
        
        card_layout.addWidget(login_card)
        card_layout.addStretch(1)
        
        main_layout.addWidget(card_container)
        
        # Alt spacer
        main_layout.addStretch(1)
        
        # Alt bilgi
        info_label = QLabel('Varsayılan: admin / admin123')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 13px;
                letter-spacing: 0.5px;
                background: transparent;
                margin: 10px 0px 0px 0px;
                padding: 0px;
            }
        """)
        main_layout.addWidget(info_label)
        
        # Enter tuşu ile giriş
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.login)
    
    def login(self):
        """Giriş işlemi"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen kullanıcı adı ve şifre girin!')
            return
        
        # Veritabanından kontrol et
        user = self.parent.db.login(username, password)
        
        if user:
            self.login_success.emit(user)
            self.clear_form()
        else:
            QMessageBox.warning(self, 'Hata', 'Kullanıcı adı veya şifre yanlış!')
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_register(self):
        """Kayıt formu göster"""
        from register_dialog import RegisterDialog
        
        dialog = RegisterDialog(self)
        if dialog.exec_() == dialog.Accepted:
            QMessageBox.information(self, 'Başarılı', 
                                  'Kullanıcı başarıyla kaydedildi!\nŞimdi giriş yapabilirsiniz.')
    
    def clear_form(self):
        """Formu temizle"""
        if not self.remember_checkbox.isChecked():
            self.username_input.clear()
        self.password_input.clear()
    
    def keyPressEvent(self, event):
        """ESC tuşu ile çıkış"""
        if event.key() == Qt.Key_Escape:
            reply = QMessageBox.question(self, 'Çıkış', 
                                       'Uygulamadan çıkmak istediğinizden emin misiniz?',
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.parent.close()
        super().keyPressEvent(event)