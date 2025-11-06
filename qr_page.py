from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                            QHeaderView, QComboBox, QDialog, QFormLayout,
                            QSpinBox, QLineEdit, QTextEdit, QFileDialog, QGroupBox,
                            QCheckBox, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import qrcode
import os
from datetime import datetime

class QRPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_business_id = None
        self.init_ui()
        self.load_businesses()
        self.load_qr_codes()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('QR Kod Yönetimi')
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                border-bottom: 2px solid #1abc9c;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Filtre ve seçimler
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
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton('+ QR Kod Oluştur')
        self.generate_button.clicked.connect(self.generate_qr_code)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        
        self.bulk_generate_button = QPushButton('📋 Toplu Oluştur')
        self.bulk_generate_button.clicked.connect(self.bulk_generate_qr)
        self.bulk_generate_button.setStyleSheet("""
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
        
        self.view_button = QPushButton('👁 Görüntüle')
        self.view_button.clicked.connect(self.view_qr_code)
        self.view_button.setStyleSheet("""
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
        
        self.download_button = QPushButton('💾 İndir')
        self.download_button.clicked.connect(self.download_qr_code)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        
        self.delete_button = QPushButton('🗑 Sil')
        self.delete_button.clicked.connect(self.delete_qr_code)
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
        self.refresh_button.clicked.connect(self.load_qr_codes)
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
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.bulk_generate_button)
        button_layout.addWidget(self.view_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'İşletme', 'Menü Tipi', 'Masa No', 'URL', 'Oluşturma Tarihi'
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
                background-color: #1abc9c;
                color: white;
            }
            QHeaderView::section {
                background-color: #16a085;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Tablo genişlik ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # İşletme
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Menü Tipi
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Masa No
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # URL
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Tarih
        
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
            self.business_combo.addItem('Tüm İşletmeler', None)
            
            for business in businesses:
                # business expected: (id, name, slug)
                self.business_combo.addItem(business[1], business[0])  # name, id
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'İşletmeler yüklenirken hata oluştu: {str(e)}')
    
    def get_business_slug(self, business_id):
        """İşletme slug'ını getir"""
        try:
            businesses = self.db.get_businesses()
            for business in businesses:
                if business[0] == business_id:
                    # expected index 2 is slug
                    return business[2]
        except Exception:
            pass
        return f"business{business_id}"
    
    def on_business_changed(self):
        """İşletme değiştiğinde"""
        self.current_business_id = self.business_combo.currentData()
        self.load_qr_codes()
    
    def load_qr_codes(self):
        """QR kodlarını yükle"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if self.current_business_id:
                cursor.execute('''
                    SELECT qr.*, b.name as business_name 
                    FROM qr_codes qr
                    JOIN businesses b ON qr.business_id = b.id
                    WHERE qr.business_id = ?
                    ORDER BY qr.created_at DESC
                ''', (self.current_business_id,))
            else:
                cursor.execute('''
                    SELECT qr.*, b.name as business_name 
                    FROM qr_codes qr
                    JOIN businesses b ON qr.business_id = b.id
                    ORDER BY qr.created_at DESC
                ''')
            
            qr_codes = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(qr_codes))
            
            for row, qr_code in enumerate(qr_codes):
                # NOTE: burada qr_code sütun indeksleri DB şemanıza göre değişebilir.
                # Aşağıdaki indeksleme orijinal koddaki varsayıma dayanıyor.
                self.table.setItem(row, 0, QTableWidgetItem(str(qr_code[0])))     # ID
                # business_name muhtemelen son sütun
                business_name = qr_code[-1] if len(qr_code) > 7 else (qr_code[6] if len(qr_code) > 6 else '')
                self.table.setItem(row, 1, QTableWidgetItem(business_name))          # Business name
                self.table.setItem(row, 2, QTableWidgetItem(f'Menü {qr_code[2]}')) # Menu Type
                
                # Masa numarası
                table_num = qr_code[5] or 'Genel'
                self.table.setItem(row, 3, QTableWidgetItem(str(table_num)))
                
                # URL - kısalt
                url = qr_code[3] or ''
                if len(url) > 50:
                    url = url[:47] + '...'
                self.table.setItem(row, 4, QTableWidgetItem(url))
                
                # Tarih
                # created_at indeksi orijinalde 6 (0-based) idi; güvenli kontrol ile alalım
                created_at = ''
                if len(qr_code) > 6 and qr_code[6]:
                    created_at = str(qr_code[6])
                    if len(created_at) > 10:
                        created_at = created_at[:10]
                self.table.setItem(row, 5, QTableWidgetItem(created_at))
            
            # İstatistik güncelle
            business_name = self.business_combo.currentText()
            total_count = len(qr_codes)
            
            # Menü tiplerini say
            menu_counts = {}
            for qr in qr_codes:
                menu_type = qr[2]
                menu_counts[menu_type] = menu_counts.get(menu_type, 0) + 1
            
            stats_text = f'{business_name} | Toplam: {total_count} QR kod'
            if menu_counts:
                menu_stats = ', '.join([f'Menü {k}: {v}' for k, v in menu_counts.items()])
                stats_text += f' | {menu_stats}'
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'QR kodları yüklenirken hata oluştu: {str(e)}')
    
    def view_qr_code(self):
        """QR kodu görüntüle"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen görüntülemek istediğiniz QR kodu seçin!')
            return
        
        qr_id = int(self.table.item(current_row, 0).text())
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM qr_codes WHERE id = ?', (qr_id,))
            qr_data = cursor.fetchone()
            conn.close()
            
            if qr_data and qr_data[4] and os.path.exists(qr_data[4]):  # qr_image_path
                dialog = QRViewDialog(self, qr_data)
                dialog.exec_()
            else:
                QMessageBox.warning(self, 'Uyarı', 'QR kod dosyası bulunamadı!')
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'QR kod görüntülenirken hata oluştu: {str(e)}')
    
    def download_qr_code(self):
        """QR kodu indir"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen indirmek istediğiniz QR kodu seçin!')
            return
        
        qr_id = int(self.table.item(current_row, 0).text())
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM qr_codes WHERE id = ?', (qr_id,))
            qr_data = cursor.fetchone()
            conn.close()
            
            if qr_data and qr_data[4] and os.path.exists(qr_data[4]):  # qr_image_path
                # Kaydet dialog
                save_path, _ = QFileDialog.getSaveFileName(
                    self, 'QR Kodu Kaydet', 
                    f'qr_code_{qr_id}.png',
                    'PNG Dosyaları (*.png)'
                )
                
                if save_path:
                    import shutil
                    shutil.copy2(qr_data[4], save_path)
                    QMessageBox.information(self, 'Başarılı', f'QR kod başarıyla kaydedildi:\n{save_path}')
            else:
                QMessageBox.warning(self, 'Uyarı', 'QR kod dosyası bulunamadı!')
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'QR kod indirilirken hata oluştu: {str(e)}')
    
    def delete_qr_code(self):
        """QR kodu sil"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz QR kodu seçin!')
            return
        
        qr_id = int(self.table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, 'Onay', 
            'Bu QR kodu silmek istediğinizden emin misiniz?\n\nDosya da silinecektir!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Önce dosya yolunu al
                cursor.execute('SELECT qr_image_path FROM qr_codes WHERE id = ?', (qr_id,))
                result = cursor.fetchone()
                
                if result and result[0] and os.path.exists(result[0]):
                    os.remove(result[0])  # Dosyayı sil
                
                # Veritabanından sil
                cursor.execute('DELETE FROM qr_codes WHERE id = ?', (qr_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Başarılı', 'QR kod başarıyla silindi!')
                self.load_qr_codes()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'QR kod silinirken hata oluştu: {str(e)}')
    
    def generate_qr_code(self):
        """Tek QR kod oluştur"""
        businesses = self.db.get_businesses()
        if not businesses:
            QMessageBox.warning(self, 'Uyarı', 'Önce bir işletme oluşturmalısınız!')
            return
        
        dialog = QRGenerateDialog(self, businesses)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.create_qr_code_file(data)
    
    def bulk_generate_qr(self):
        """Toplu QR kod oluştur"""
        businesses = self.db.get_businesses()
        if not businesses:
            QMessageBox.warning(self, 'Uyarı', 'Önce bir işletme oluşturmalısınız!')
            return
        
        dialog = BulkQRDialog(self, businesses)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.create_bulk_qr_codes(data)
    
    def create_qr_code_file(self, data):
        """QR kod dosyasını oluştur ve veritabanına kaydet"""
        try:
            # URL'yi oluştur
            business_slug = self.get_business_slug(data['business_id'])
            if data['table_number']:
                qr_url = f"https://qrmenu.com/{business_slug}/menu{data['menu_type']}?table={data['table_number']}"
            else:
                qr_url = f"https://qrmenu.com/{business_slug}/menu{data['menu_type']}"
            
            # QR kod oluştur
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # Resim oluştur
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Dosya yolu oluştur
            if not os.path.exists('qr_codes'):
                os.makedirs('qr_codes')
            
            filename = f"qr_{business_slug}_menu{data['menu_type']}"
            if data['table_number']:
                filename += f"_table{data['table_number']}"
            filename += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            file_path = os.path.join('qr_codes', filename)
            img.save(file_path)
            
            # Veritabanına kaydet
            qr_id = self.db.save_qr_code(
                data['business_id'], 
                data['menu_type'], 
                qr_url, 
                file_path, 
                data['table_number']
            )
            
            if qr_id:
                QMessageBox.information(self, 'Başarılı', 
                                      f'QR kod başarıyla oluşturuldu!\nDosya: {file_path}')
                self.load_qr_codes()
            else:
                QMessageBox.warning(self, 'Hata', 'QR kod kaydedilemedi!')
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'QR kod oluşturulurken hata oluştu: {str(e)}')
    
    def create_bulk_qr_codes(self, data):
        """Toplu QR kod oluştur"""
        try:
            business_slug = self.get_business_slug(data['business_id'])
            created_count = 0
            
            for table_num in range(data['start_table'], data['end_table'] + 1):
                # URL'yi oluştur
                qr_url = f"https://qrmenu.com/{business_slug}/menu{data['menu_type']}?table={table_num}"
                
                # QR kod oluştur
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_url)
                qr.make(fit=True)
                
                # Resim oluştur
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Dosya yolu
                if not os.path.exists('qr_codes'):
                    os.makedirs('qr_codes')
                
                filename = f"qr_{business_slug}_menu{data['menu_type']}_table{table_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                file_path = os.path.join('qr_codes', filename)
                img.save(file_path)
                
                # Veritabanına kaydet
                self.db.save_qr_code(data['business_id'], data['menu_type'], qr_url, file_path, table_num)
                created_count += 1
            
            QMessageBox.information(self, 'Başarılı', 
                                  f'{created_count} adet QR kod başarıyla oluşturuldu!\nKlasör: qr_codes/')
            self.load_qr_codes()
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Toplu QR kod oluşturulurken hata oluştu: {str(e)}')


class QRGenerateDialog(QDialog):
    def __init__(self, parent=None, businesses=None):
        super().__init__(parent)
        self.businesses = businesses or []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('QR Kod Oluştur')
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('QR Kod Oluştur')
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
        
        # İşletme seçimi
        self.business_combo = QComboBox()
        for business in self.businesses:
            self.business_combo.addItem(business[1], business[0])  # name, id
        form_layout.addRow('İşletme:', self.business_combo)
        
        # Menü tipi
        self.menu_combo = QComboBox()
        self.menu_combo.addItems(['Menü 1', 'Menü 2', 'Menü 3'])
        form_layout.addRow('Menü Tipi:', self.menu_combo)
        
        # Masa numarası
        self.table_spin = QSpinBox()
        self.table_spin.setMinimum(0)
        self.table_spin.setMaximum(999)
        self.table_spin.setSpecialValueText('Genel (Masa belirtilmesin)')
        form_layout.addRow('Masa Numarası:', self.table_spin)
        
        layout.addLayout(form_layout)
        
        # Bilgi
        info_label = QLabel('QR kod oluşturulduktan sonra "qr_codes" klasörüne kaydedilecektir.')
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
                margin: 10px 0;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton('Oluştur')
        create_btn.clicked.connect(self.accept)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        layout.addLayout(button_layout)
    
    def get_data(self):
        """Form verilerini döndür"""
        return {
            'business_id': self.business_combo.currentData(),
            'menu_type': self.menu_combo.currentIndex() + 1,
            'table_number': self.table_spin.value() if self.table_spin.value() > 0 else None
        }


class BulkQRDialog(QDialog):
    def __init__(self, parent=None, businesses=None):
        super().__init__(parent)
        self.businesses = businesses or []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Toplu QR Kod Oluştur')
        self.setModal(True)
        self.resize(400, 350)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Toplu QR Kod Oluştur')
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
        
        # İşletme seçimi
        self.business_combo = QComboBox()
        for business in self.businesses:
            self.business_combo.addItem(business[1], business[0])  # name, id
        form_layout.addRow('İşletme:', self.business_combo)
        
        # Menü tipi
        self.menu_combo = QComboBox()
        self.menu_combo.addItems(['Menü 1', 'Menü 2', 'Menü 3'])
        form_layout.addRow('Menü Tipi:', self.menu_combo)
        
        # Başlangıç masa
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setMaximum(999)
        self.start_spin.setValue(1)
        form_layout.addRow('Başlangıç Masa:', self.start_spin)
        
        # Bitiş masa
        self.end_spin = QSpinBox()
        self.end_spin.setMinimum(1)
        self.end_spin.setMaximum(999)
        self.end_spin.setValue(10)
        form_layout.addRow('Bitiş Masa:', self.end_spin)
        
        layout.addLayout(form_layout)
        
        # Bilgi
        info_label = QLabel('Belirttiğiniz masa aralığında her masa için ayrı QR kod oluşturulacaktır. Örneğin 1-10 arası seçerseniz 10 adet QR kod oluşturulur.')
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
                margin: 10px 0;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton('Toplu Oluştur')
        create_btn.clicked.connect(self.accept)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        layout.addLayout(button_layout)
    
    def get_data(self):
        """Form verilerini döndür"""
        return {
            'business_id': self.business_combo.currentData(),
            'menu_type': self.menu_combo.currentIndex() + 1,
            'start_table': self.start_spin.value(),
            'end_table': self.end_spin.value()
        }
    
    def accept(self):
        """Kaydetmeden önce validasyon"""
        if self.start_spin.value() > self.end_spin.value():
            QMessageBox.warning(self, 'Uyarı', 'Başlangıç masa numarası bitiş masa numarasından büyük olamaz!')
            return
        
        count = self.end_spin.value() - self.start_spin.value() + 1
        if count > 100:
            reply = QMessageBox.question(
                self, 'Onay',
                f'{count} adet QR kod oluşturulacak. Devam etmek istiyor musunuz?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        super().accept()


class QRViewDialog(QDialog):
    def __init__(self, parent=None, qr_data=None):
        super().__init__(parent)
        self.qr_data = qr_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('QR Kod Görüntüle')
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('QR Kod Detayları')
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
        
        if self.qr_data:
            # QR kod resmi
            image_path = None
            if len(self.qr_data) > 4:
                image_path = self.qr_data[4]
            if image_path and os.path.exists(image_path):  # qr_image_path
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                qr_image = QLabel()
                qr_image.setPixmap(scaled_pixmap)
                qr_image.setAlignment(Qt.AlignCenter)
                qr_image.setStyleSheet("""
                    QLabel {
                        border: 2px solid #bdc3c7;
                        border-radius: 8px;
                        padding: 10px;
                        background-color: white;
                    }
                """)
                layout.addWidget(qr_image)
            
            # Bilgiler
            info_layout = QFormLayout()
            
            # indices according to qr_codes table: (id, business_id, menu_type, url, qr_image_path, table_number, created_at)
            info_layout.addRow('Menü Tipi:', QLabel(f'Menü {self.qr_data[2]}'))
            info_layout.addRow('Masa Numarası:', QLabel(str(self.qr_data[5]) if self.qr_data[5] else 'Genel'))
            
            url_label = QLabel(self.qr_data[3] if len(self.qr_data) > 3 else '')
            url_label.setWordWrap(True)
            url_label.setStyleSheet('QLabel { color: #3498db; }')
            info_layout.addRow('URL:', url_label)
            
            info_layout.addRow('Oluşturulma:', QLabel(str(self.qr_data[6]) if len(self.qr_data) > 6 else 'Bilinmiyor'))
            
            layout.addLayout(info_layout)
        
        # Kapat butonu
        close_btn = QPushButton('Kapat')
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        layout.addWidget(close_btn)
