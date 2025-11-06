from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                            QLabel, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                            QHeaderView, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BusinessPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_businesses()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('İşletme Yönetimi')
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                border-bottom: 2px solid #3498db;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton('+ İşletme Ekle')
        self.add_button.clicked.connect(self.add_business)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        
        self.edit_button = QPushButton('✏ Düzenle')
        self.edit_button.clicked.connect(self.edit_business)
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
        self.delete_button.clicked.connect(self.delete_business)
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
        self.refresh_button.clicked.connect(self.load_businesses)
        self.refresh_button.setStyleSheet("""
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
            'ID', 'İşletme Adı', 'Slug', 'Telefon', 'Adres', 'Aktif', 'Oluşturma Tarihi'
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
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Tablo genişlik ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # İşletme Adı
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Slug
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Telefon
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # Adres
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Aktif
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Tarih
        
        # Satır seçimini tek yapm
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.table)
        
        # İstatistik bilgisi
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
            
            # Eğer None veya boş ise
            if not businesses:
                businesses = []
            
            self.table.setRowCount(len(businesses))
            
            for row, business in enumerate(businesses):
                self.table.setItem(row, 0, QTableWidgetItem(str(business[0])))  # ID
                self.table.setItem(row, 1, QTableWidgetItem(str(business[1])))  # Name
                self.table.setItem(row, 2, QTableWidgetItem(str(business[2])))  # Slug
                self.table.setItem(row, 3, QTableWidgetItem(str(business[4]) if business[4] else ''))  # Phone
                
                # Adres - uzunsa kısalt
                address = str(business[5]) if business[5] else ''
                if len(address) > 50:
                    address = address[:50] + '...'
                self.table.setItem(row, 4, QTableWidgetItem(address))
                
                # Aktif durumu
                is_active = 'Aktif' if business[7] else 'Pasif'
                self.table.setItem(row, 5, QTableWidgetItem(is_active))
                
                # Tarih - str'ye çevir
                created_at = str(business[8]) if business[8] else ''
                if len(created_at) > 10:
                    created_at = created_at[:10]
                self.table.setItem(row, 6, QTableWidgetItem(created_at))
            
            # İstatistik güncelle
            active_count = len([b for b in businesses if b[7]])
            total_count = len(businesses)
            self.stats_label.setText(f'Toplam: {total_count} işletme | Aktif: {active_count} | Pasif: {total_count - active_count}')
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(error_details)  # Konsola yazdır
            QMessageBox.critical(self, 'Hata', f'İşletmeler yüklenirken hata oluştu: {str(e)}') # Konsola detaylı hata yazdır
    def add_business(self):
        """İşletme ekleme dialogu"""
        dialog = BusinessDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                business_id = self.db.add_business(
                    data['name'], 
                    data['slug'], 
                    data['description'], 
                    data['phone'], 
                    data['address'], 
                    data['logo']
                )
                
                if business_id:
                    QMessageBox.information(self, 'Başarılı', 'İşletme başarıyla eklendi!')
                    self.load_businesses()
                else:
                    QMessageBox.warning(self, 'Hata', 'Bu slug zaten kullanılıyor!')
                    
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'İşletme eklenirken hata oluştu: {str(e)}')
    
    def edit_business(self):
        """İşletme düzenleme"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlemek istediğiniz işletmeyi seçin!')
            return
        
        business_id = int(self.table.item(current_row, 0).text())
        
        # Mevcut veriyi getir
        businesses = self.db.get_businesses()
        business = next((b for b in businesses if b[0] == business_id), None)
        
        if business:
            dialog = BusinessDialog(self, business)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                
                try:
                    self.db.update_business(
                        business_id,
                        data['name'], 
                        data['slug'], 
                        data['description'], 
                        data['phone'], 
                        data['address'], 
                        data['logo']
                    )
                    
                    QMessageBox.information(self, 'Başarılı', 'İşletme başarıyla güncellendi!')
                    self.load_businesses()
                    
                except Exception as e:
                    QMessageBox.critical(self, 'Hata', f'İşletme güncellenirken hata oluştu: {str(e)}')
    
    def delete_business(self):
        """İşletme silme"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz işletmeyi seçin!')
            return
        
        business_name = self.table.item(current_row, 1).text()
        business_id = int(self.table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, 'Onay', 
            f'"{business_name}" işletmesini silmek istediğinizden emin misiniz?\n\n'
            'Bu işlem geri alınamaz ve tüm kategoriler, ürünler de silinecek!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_business(business_id)
                QMessageBox.information(self, 'Başarılı', 'İşletme başarıyla silindi!')
                self.load_businesses()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'İşletme silinirken hata oluştu: {str(e)}')


class BusinessDialog(QDialog):
    def __init__(self, parent=None, business_data=None):
        super().__init__(parent)
        self.business_data = business_data
        self.init_ui()
        
        if business_data:
            self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('İşletme Ekle' if not self.business_data else 'İşletme Düzenle')
        self.setModal(True)
        self.resize(500, 400)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                font-size: 13px;
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3498db;
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
        title = QLabel('İşletme Bilgileri')
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
        self.name_edit.setPlaceholderText('Örnek: Lezzet Restoranı')
        form_layout.addRow('İşletme Adı (*)', self.name_edit)
        
        self.slug_edit = QLineEdit()
        self.slug_edit.setPlaceholderText('Örnek: lezzet-restoran (URL için)')
        form_layout.addRow('Slug (*)', self.slug_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText('İşletme açıklaması...')
        form_layout.addRow('Açıklama', self.description_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText('Örnek: 0555 123 45 67')
        form_layout.addRow('Telefon', self.phone_edit)
        
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(60)
        self.address_edit.setPlaceholderText('İşletme adresi...')
        form_layout.addRow('Adres', self.address_edit)
        
        # Logo yolu
        logo_layout = QHBoxLayout()
        self.logo_edit = QLineEdit()
        self.logo_edit.setPlaceholderText('Logo dosya yolu (opsiyonel)')
        logo_button = QPushButton('Dosya Seç')
        logo_button.clicked.connect(self.select_logo)
        logo_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        logo_layout.addWidget(self.logo_edit)
        logo_layout.addWidget(logo_button)
        
        form_layout.addRow('Logo', logo_layout)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton('Kaydet')
        self.save_button.clicked.connect(self.accept)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #219a52;
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
        self.slug_edit.returnPressed.connect(self.accept)
    
    def load_data(self):
        """Mevcut veriyi yükle"""
        if self.business_data:
            self.name_edit.setText(self.business_data[1] or '')
            self.slug_edit.setText(self.business_data[2] or '')
            self.description_edit.setPlainText(self.business_data[3] or '')
            self.phone_edit.setText(self.business_data[4] or '')
            self.address_edit.setPlainText(self.business_data[5] or '')
            self.logo_edit.setText(self.business_data[6] or '')
    
    def select_logo(self):
        """Logo dosyası seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Logo Seç', '', 
            'Resim Dosyaları (*.png *.jpg *.jpeg *.gif *.bmp)'
        )
        if file_path:
            self.logo_edit.setText(file_path)
    
    def get_data(self):
        """Form verilerini döndür"""
        return {
            'name': self.name_edit.text().strip(),
            'slug': self.slug_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'phone': self.phone_edit.text().strip(),
            'address': self.address_edit.toPlainText().strip(),
            'logo': self.logo_edit.text().strip()
        }
    
    def accept(self):
        """Kaydetmeden önce validasyon"""
        data = self.get_data()
        
        if not data['name']:
            QMessageBox.warning(self, 'Uyarı', 'İşletme adı boş olamaz!')
            self.name_edit.setFocus()
            return
        
        if not data['slug']:
            QMessageBox.warning(self, 'Uyarı', 'Slug boş olamaz!')
            self.slug_edit.setFocus()
            return
        
        # Slug formatı kontrol et
        if not data['slug'].replace('-', '').replace('_', '').isalnum():
            QMessageBox.warning(self, 'Uyarı', 'Slug sadece harf, rakam, tire ve alt çizgi içerebilir!')
            self.slug_edit.setFocus()
            return
        
        super().accept()