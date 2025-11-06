from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                            QHeaderView, QComboBox, QDialog, QFormLayout,
                            QSpinBox, QLineEdit, QTextEdit, QGroupBox, QCheckBox,
                            QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta

class WaiterPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_business_id = None
        self.filter_status = 'pending'  # pending, resolved, all
        self.init_ui()
        self.setup_timer()
        self.load_businesses()
        self.load_waiter_calls()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Garson Çağırma Yönetimi')
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                border-bottom: 2px solid #e67e22;
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
        
        # Durum filtresi
        filter_layout.addWidget(QLabel('Durum:'))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Bekleyen', 'Çözülmüş', 'Tümü'])
        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        filter_layout.addWidget(self.status_combo)
        
        # Otomatik yenile checkbox
        self.auto_refresh_check = QCheckBox('Otomatik Yenile (10sn)')
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        filter_layout.addWidget(self.auto_refresh_check)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.resolve_button = QPushButton('✓ Çöz')
        self.resolve_button.clicked.connect(self.resolve_call)
        self.resolve_button.setStyleSheet("""
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
        
        self.bulk_resolve_button = QPushButton('✓ Seçilileri Çöz')
        self.bulk_resolve_button.clicked.connect(self.bulk_resolve_calls)
        self.bulk_resolve_button.setStyleSheet("""
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
        self.delete_button.clicked.connect(self.delete_call)
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
        
        self.test_call_button = QPushButton('+ Test Çağrı')
        self.test_call_button.clicked.connect(self.add_test_call)
        self.test_call_button.setStyleSheet("""
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
        self.refresh_button.clicked.connect(self.load_waiter_calls)
        self.refresh_button.setStyleSheet("""
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
        
        button_layout.addWidget(self.resolve_button)
        button_layout.addWidget(self.bulk_resolve_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.test_call_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'İşletme', 'Masa No', 'Mesaj', 'Durum', 'Çağrı Zamanı'
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
                background-color: #e67e22;
                color: white;
            }
            QHeaderView::section {
                background-color: #d35400;
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
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Masa No
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Mesaj
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Durum
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Zaman
        
        # Çoklu seçim
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        layout.addWidget(self.table)
        
        # Aktif çağrılar özeti
        summary_group = QGroupBox('Aktif Çağrılar - Özet')
        summary_group.setStyleSheet("""
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
        summary_layout = QHBoxLayout()
        
        self.summary_label = QLabel('Yükleniyor...')
        self.summary_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                color: #495057;
            }
        """)
        summary_layout.addWidget(self.summary_label)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
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
    
    def setup_timer(self):
        """Otomatik yenileme timer'ı"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh)
        if self.auto_refresh_check.isChecked():
            self.timer.start(10000)  # 10 saniye
    
    def toggle_auto_refresh(self, state):
        """Otomatik yenilemeyi aç/kapat"""
        if state == Qt.Checked:
            self.timer.start(10000)  # 10 saniye
        else:
            self.timer.stop()
    
    def auto_refresh(self):
        """Otomatik yenileme"""
        if self.filter_status == 'pending':  # Sadece bekleyen çağrıları otomatik yenile
            self.load_waiter_calls()
    
    def load_businesses(self):
        """İşletmeleri yükle"""
        try:
            businesses = self.db.get_businesses()
            self.business_combo.clear()
            self.business_combo.addItem('Tüm İşletmeler', None)
            
            for business in businesses:
                self.business_combo.addItem(business[1], business[0])  # name, id
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'İşletmeler yüklenirken hata oluştu: {str(e)}')
    
    def on_business_changed(self):
        """İşletme değiştiğinde"""
        self.current_business_id = self.business_combo.currentData()
        self.load_waiter_calls()
    
    def on_status_changed(self):
        """Durum filtresi değiştiğinde"""
        status_map = {'Bekleyen': 'pending', 'Çözülmüş': 'resolved', 'Tümü': 'all'}
        self.filter_status = status_map[self.status_combo.currentText()]
        self.load_waiter_calls()
    
    def load_waiter_calls(self):
        """Garson çağrılarını yükle"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Sorgu oluştur
            if self.current_business_id:
                if self.filter_status == 'all':
                    cursor.execute('''
                        SELECT w.*, b.name as business_name 
                        FROM waiter_calls w
                        JOIN businesses b ON w.business_id = b.id
                        WHERE w.business_id = ?
                        ORDER BY w.created_at DESC
                    ''', (self.current_business_id,))
                else:
                    cursor.execute('''
                        SELECT w.*, b.name as business_name 
                        FROM waiter_calls w
                        JOIN businesses b ON w.business_id = b.id
                        WHERE w.business_id = ? AND w.status = ?
                        ORDER BY w.created_at DESC
                    ''', (self.current_business_id, self.filter_status))
            else:
                if self.filter_status == 'all':
                    cursor.execute('''
                        SELECT w.*, b.name as business_name 
                        FROM waiter_calls w
                        JOIN businesses b ON w.business_id = b.id
                        ORDER BY w.created_at DESC
                    ''')
                else:
                    cursor.execute('''
                        SELECT w.*, b.name as business_name 
                        FROM waiter_calls w
                        JOIN businesses b ON w.business_id = b.id
                        WHERE w.status = ?
                        ORDER BY w.created_at DESC
                    ''', (self.filter_status,))
            
            calls = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(calls))
            
            for row, call in enumerate(calls):
                self.table.setItem(row, 0, QTableWidgetItem(str(call[0])))     # ID
                self.table.setItem(row, 1, QTableWidgetItem(call[6]))          # Business name
                self.table.setItem(row, 2, QTableWidgetItem(f'Masa {call[1]}')) # Table number
                self.table.setItem(row, 3, QTableWidgetItem(call[3] or 'Garson çağırıldı')) # Message
                
                # Durum
                status_text = 'Bekliyor' if call[4] == 'pending' else 'Çözüldü'
                status_item = QTableWidgetItem(status_text)
                
                # Durum rengini ayarla
                if call[4] == 'pending':
                    status_item.setStyleSheet('color: #e74c3c; font-weight: bold;')
                else:
                    status_item.setStyleSheet('color: #27ae60; font-weight: bold;')
                
                self.table.setItem(row, 4, status_item)
                
                # Zaman
                created_at = call[5] or ''
                if len(created_at) > 16:
                    created_at = created_at[:16].replace('T', ' ')
                self.table.setItem(row, 5, QTableWidgetItem(created_at))
            
            # Özet ve istatistik güncelle
            self.update_summary(calls)
            self.update_statistics(calls)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Garson çağrıları yüklenirken hata oluştu: {str(e)}')
    
    def update_summary(self, calls):
        """Aktif çağrılar özetini güncelle"""
        pending_calls = [c for c in calls if c[4] == 'pending']
        
        if not pending_calls:
            self.summary_label.setText('Şu anda bekleyen garson çağrısı bulunmuyor. ✅')
            self.summary_label.setStyleSheet("""
                QLabel {
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 12px;
                    color: #155724;
                }
            """)
        else:
            # Masa numaralarını grupla
            table_numbers = [f"Masa {call[1]}" for call in pending_calls]
            table_summary = ', '.join(sorted(set(table_numbers)))
            
            # En eski çağrı
            oldest_call = min(pending_calls, key=lambda x: x[5])
            oldest_time = oldest_call[5]
            
            summary_text = f"🔔 {len(pending_calls)} bekleyen çağrı: {table_summary}"
            if oldest_time:
                try:
                    call_time = datetime.fromisoformat(oldest_time.replace('Z', ''))
                    time_diff = datetime.now() - call_time
                    minutes = int(time_diff.total_seconds() / 60)
                    if minutes > 0:
                        summary_text += f"\nEn eski çağrı: {minutes} dakika önce"
                except:
                    pass
            
            self.summary_label.setText(summary_text)
            self.summary_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 12px;
                    color: #856404;
                }
            """)
    
    def update_statistics(self, calls):
        """İstatistikleri güncelle"""
        business_name = self.business_combo.currentText()
        status_name = self.status_combo.currentText()
        
        pending_count = len([c for c in calls if c[4] == 'pending'])
        resolved_count = len([c for c in calls if c[4] == 'resolved'])
        total_count = len(calls)
        
        self.stats_label.setText(
            f'{business_name} - {status_name} | '
            f'Toplam: {total_count} çağrı | Bekleyen: {pending_count} | Çözülmüş: {resolved_count}'
        )
    
    def resolve_call(self):
        """Seçili çağrıyı çöz"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen çözmek istediğiniz çağrıyı seçin!')
            return
        
        call_id = int(self.table.item(current_row, 0).text())
        table_number = self.table.item(current_row, 2).text()
        
        try:
            self.db.resolve_waiter_call(call_id)
            QMessageBox.information(self, 'Başarılı', f'{table_number} çağrısı çözüldü!')
            self.load_waiter_calls()
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Çağrı çözülürken hata oluştu: {str(e)}')
    
    def bulk_resolve_calls(self):
        """Seçili çağrıları toplu çöz"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen çözmek istediğiniz çağrıları seçin!')
            return
        
        reply = QMessageBox.question(
            self, 'Onay',
            f'{len(selected_rows)} çağrıyı çözmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                resolved_count = 0
                for row in selected_rows:
                    call_id = int(self.table.item(row, 0).text())
                    self.db.resolve_waiter_call(call_id)
                    resolved_count += 1
                
                QMessageBox.information(self, 'Başarılı', f'{resolved_count} çağrı çözüldü!')
                self.load_waiter_calls()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Çağrılar çözülürken hata oluştu: {str(e)}')
    
    def delete_call(self):
        """Çağrıyı sil"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz çağrıyı seçin!')
            return
        
        call_id = int(self.table.item(current_row, 0).text())
        table_number = self.table.item(current_row, 2).text()
        
        reply = QMessageBox.question(
            self, 'Onay',
            f'{table_number} çağrısını silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM waiter_calls WHERE id = ?', (call_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Başarılı', 'Çağrı başarıyla silindi!')
                self.load_waiter_calls()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Çağrı silinirken hata oluştu: {str(e)}')
    
    def add_test_call(self):
        """Test garson çağrısı ekle"""
        businesses = self.db.get_businesses()
        if not businesses:
            QMessageBox.warning(self, 'Uyarı', 'Önce bir işletme oluşturmalısınız!')
            return
        
        dialog = TestCallDialog(self, businesses)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO waiter_calls (table_number, business_id, message, status)
                    VALUES (?, ?, ?, 'pending')
                ''', (data['table_number'], data['business_id'], data['message']))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Başarılı', 'Test çağrısı oluşturuldu!')
                self.load_waiter_calls()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Test çağrısı oluşturulurken hata oluştu: {str(e)}')
    
    def closeEvent(self, event):
        """Sayfa kapatılırken timer'ı durdur"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()


class TestCallDialog(QDialog):
    def __init__(self, parent=None, businesses=None):
        super().__init__(parent)
        self.businesses = businesses or []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Test Garson Çağrısı')
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Test Garson Çağrısı Oluştur')
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
        
        # Masa numarası
        self.table_spin = QSpinBox()
        self.table_spin.setMinimum(1)
        self.table_spin.setMaximum(999)
        self.table_spin.setValue(1)
        form_layout.addRow('Masa Numarası:', self.table_spin)
        
        layout.addLayout(form_layout)
        
        # Mesaj seçimi
        message_group = QGroupBox('Çağrı Mesajı')
        message_layout = QVBoxLayout()
        
        self.message_group = QButtonGroup()
        
        messages = [
            'Garson çağırıldı',
            'Hesap istiyoruz',
            'Menü istiyoruz',
            'Su istiyoruz',
            'Sipariş vermek istiyoruz',
            'Yardım gerekiyor'
        ]
        
        for i, msg in enumerate(messages):
            radio = QRadioButton(msg)
            if i == 0:  # İlk seçeneği varsayılan yap
                radio.setChecked(True)
            self.message_group.addButton(radio, i)
            message_layout.addWidget(radio)
        
        # Özel mesaj
        custom_layout = QHBoxLayout()
        self.custom_radio = QRadioButton('Özel:')
        self.message_group.addButton(self.custom_radio, len(messages))
        self.custom_edit = QLineEdit()
        self.custom_edit.setPlaceholderText('Özel mesaj yazın...')
        self.custom_edit.setEnabled(False)
        
        self.custom_radio.toggled.connect(lambda checked: self.custom_edit.setEnabled(checked))
        
        custom_layout.addWidget(self.custom_radio)
        custom_layout.addWidget(self.custom_edit)
        message_layout.addLayout(custom_layout)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # Bilgi
        info_label = QLabel('Test amaçlı garson çağrısı oluşturulacak. Gerçek bir müşteri çağrısı değildir.')
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
                background-color: #e67e22;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
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
        # Seçili mesajı bul
        selected_id = self.message_group.checkedId()
        
        messages = [
            'Garson çağırıldı',
            'Hesap istiyoruz',
            'Menü istiyoruz',
            'Su istiyoruz',
            'Sipariş vermek istiyoruz',
            'Yardım gerekiyor'
        ]
        
        if selected_id < len(messages):
            message = messages[selected_id]
        else:
            message = self.custom_edit.text().strip() or 'Garson çağırıldı'
        
        return {
            'business_id': self.business_combo.currentData(),
            'table_number': self.table_spin.value(),
            'message': message
        }