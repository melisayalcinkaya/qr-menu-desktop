from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                            QLabel, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                            QHeaderView, QFileDialog, QComboBox, QDoubleSpinBox, QCheckBox,
                            QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ProductsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_business_id = None
        self.current_category_id = None
        self.init_ui()
        self.load_businesses()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Ürün Yönetimi')
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                border-bottom: 2px solid #f39c12;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Filtre seçimleri
        filter_layout = QHBoxLayout()
        
        # İşletme seçimi
        filter_layout.addWidget(QLabel('İşletme:'))
        self.business_combo = QComboBox()
        self.business_combo.currentIndexChanged.connect(self.on_business_changed)
        self.business_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(self.business_combo)
        
        # Menü tipi seçimi
        filter_layout.addWidget(QLabel('Menü:'))
        self.menu_type_combo = QComboBox()
        self.menu_type_combo.addItems(['Menü 1', 'Menü 2', 'Menü 3'])
        self.menu_type_combo.currentIndexChanged.connect(self.load_categories)
        filter_layout.addWidget(self.menu_type_combo)
        
        # Kategori seçimi
        filter_layout.addWidget(QLabel('Kategori:'))
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton('+ Ürün Ekle')
        self.add_button.clicked.connect(self.add_product)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        
        self.edit_button = QPushButton('✏ Düzenle')
        self.edit_button.clicked.connect(self.edit_product)
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
        self.delete_button.clicked.connect(self.delete_product)
        self.delete_button.setStyleSheet("""
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
        
        self.refresh_button = QPushButton('🔄 Yenile')
        self.refresh_button.clicked.connect(self.load_products)
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Ürün Adı', 'Kategori', 'Fiyat', 'Menü', 'Rating', 'Durum', 'Oluşturma Tarihi'
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
                background-color: #f39c12;
                color: white;
            }
            QHeaderView::section {
                background-color: #e67e22;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Tablo genişlik ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Ürün Adı
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Kategori
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Fiyat
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Menü
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Rating
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Durum
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents) # Tarih
        
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
    
    def load_categories(self):
        """Kategorileri yükle"""
        self.category_combo.clear()
        self.category_combo.addItem('Tüm Kategoriler', None)
        
        if not self.current_business_id:
            self.load_products()
            return
        
        try:
            menu_type = self.get_current_menu_type()
            categories = self.db.get_categories(self.current_business_id, menu_type)
            
            for category in categories:
                self.category_combo.addItem(category[1], category[0])  # name, id
            
            self.load_products()
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kategoriler yüklenirken hata oluştu: {str(e)}')
    
    def on_category_changed(self):
        """Kategori değiştiğinde"""
        self.current_category_id = self.category_combo.currentData()
        self.load_products()
    
    def get_current_menu_type(self):
        """Seçili menü tipini döndür"""
        return self.menu_type_combo.currentIndex() + 1  # 1, 2, 3
    
    def load_products(self):
        """Ürünleri yükle"""
        if not self.current_business_id:
            self.table.setRowCount(0)
            self.stats_label.setText('Önce bir işletme seçin')
            return
        
        try:
            menu_type = self.get_current_menu_type()
            products = self.db.get_products(
                business_id=self.current_business_id,
                category_id=self.current_category_id,
                menu_type=menu_type
            )
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                self.table.setItem(row, 0, QTableWidgetItem(str(product[0])))  # ID
                self.table.setItem(row, 1, QTableWidgetItem(product[1]))       # Name
                self.table.setItem(row, 2, QTableWidgetItem(product[-1] or 'Kategori Yok'))  # Category name
                self.table.setItem(row, 3, QTableWidgetItem(f'{product[3]:.2f} TL'))  # Price
                self.table.setItem(row, 4, QTableWidgetItem(f'Menü {product[7]}'))   # Menu Type
                self.table.setItem(row, 5, QTableWidgetItem(f'{product[8]:.1f}'))    # Rating
                
                # Durum
                is_available = 'Mevcut' if product[10] else 'Stokta Yok'
                self.table.setItem(row, 6, QTableWidgetItem(is_available))
                
                # Tarih
                created_at = product[11] or ''
                if len(created_at) > 10:
                    created_at = created_at[:10]
                self.table.setItem(row, 7, QTableWidgetItem(created_at))
            
            # İstatistik güncelle
            business_name = self.business_combo.currentText()
            menu_name = self.menu_type_combo.currentText()
            category_name = self.category_combo.currentText()
            available_count = len([p for p in products if p[10]])
            total_count = len(products)
            
            stats_text = f'{business_name} - {menu_name}'
            if category_name != 'Tüm Kategoriler':
                stats_text += f' - {category_name}'
            stats_text += f' | Toplam: {total_count} ürün | Mevcut: {available_count} | Stokta Yok: {total_count - available_count}'
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Ürünler yüklenirken hata oluştu: {str(e)}')
    
    def add_product(self):
        """Ürün ekleme"""
        if not self.current_business_id:
            QMessageBox.warning(self, 'Uyarı', 'Önce bir işletme seçin!')
            return
        
        # Kategorileri kontrol et
        menu_type = self.get_current_menu_type()
        categories = self.db.get_categories(self.current_business_id, menu_type)
        
        if not categories:
            QMessageBox.warning(self, 'Uyarı', 'Önce kategori oluşturmalısınız!')
            return
        
        dialog = ProductDialog(self, categories)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                product_id = self.db.add_product(
                    data['name'],
                    data['description'],
                    data['price'],
                    data['category_id'],
                    self.current_business_id,
                    menu_type,
                    data['image']
                )
                
                if product_id:
                    QMessageBox.information(self, 'Başarılı', 'Ürün başarıyla eklendi!')
                    self.load_products()
                else:
                    QMessageBox.warning(self, 'Hata', 'Ürün eklenirken hata oluştu!')
                    
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Ürün eklenirken hata oluştu: {str(e)}')
    
    def edit_product(self):
        """Ürün düzenleme"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlemek istediğiniz ürünü seçin!')
            return
        
        product_id = int(self.table.item(current_row, 0).text())
        
        # Mevcut veriyi getir
        menu_type = self.get_current_menu_type()
        products = self.db.get_products(
            business_id=self.current_business_id,
            menu_type=menu_type
        )
        product = next((p for p in products if p[0] == product_id), None)
        categories = self.db.get_categories(self.current_business_id, menu_type)
        
        if product and categories:
            dialog = ProductDialog(self, categories, product)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                
                try:
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE products 
                        SET name=?, description=?, price=?, category_id=?, image=?
                        WHERE id=?
                    ''', (data['name'], data['description'], data['price'], 
                          data['category_id'], data['image'], product_id))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, 'Başarılı', 'Ürün başarıyla güncellendi!')
                    self.load_products()
                    
                except Exception as e:
                    QMessageBox.critical(self, 'Hata', f'Ürün güncellenirken hata oluştu: {str(e)}')
    
    def delete_product(self):
        """Ürün silme"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz ürünü seçin!')
            return
        
        product_name = self.table.item(current_row, 1).text()
        product_id = int(self.table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, 'Onay', 
            f'"{product_name}" ürünını silmek istediğinizden emin misiniz?\n\n'
            'Bu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE products SET is_available = 0 WHERE id = ?', (product_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Başarılı', 'Ürün başarıyla silindi!')
                self.load_products()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Ürün silinirken hata oluştu: {str(e)}')


class ProductDialog(QDialog):
    def __init__(self, parent=None, categories=None, product_data=None):
        super().__init__(parent)
        self.categories = categories or []
        self.product_data = product_data
        self.init_ui()
        
        if product_data:
            self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('Ürün Ekle' if not self.product_data else 'Ürün Düzenle')
        self.setModal(True)
        self.resize(500, 500)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                font-size: 13px;
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border-color: #f39c12;
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
        title = QLabel('Ürün Bilgileri')
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
        
        # Ürün adı
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Örnek: Margherita Pizza, Karışık Salata')
        form_layout.addRow('Ürün Adı (*)', self.name_edit)
        
        # Kategori seçimi
        self.category_combo = QComboBox()
        for category in self.categories:
            self.category_combo.addItem(category[1], category[0])  # name, id
        form_layout.addRow('Kategori (*)', self.category_combo)
        
        # Açıklama
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText('Ürün açıklaması, malzemeler, özellikler...')
        form_layout.addRow('Açıklama', self.description_edit)
        
        # Fiyat
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setDecimals(2)
        self.price_spin.setMinimum(0.01)
        self.price_spin.setMaximum(9999.99)
        self.price_spin.setSuffix(' TL')
        form_layout.addRow('Fiyat (*)', self.price_spin)
        
        # Resim yolu
        image_layout = QHBoxLayout()
        self.image_edit = QLineEdit()
        self.image_edit.setPlaceholderText('Ürün resmi yolu (opsiyonel)')
        image_button = QPushButton('Resim Seç')
        image_button.clicked.connect(self.select_image)
        image_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        image_layout.addWidget(self.image_edit)
        image_layout.addWidget(image_button)
        
        form_layout.addRow('Ürün Resmi', image_layout)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton('Kaydet')
        self.save_button.clicked.connect(self.accept)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
            }
            QPushButton:hover {
                background-color: #e67e22;
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
        
        # Enter tuşu ile kaydet
        self.name_edit.returnPressed.connect(self.accept)
    
    def load_data(self):
        """Mevcut veriyi yükle"""
        if self.product_data:
            self.name_edit.setText(self.product_data[1] or '')
            self.description_edit.setPlainText(self.product_data[2] or '')
            self.price_spin.setValue(float(self.product_data[3] or 0))
            self.image_edit.setText(self.product_data[4] or '')
            
            # Kategori seç
            category_id = self.product_data[5]
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == category_id:
                    self.category_combo.setCurrentIndex(i)
                    break
    
    def select_image(self):
        """Ürün resmi seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Ürün Resmi Seç', '', 
            'Resim Dosyaları (*.png *.jpg *.jpeg *.gif *.bmp)'
        )
        if file_path:
            self.image_edit.setText(file_path)
    
    def get_data(self):
        """Form verilerini döndür"""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'price': self.price_spin.value(),
            'category_id': self.category_combo.currentData(),
            'image': self.image_edit.text().strip()
        }
    
    def accept(self):
        """Kaydetmeden önce validasyon"""
        data = self.get_data()
        
        if not data['name']:
            QMessageBox.warning(self, 'Uyarı', 'Ürün adı boş olamaz!')
            self.name_edit.setFocus()
            return
        
        if not data['category_id']:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir kategori seçin!')
            self.category_combo.setFocus()
            return
        
        if data['price'] <= 0:
            QMessageBox.warning(self, 'Uyarı', 'Fiyat sıfırdan büyük olmalıdır!')
            self.price_spin.setFocus()
            return
        
        super().accept()