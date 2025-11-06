from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame,
                            QFormLayout, QCheckBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette

class LoginPage(QWidget):
    login_success = pyqtSignal(tuple)  # Kullanıcı verilerini gönder
    
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
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)
        
        # Başlık alanı
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Başlık
        title = QLabel('QR MENU')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel('Admin Panel')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                margin-bottom: 30px;
                opacity: 0.9;
            }
        """)
        title_layout.addWidget(subtitle)
        
        main_layout.addLayout(title_layout)
        
        # Login formu
        form_frame = QFrame()
        form_frame.setFixedSize(400, 350)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        
        form_layout = QVBoxLayout()
        form_frame.setLayout(form_layout)
        
        # Form başlığı
        form_title = QLabel('Giriş Yapın')
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 20px;
            }
        """)
        form_layout.addWidget(form_title)
        
        # Kullanıcı adı
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Kullanıcı Adı')
        self.username_input.setText('admin')  # Varsayılan değer
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                outline: none;
            }
        """)
        form_layout.addWidget(self.username_input)
        
        # Şifre
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Şifre')
        self.password_input.setText('admin123')  # Varsayılan değer
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                outline: none;
            }
        """)
        form_layout.addWidget(self.password_input)
        
        # Beni hatırla checkbox
        self.remember_checkbox = QCheckBox('Beni Hatırla')
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #666;
                font-size: 12px;
                margin-bottom: 20px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:checked {
                background-color: #667eea;
                border: 2px solid #667eea;
            }
        """)
        form_layout.addWidget(self.remember_checkbox)
        
        # Giriş butonu
        login_btn = QPushButton('Giriş Yap')
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px;
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
        form_layout.addWidget(login_btn)
        
        # Kayıt ol linki
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)
        
        register_label = QLabel('Hesabınız yok mu?')
        register_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
            }
        """)
        register_layout.addWidget(register_label)
        
        register_btn = QPushButton('Kayıt Ol')
        register_btn.clicked.connect(self.show_register)
        register_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #667eea;
                font-size: 12px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #5a67d8;
            }
        """)
        register_layout.addWidget(register_btn)
        
        form_layout.addLayout(register_layout)
        
        main_layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        
        # Alt bilgi
        info_label = QLabel('Varsayılan: admin / admin123')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                margin-top: 20px;
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