import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QStackedWidget, QLabel,
                            QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.init_ui()
        self.show_login()
    
    def init_ui(self):
        self.setWindowTitle('QR Menu Admin Panel')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Sol panel (menü)
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Sağ panel (içerik)
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area, 1)
        
        # Sayfaları oluştur
        self.create_pages()
        
        # Stili uygula
        self.apply_styles()
        
        # İlk sayfa
        self.show_dashboard()
    
    def create_sidebar(self):
        """Sol menü paneli"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout()
        self.sidebar.setLayout(layout)
        
        # Logo/Başlık
        title = QLabel('QR Menu Admin')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-bottom: 2px solid #bdc3c7;
            }
        """)
        layout.addWidget(title)
        
        # Menü butonları
        self.menu_buttons = {}
        
        menu_items = [
            ('Dashboard', 'dashboard'),
            ('İşletmeler', 'business'),
            ('Kategoriler', 'categories'),
            ('Ürünler', 'products'),
            ('Yorumlar', 'comments'),
            ('QR Kodlar', 'qrcodes'),
            ('Garson Çağrıları', 'waiter'),
            ('WiFi Ayarları', 'wifi'),
            ('Çıkış', 'logout')
        ]
        
        for text, key in menu_items:
            btn = QPushButton(text)
            btn.setObjectName(key)
            btn.clicked.connect(lambda checked, k=key: self.menu_clicked(k))
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 15px 20px;
                    font-size: 14px;
                    border: none;
                    background-color: transparent;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #2980b9;
                }
            """)
            layout.addWidget(btn)
            self.menu_buttons[key] = btn
        
        layout.addStretch()
        
        # Kullanıcı bilgisi
        self.user_label = QLabel('Kullanıcı: Giriş yapılmamış')
        self.user_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #34495e;
                color: white;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.user_label)
    
    def create_pages(self):
        """Tüm sayfaları oluştur"""
        # Login sayfası
        from login_page import LoginPage
        self.login_page = LoginPage(self)
        self.login_page.login_success.connect(self.on_login_success)
        self.content_area.addWidget(self.login_page)
        
        #     # Geçici placeholder sayfalar
        # self.dashboard_page = QLabel("Dashboard sayfası yakında...")
        # self.dashboard_page.setAlignment(Qt.AlignCenter)
        # self.dashboard_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.dashboard_page)
        
        # self.business_page = QLabel("İşletme sayfası yakında...")
        # self.business_page.setAlignment(Qt.AlignCenter)
        # self.business_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.business_page)
        
        # self.categories_page = QLabel("Kategoriler sayfası yakında...")
        # self.categories_page.setAlignment(Qt.AlignCenter) 
        # self.categories_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.categories_page)
        
        # self.products_page = QLabel("Ürünler sayfası yakında...")
        # self.products_page.setAlignment(Qt.AlignCenter)
        # self.products_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.products_page)
        
        # self.comments_page = QLabel("Yorumlar sayfası yakında...")
        # self.comments_page.setAlignment(Qt.AlignCenter)
        # self.comments_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.comments_page)
        
        # self.qr_page = QLabel("QR Kodlar sayfası yakında...")
        # self.qr_page.setAlignment(Qt.AlignCenter)
        # self.qr_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.qr_page)
        
        # self.waiter_page = QLabel("Garson Çağrıları sayfası yakında...")
        # self.waiter_page.setAlignment(Qt.AlignCenter)
        # self.waiter_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.waiter_page)
        
        # self.wifi_page = QLabel("WiFi Ayarları sayfası yakında...")
        # self.wifi_page.setAlignment(Qt.AlignCenter)
        # self.wifi_page.setStyleSheet("font-size: 18px; color: #666; padding: 50px;")
        # self.content_area.addWidget(self.wifi_page)

        # Dashboard sayfası
        from dashboard_page import DashboardPage
        self.dashboard_page = DashboardPage(self.db)
        self.content_area.addWidget(self.dashboard_page)
        
        # İşletme sayfası
        from business_page import BusinessPage
        self.business_page = BusinessPage(self.db)
        self.content_area.addWidget(self.business_page)
        
        # Kategori sayfası
        from categories_page import CategoriesPage
        self.categories_page = CategoriesPage(self.db)
        self.content_area.addWidget(self.categories_page)
        
        # Ürün sayfası
        from products_page import ProductsPage
        self.products_page = ProductsPage(self.db)
        self.content_area.addWidget(self.products_page)
        
        # Yorum sayfası
        from comments_page import CommentsPage
        self.comments_page = CommentsPage(self.db)
        self.content_area.addWidget(self.comments_page)
        
        # QR kod sayfası
        from qr_page import QRPage
        self.qr_page = QRPage(self.db)
        self.content_area.addWidget(self.qr_page)
        
        # Garson çağrı sayfası
        from waiter_page import WaiterPage
        self.waiter_page = WaiterPage(self.db)
        self.content_area.addWidget(self.waiter_page)
        
        # WiFi ayar sayfası
        from wifi_page import WiFiPage
        self.wifi_page = WiFiPage(self.db)
        self.content_area.addWidget(self.wifi_page)
    
    def apply_styles(self):
        """Genel stilleri uygula"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
            }
        """)
    
    def show_login(self):
        """Login sayfasını göster"""
        self.content_area.setCurrentWidget(self.login_page)
        self.sidebar.setVisible(False)
    
    def on_login_success(self, user_data):
        """Login başarılı olduğunda"""
        self.current_user = user_data
        self.user_label.setText(f'Kullanıcı: {user_data[1]}')  # username
        self.sidebar.setVisible(True)
        self.show_dashboard()
    
    def menu_clicked(self, key):
        """Menü butonuna tıklandığında"""
        if key == 'logout':
            self.logout()
            return
        
        # Aktif butonu vurgula
        for btn_key, btn in self.menu_buttons.items():
            if btn_key == key:
                btn.setStyleSheet(btn.styleSheet() + """
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                    }
                """)
            else:
                btn.setStyleSheet(btn.styleSheet().replace("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                    }
                """, ""))
        
        # Sayfayı göster
        if key == 'dashboard':
            self.show_dashboard()
        elif key == 'business':
            self.show_business()
        elif key == 'categories':
            self.show_categories()
        elif key == 'products':
            self.show_products()
        elif key == 'comments':
            self.show_comments()
        elif key == 'qrcodes':
            self.show_qrcodes()
        elif key == 'waiter':
            self.show_waiter()
        elif key == 'wifi':
            self.show_wifi()
    
    def show_dashboard(self):
        self.content_area.setCurrentWidget(self.dashboard_page)
        self.dashboard_page.refresh_data()
    
    def show_business(self):
        self.content_area.setCurrentWidget(self.business_page)
        self.business_page.load_businesses()
    
    def show_categories(self):
        self.content_area.setCurrentWidget(self.categories_page)
        self.categories_page.load_categories()
    
    def show_products(self):
        self.content_area.setCurrentWidget(self.products_page)
        self.products_page.load_products()
    
    def show_comments(self):
        self.content_area.setCurrentWidget(self.comments_page)
        self.comments_page.load_comments()
    
    def show_qrcodes(self):
        self.content_area.setCurrentWidget(self.qr_page)
        self.qr_page.load_qr_codes()
    
    def show_waiter(self):
        self.content_area.setCurrentWidget(self.waiter_page)
        self.waiter_page.load_waiter_calls()
    
    def show_wifi(self):
        self.content_area.setCurrentWidget(self.wifi_page)
        self.wifi_page.load_wifi_settings()
    
    def logout(self):
        """Çıkış yap"""
        reply = QMessageBox.question(self, 'Çıkış', 
                                   'Çıkış yapmak istediğinizden emin misiniz?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.user_label.setText('Kullanıcı: Giriş yapılmamış')
            self.show_login()


def main():
    app = QApplication(sys.argv)
    
    # Uygulama ayarları
    app.setApplicationName('QR Menu Admin')
    app.setApplicationVersion('1.0')
    app.setOrganizationName('QR Menu')
    
    # Ana pencere
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    