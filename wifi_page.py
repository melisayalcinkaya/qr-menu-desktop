from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                            QHeaderView, QComboBox, QDialog, QFormLayout,
                            QLineEdit, QTextEdit, QGroupBox, QCheckBox, QFrame,
                            QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import qrcode
import os

class WiFiPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_business_id = None
        self.init_ui()
        self.load_businesses()
        self.load_wifi_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('WiFi Ayarları Yönetimi')
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
        
        # İşletme seçimi
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('İşletme Seçin:'))
        
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
                border-color: #3498db;
            }
        """)
        filter_layout.addWidget(self.business_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton('+ WiFi Ayarı Ekle')
        self.add_button.clicked.connect(self.add_wifi_setting)
        self.add_button.setStyleSheet("""
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
        
        self.edit_button = QPushButton('✏ Düzenle')
        self.edit_button.clicked.connect(self.edit_wifi_setting)
        self.edit_button.setStyleSheet("""
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
        
        self.delete_button = QPushButton('🗑 Sil')
        self.delete_button.clicked.connect(self.delete_wifi_setting)
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
        
        self.generate_qr_button = QPushButton('📱 WiFi QR Oluştur')
        self.generate_qr_button.clicked.connect(self.generate_wifi_qr)
        self.generate_qr_button.setStyleSheet("""
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
        
        self.refresh_button = QPushButton('🔄 Yenile')
        self.refresh_button.clicked.connect(self.load_wifi_settings)
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
        button_layout.addWidget(self.generate_qr_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'WiFi Adı', 'Şifre', 'Genel WiFi', 'Oluşturma Tarihi'
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
                background-color: #2980b9;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Tablo genişlik ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # WiFi Adı
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Şifre
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Genel WiFi
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Tarih
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        # WiFi QR kodları bölümü
        qr_group = QGroupBox('WiFi QR Kodları')
        qr_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        qr_layout = QHBoxLayout()
        
        # QR kodları grid layout
        self.qr_grid = QGridLayout()
        self.qr_scroll_widget = QWidget()
        self.qr_scroll_widget.setLayout(self.qr_grid)
        qr_layout.addWidget(self.qr_scroll_widget)
        
        qr_group.setLayout(qr_layout)
        layout.addWidget(qr_group)
        
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
        self.load_wifi_settings()
    
    def load_wifi_settings(self):
        """WiFi ayarlarını yükle"""
        if not self.current_business_id:
            self.table.setRowCount(0)
            self.clear_qr_codes()
            self.stats_label.setText('Önce bir işletme seçin')
            return
        
        try:
            wifi_settings = self.db.get_wifi_settings(self.current_business_id)
            self.table.setRowCount(len(wifi_settings))
            
            for row, wifi in enumerate(wifi_settings):
                self.table.setItem(row, 0, QTableWidgetItem(str(wifi[0])))  # ID
                self.table.setItem(row, 1, QTableWidgetItem(wifi[2]))       # WiFi name
                
                # Şifreyi gizle
                password = wifi[3] or ''
                masked_password = '*' * len(password) if password else 'Şifresiz'
                self.table.setItem(row, 2, QTableWidgetItem(masked_password))
                
                # Genel WiFi durumu
                is_public = 'Evet' if wifi[4] else 'Hayır'
                self.table.setItem(row, 3, QTableWidgetItem(is_public))
                
                # Tarih
                created_at = wifi[5] or ''
                if len(created_at) > 10:
                    created_at = created_at[:10]
                self.table.setItem(row, 4, QTableWidgetItem(created_at))
            
            # QR kodlarını güncelle
            self.update_qr_codes(wifi_settings)
            
            # İstatistik güncelle
            business_name = self.business_combo.currentText()
            public_count = len([w for w in wifi_settings if w[4]])
            private_count = len(wifi_settings) - public_count
            total_count = len(wifi_settings)
            
            self.stats_label.setText(
                f'{business_name} | Toplam: {total_count} WiFi | Genel: {public_count} | Özel: {private_count}'
            )
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'WiFi ayarları yüklenirken hata oluştu: {str(e)}')
    
    def update_qr_codes(self, wifi_settings):
        """WiFi QR kodlarını güncelle"""
        self.clear_qr_codes()
        
        for i, wifi in enumerate(wifi_settings):
            qr_frame = self.create_wifi_qr_widget(wifi)
            row = i // 3
            col = i % 3
            self.qr_grid.addWidget(qr_frame, row, col)
    
    def clear_qr_codes(self):
        """QR kodlarını temizle"""
        while self.qr_grid.count():
            child = self.qr_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def create_wifi_qr_widget(self, wifi_data):
        """WiFi QR kod widget'ı oluştur"""
        frame = QFrame()
        frame.setFixedSize(200, 250)
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #3498db;
            }
        """)
        
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        # WiFi adı
        name_label = QLabel(wifi_data[2])  # WiFi name
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # QR kod oluştur ve göster
        wifi_qr_data = self.generate_wifi_qr_data(wifi_data[2], wifi_data[3], wifi_data[4])
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=2,
            )
            qr.add_data(wifi_qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Geçici dosyaya kaydet
            temp_path = f"temp_wifi_qr_{wifi_data[0]}.png"
            img.save(temp_path)
            
            # QLabel'a yükle
            pixmap = QPixmap(temp_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            qr_label = QLabel()
            qr_label.setPixmap(scaled_pixmap)
            qr_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(qr_label)
            
            # Geçici dosyayı sil
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            error_label = QLabel(f'QR oluşturulamadı:\n{str(e)}')
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet('color: red; font-size: 10px;')
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
        
        # Bilgiler
        info_text = f"Şifre: {'Yok' if not wifi_data[3] else '***'}\n"
        info_text += f"Tür: {'Genel' if wifi_data[4] else 'Özel'}"
        
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #7f8c8d;
                margin-top: 5px;
            }
        """)
        layout.addWidget(info_label)
        
        return frame
    
    def generate_wifi_qr_data(self, ssid, password, is_public):
        """WiFi QR kod verisini oluştur"""
        if is_public or not password:
            # Genel WiFi (şifresiz)
            return f"WIFI:T:nopass;S:{ssid};P:;H:false;;"
        else:
            # Şifreli WiFi (WPA)
            return f"WIFI:T:WPA;S:{ssid};P:{password};H:false;;"
    
    def add_wifi_setting(self):
        """WiFi ayarı ekle"""
        if not self.current_business_id:
            QMessageBox.warning(self, 'Uyarı', 'Önce bir işletme seçin!')
            return
        
        dialog = WiFiDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                wifi_id = self.db.add_wifi_setting(
                    self.current_business_id,
                    data['wifi_name'],
                    data['wifi_password'],
                    data['is_public']
                )
                
                if wifi_id:
                    QMessageBox.information(self, 'Başarılı', 'WiFi ayarı başarıyla eklendi!')
                    self.load_wifi_settings()
                else:
                    QMessageBox.warning(self, 'Hata', 'WiFi ayarı eklenirken hata oluştu!')
                    
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'WiFi ayarı eklenirken hata oluştu: {str(e)}')
    
    def edit_wifi_setting(self):
        """WiFi ayarını düzenle"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlemek istediğiniz WiFi ayarını seçin!')
            return
        
        wifi_id = int(self.table.item(current_row, 0).text())
        
        # Mevcut veriyi getir
        wifi_settings = self.db.get_wifi_settings(self.current_business_id)
        wifi = next((w for w in wifi_settings if w[0] == wifi_id), None)
        
        if wifi:
            dialog = WiFiDialog(self, wifi)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                
                try:
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE wifi_settings 
                        SET wifi_name=?, wifi_password=?, is_public=?
                        WHERE id=?
                    ''', (data['wifi_name'], data['wifi_password'], data['is_public'], wifi_id))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, 'Başarılı', 'WiFi ayarı başarıyla güncellendi!')
                    self.load_wifi_settings()
                    
                except Exception as e:
                    QMessageBox.critical(self, 'Hata', f'WiFi ayarı güncellenirken hata oluştu: {str(e)}')
    
    def delete_wifi_setting(self):
        """WiFi ayarını sil"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz WiFi ayarını seçin!')
            return
        
        wifi_name = self.table.item(current_row, 1).text()
        wifi_id = int(self.table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, 'Onay', 
            f'"{wifi_name}" WiFi ayarını silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM wifi_settings WHERE id = ?', (wifi_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Başarılı', 'WiFi ayarı başarıyla silindi!')
                self.load_wifi_settings()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'WiFi ayarı silinirken hata oluştu: {str(e)}')
    
    def generate_wifi_qr(self):
        """Seçili WiFi için QR kod oluştur ve kaydet"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen QR kod oluşturmak istediğiniz WiFi ayarını seçin!')
            return
        
        wifi_id = int(self.table.item(current_row, 0).text())
        
        # WiFi verilerini getir
        wifi_settings = self.db.get_wifi_settings(self.current_business_id)
        wifi = next((w for w in wifi_settings if w[0] == wifi_id), None)
        
        if wifi:
            try:
                # QR kod verisi oluştur
                wifi_qr_data = self.generate_wifi_qr_data(wifi[2], wifi[3], wifi[4])
                
                # QR kod oluştur
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(wifi_qr_data)
                qr.make(fit=True)
                
                # Resim oluştur
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Dosya kaydet dialog
                business_name = self.business_combo.currentText().replace(' ', '_')
                wifi_name = wifi[2].replace(' ', '_')
                default_filename = f"wifi_qr_{business_name}_{wifi_name}.png"
                
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 'WiFi QR Kodu Kaydet', 
                    default_filename,
                    'PNG Dosyaları (*.png)'
                )
                
                if file_path:
                    img.save(file_path)
                    QMessageBox.information(self, 'Başarılı', f'WiFi QR kod başarıyla kaydedildi:\n{file_path}')
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'WiFi QR kod oluşturulurken hata oluştu: {str(e)}')


class WiFiDialog(QDialog):
    def __init__(self, parent=None, wifi_data=None):
        super().__init__(parent)
        self.wifi_data = wifi_data
        self.init_ui()
        
        if wifi_data:
            self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('WiFi Ayarı Ekle' if not self.wifi_data else 'WiFi Ayarı Düzenle')
        self.setModal(True)
        self.resize(400, 350)
        
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
        title = QLabel('WiFi Ayarları')
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
        
        # WiFi adı
        self.wifi_name_edit = QLineEdit()
        self.wifi_name_edit.setPlaceholderText('Örnek: Restoran_WiFi, Kafe_Guest')
        form_layout.addRow('WiFi Adı (SSID) (*)', self.wifi_name_edit)
        
        # WiFi şifresi
        self.wifi_password_edit = QLineEdit()
        self.wifi_password_edit.setPlaceholderText('Şifre (boş bırakılırsa açık ağ)')
        form_layout.addRow('WiFi Şifresi', self.wifi_password_edit)
        
        # Genel WiFi checkbox
        self.is_public_check = QCheckBox('Bu bir genel WiFi (herkesin kullanımına açık)')
        self.is_public_check.stateChanged.connect(self.on_public_changed)
        form_layout.addRow('', self.is_public_check)
        
        layout.addLayout(form_layout)
        
        # Bilgilendirme
        info_group = QGroupBox('Bilgilendirme')
        info_layout = QVBoxLayout()
        
        info_text = """
• WiFi QR kodu müşterilerin kolayca ağınıza bağlanmasını sağlar
• QR kodu mobil cihazlarla taranarak otomatik bağlantı kurulur
• Genel WiFi seçeneği şifresiz ağlar için kullanılır
• QR kodları masalarda veya girişte sergilenebilir
        """
        
        info_label = QLabel(info_text.strip())
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 11px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
                line-height: 1.4;
            }
        """)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton('Kaydet')
        self.save_button.clicked.connect(self.accept)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
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
        self.wifi_name_edit.returnPressed.connect(self.accept)
        self.wifi_password_edit.returnPressed.connect(self.accept)
    
    def on_public_changed(self, state):
        """Genel WiFi seçeneği değiştiğinde"""
        if state == Qt.Checked:
            # Genel WiFi seçilirse şifreyi temizle ve devre dışı bırak
            self.wifi_password_edit.clear()
            self.wifi_password_edit.setEnabled(False)
            self.wifi_password_edit.setPlaceholderText('Genel WiFi şifresizdir')
        else:
            # Genel WiFi seçilmezse şifre alanını aktif et
            self.wifi_password_edit.setEnabled(True)
            self.wifi_password_edit.setPlaceholderText('Şifre (boş bırakılırsa açık ağ)')
    
    def load_data(self):
        """Mevcut veriyi yükle"""
        if self.wifi_data:
            self.wifi_name_edit.setText(self.wifi_data[2] or '')
            self.wifi_password_edit.setText(self.wifi_data[3] or '')
            self.is_public_check.setChecked(bool(self.wifi_data[4]))
    
    def get_data(self):
        """Form verilerini döndür"""
        return {
            'wifi_name': self.wifi_name_edit.text().strip(),
            'wifi_password': self.wifi_password_edit.text().strip() if self.wifi_password_edit.isEnabled() else '',
            'is_public': self.is_public_check.isChecked()
        }
    
    def accept(self):
        """Kaydetmeden önce validasyon"""
        data = self.get_data()
        
        if not data['wifi_name']:
            QMessageBox.warning(self, 'Uyarı', 'WiFi adı boş olamaz!')
            self.wifi_name_edit.setFocus()
            return
        
        # WiFi adında özel karakterler kontrolü
        invalid_chars = ['<', '>', '"', '|', '*', '?', ':', '\\', '/']
        if any(char in data['wifi_name'] for char in invalid_chars):
            QMessageBox.warning(self, 'Uyarı', 'WiFi adında geçersiz karakterler bulunuyor!\n' +
                              'Şu karakterler kullanılamaz: < > " | * ? : \\ /')
            self.wifi_name_edit.setFocus()
            return
        
        super().accept()