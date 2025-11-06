from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                            QLabel, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                            QHeaderView, QFileDialog, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CategoriesPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_business_id = None
        self.init_ui()
        self.load_businesses()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Kategori Yönetimi')
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                border-bottom: 2px solid #e74c3c;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # İşletme seçimi
        business_layout = QHBoxLayout()
        business_layout.addWidget(QLabel('İşletme Seçin:'))
        
        self.business_combo = QComboBox()
        self.business_combo.currentIndexChanged.connect(self.on_business_changed)
        self.business_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #e74c3c;
            }
        """)
        business_layout.addWidget(self.business_combo)
        
        # Menü tipi seçimi
        business_layout.addWidget(QLabel('Menü Tipi:'))
        self.menu_type_combo = QComboBox()
        self.menu_type_combo.addItems(['Menü 1', 'Menü 2', 'Menü 3'])
        self.menu_type_combo.currentIndexChanged.connect(self.load_categories)
        self.menu_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 120px;
            }
        """)
        business_layout.addWidget(self.menu_type_combo)
        
        business_layout.addStretch()
        layout.addLayout(business_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton('+ Kategori Ekle')
        self.add_button.clicked.connect(self.add_category)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        self.edit_button = QPushButton('✏ Düzenle')
        self.edit_button.clicked.connect(self.edit_category)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.delete_button = QPushButton('🗑 Sil')
        self.delete_button.clicked.connect(self.delete_category)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.refresh_button = QPushButton('🔄 Yenile')
        self.refresh_button.clicked.connect(self.load_categories)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Kategori Adı', 'Menü Tipi', 'Sıra', 'Banner', 'Aktif', 'Oluşturma Tarihi'
        ])
        
        # Tablo stilleri
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #e74c3c;
                color: white;
            }
            QHeaderView::section {
                background-color: #c0392b;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Tablo genişlik ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Kategori Adı
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Menü Tipi
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Sıra
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Banner
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Aktif
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Tarih
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        # İstatistik
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 6px;
                font-size: 12px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.stats_label)
    
    def load_businesses(self):
        """İşletmeleri yükle"""
        try:
            businesses = self.db.get_businesses()
            self.business_combo.clear()
            self.business_combo.addItem('İşletme Seçin', None)
            
            for business in businesses:
                self.business_combo.addItem(business[1], business[0])  # name, id
            
            if businesses:
                self.business_combo.setCurrentIndex(1)  # İlk işletmeyi seç
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'İşletmeler yüklenirken hata oluştu: {str(e)}')
    
    def on_business_changed(self):
        """İşletme değiştiğinde"""
        self.current_business_id = self.business_combo.currentData()
        self.load_categories()
    
    def get_current_menu_type(self):
        """Seçili menü tipini döndür"""
        return self.menu_type_combo.currentIndex() + 1  # 1, 2, 3
    
    def load_categories(self):
        """Kategorileri yükle"""
        if not self.current_business_id:
            self.table.setRowCount(0)
            self.stats_label.setText('Önce bir işletme seçin')
            return
        
        try:
            menu_type = self.get_current_menu_type()
            categories = self.db.get_categories(self.current_business_id, menu_type)
            self.table.setRowCount(len(categories))
            
            for row, category in enumerate(categories):
                self.table.setItem(row, 0, QTableWidgetItem(str(category[0])))  # ID
                self.table.setItem(row, 1, QTableWidgetItem(category[1]))       # Name
                self.table.setItem(row, 2, QTableWidgetItem(f'Menü {category[3]}')) # Menu Type
                self.table.setItem(row, 3, QTableWidgetItem(str(category[5])))  # Sort Order
                
                # Banner image - path varsa dosya adını göster
                banner = category[4] or ''
                if banner:
                    banner = banner.split('/')[-1][:30]  # Sadece dosya adı, ilk 30 karakter
                self.table.setItem(row, 4, QTableWidgetItem(banner))
                
                # Aktif durumu
                is_active = 'Aktif' if category[6] else 'Pasif'
                self.table.setItem(row, 5, QTableWidgetItem(is_active))
                
                # Tarih
                created_at = category[7] or ''
                if len(created_at) > 10:
                    created_at = created_at[:10]
                self.table.setItem(row, 6, QTableWidgetItem(created_at))
            
            # İstatistik güncelle
            business_name = self.business_combo.currentText()
            menu_name = self.menu_type_combo.currentText()
            active_count = len([c for c in categories if c[6]])
            total_count = len(categories)
            
            self.stats_label.setText(
                f'{business_name} - {menu_name} | '
                f'Toplam: {total_count} kategori | Aktif: {active_count} | Pasif: {total_count - active_count}'
            )
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kategoriler yüklenirken hata oluştu: {str(e)}')
    
    def add_category(self):
        """Kategori ekleme"""
        if not self.current_business_id:
            QMessageBox.warning(self, 'Uyarı', 'Önce bir işletme seçin!')
            return
        
        dialog = CategoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                menu_type = self.get_current_menu_type()
                category_id = self.db.add_category(
                    data['name'],
                    self.current_business_id,
                    menu_type,
                    data['banner_image']
                )
                
                if category_id:
                    QMessageBox.information(self, 'Başarılı', 'Kategori başarıyla eklendi!')
                    self.load_categories()
                else:
                    QMessageBox.warning(self, 'Hata', 'Kategori eklenirken hata oluştu!')
                    
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Kategori eklenirken hata oluştu: {str(e)}')
    
    def edit_category(self):
        """Kategori düzenleme"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlemek istediğiniz kategoriyi seçin!')
            return
        
        category_id = int(self.table.item(current_row, 0).text())
        
        # Mevcut veriyi getir
        menu_type = self.get_current_menu_type()
        categories = self.db.get_categories(self.current_business_id, menu_type)
        category = next((c for c in categories if c[0] == category_id), None)
        
        if category:
            dialog = CategoryDialog(self, category)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                
                try:
                    # Güncelleme için database fonksiyonu gerekli (şimdilik basit güncelleme)
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE categories 
                        SET name=?, banner_image=?
                        WHERE id=?
                    ''', (data['name'], data['banner_image'], category_id))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, 'Başarılı', 'Kategori başarıyla güncellendi!')
                    self.load_categories()
                    
                except Exception as e:
                    QMessageBox.critical(self, 'Hata', f'Kategori güncellenirken hata oluştu: {str(e)}')
    
    def delete_category(self):
        """Kategori silme"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz kategoriyi seçin!')
            return
        
        category_name = self.table.item(current_row, 1).text()
        category_id = int(self.table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, 'Onay', 
            f'"{category_name}" kategorisini silmek istediğinizden emin misiniz?\n\n'
            'Bu işlem geri alınamaz ve bu kategorideki tüm ürünler de silinecek!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Önce kategoriye ait ürünleri sil
                cursor.execute('DELETE FROM products WHERE category_id = ?', (category_id,))
                # Sonra kategoriyi sil
                cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Başarılı', 'Kategori başarıyla silindi!')
                self.load_categories()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Kategori silinirken hata oluştu: {str(e)}')


class CategoryDialog(QDialog):
    def __init__(self, parent=None, category_data=None):
        super().__init__(parent)
        self.category_data = category_data
        self.init_ui()
        
        if category_data:
            self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('Kategori Ekle' if not self.category_data else 'Kategori Düzenle')
        self.setModal(True)
        self.resize(400, 250)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                font-size: 13px;
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #e74c3c;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Kategori Bilgileri')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 6px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Form alanları
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Örnek: Ana Yemekler, İçecekler, Tatlılar')
        form_layout.addRow('Kategori Adı (*)', self.name_edit)
        
        # Banner resim yolu
        banner_layout = QHBoxLayout()
        self.banner_edit = QLineEdit()
        self.banner_edit.setPlaceholderText('Banner resim yolu (opsiyonel)')
        banner_button = QPushButton('Resim Seç')
        banner_button.clicked.connect(self.select_banner)
        banner_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        banner_layout.addWidget(self.banner_edit)
        banner_layout.addWidget(banner_button)
        
        form_layout.addRow('Banner Resmi', banner_layout)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton('Kaydet')
        self.save_button.clicked.connect(self.accept)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        self.cancel_button = QPushButton('İptal')
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Enter ile kaydet
        self.name_edit.returnPressed.connect(self.accept)
    
    def load_data(self):
        """Mevcut veriyi yükle"""
        if self.category_data:
            self.name_edit.setText(self.category_data[1] or '')
            self.banner_edit.setText(self.category_data[4] or '')
    
    def select_banner(self):
        """Banner resmi seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Banner Resmi Seç', '', 
            'Resim Dosyaları (*.png *.jpg *.jpeg *.gif *.bmp)'
        )
        if file_path:
            self.banner_edit.setText(file_path)
    
    def get_data(self):
        """Form verilerini döndür"""
        return {
            'name': self.name_edit.text().strip(),
            'banner_image': self.banner_edit.text().strip()
        }
    
    def accept(self):
        """Kaydetmeden önce validasyon"""
        data = self.get_data()
        
        if not data['name']:
            QMessageBox.warning(self, 'Uyarı', 'Kategori adı boş olamaz!')
            self.name_edit.setFocus()
            return
        
        super().accept()