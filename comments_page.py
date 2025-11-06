from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                            QHeaderView, QComboBox, QTextEdit, QDialog, QFormLayout,
                            QSpinBox, QGroupBox, QCheckBox, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CommentsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_business_id = None
        self.filter_status = 'all'  # all, approved, pending
        self.init_ui()
        self.load_businesses()
        self.load_comments()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Yorum Yönetimi')
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                border-bottom: 2px solid #9b59b6;
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
        self.status_combo.addItems(['Tümü', 'Onaylı', 'Bekleyen'])
        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        filter_layout.addWidget(self.status_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.approve_button = QPushButton('✓ Onayla')
        self.approve_button.clicked.connect(self.approve_comment)
        self.approve_button.setStyleSheet("""
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
        
        self.reject_button = QPushButton('✗ Reddet')
        self.reject_button.clicked.connect(self.reject_comment)
        self.reject_button.setStyleSheet("""
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
        
        self.delete_button = QPushButton('🗑 Sil')
        self.delete_button.clicked.connect(self.delete_comment)
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
        
        self.add_button = QPushButton('+ Yorum Ekle')
        self.add_button.clicked.connect(self.add_comment)
        self.add_button.setStyleSheet("""
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
        self.refresh_button.clicked.connect(self.load_comments)
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
        
        button_layout.addWidget(self.approve_button)
        button_layout.addWidget(self.reject_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'İşletme', 'Yazar', 'Rating', 'Durum', 'Tarih'
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
                background-color: #9b59b6;
                color: white;
            }
            QHeaderView::section {
                background-color: #8e44ad;
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
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Yazar
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Rating
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Durum
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Tarih
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.view_comment_detail)
        layout.addWidget(self.table)
        
        # Yorum detayı alanı
        detail_group = QGroupBox('Seçili Yorumun Detayı')
        detail_group.setStyleSheet("""
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
        detail_layout = QVBoxLayout()
        
        self.comment_detail = QTextEdit()
        self.comment_detail.setMaximumHeight(100)
        self.comment_detail.setReadOnly(True)
        self.comment_detail.setPlaceholderText('Bir yorum seçin...')
        self.comment_detail.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                color: #495057;
            }
        """)
        
        detail_layout.addWidget(self.comment_detail)
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
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
        
        # Tablo seçimi değiştiğinde
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
    
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
        self.load_comments()
    
    def on_status_changed(self):
        """Durum filtresi değiştiğinde"""
        status_map = {'Tümü': 'all', 'Onaylı': 'approved', 'Bekleyen': 'pending'}
        self.filter_status = status_map[self.status_combo.currentText()]
        self.load_comments()
    
    def load_comments(self):
        """Yorumları yükle"""
        try:
            comments = self.db.get_comments(self.current_business_id)
            
            # Durum filtresini uygula
            if self.filter_status == 'approved':
                comments = [c for c in comments if c[5]]  # is_approved
            elif self.filter_status == 'pending':
                comments = [c for c in comments if not c[5]]
            
            self.table.setRowCount(len(comments))
            
            # İşletme isimlerini al
            businesses = {b[0]: b[1] for b in self.db.get_businesses()}
            
            for row, comment in enumerate(comments):
                self.table.setItem(row, 0, QTableWidgetItem(str(comment[0])))  # ID
                
                # İşletme adı
                business_name = businesses.get(comment[4], 'Bilinmiyor')
                self.table.setItem(row, 1, QTableWidgetItem(business_name))
                
                self.table.setItem(row, 2, QTableWidgetItem(comment[3] or 'Anonim'))  # Author
                
                # Rating yıldızlarla göster
                rating = comment[2] or 0
                stars = '★' * rating + '☆' * (5 - rating)
                self.table.setItem(row, 3, QTableWidgetItem(f'{stars} ({rating})'))
                
                # Durum
                status = 'Onaylı' if comment[5] else 'Bekliyor'
                self.table.setItem(row, 4, QTableWidgetItem(status))
                
                # Tarih
                created_at = comment[6] or ''
                if len(created_at) > 10:
                    created_at = created_at[:10]
                self.table.setItem(row, 5, QTableWidgetItem(created_at))
            
            # İstatistik güncelle
            business_name = self.business_combo.currentText()
            status_name = self.status_combo.currentText()
            approved_count = len([c for c in comments if c[5]])
            pending_count = len(comments) - approved_count
            total_count = len(comments)
            
            self.stats_label.setText(
                f'{business_name} - {status_name} | '
                f'Toplam: {total_count} yorum | Onaylı: {approved_count} | Bekleyen: {pending_count}'
            )
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Yorumlar yüklenirken hata oluştu: {str(e)}')
    
    def on_selection_changed(self):
        """Tablo seçimi değiştiğinde yorum detayını göster"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            comment_id = int(self.table.item(current_row, 0).text())
            comments = self.db.get_comments()
            comment = next((c for c in comments if c[0] == comment_id), None)
            
            if comment:
                self.comment_detail.setPlainText(comment[1] or 'Yorum metni yok')
            else:
                self.comment_detail.clear()
        else:
            self.comment_detail.clear()
    
    def view_comment_detail(self):
        """Yorum detayını ayrı pencerede göster"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        comment_id = int(self.table.item(current_row, 0).text())
        comments = self.db.get_comments()
        comment = next((c for c in comments if c[0] == comment_id), None)
        
        if comment:
            dialog = CommentDetailDialog(self, comment)
            dialog.exec_()
    
    def approve_comment(self):
        """Yorumu onayla"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen onaylamak istediğiniz yorumu seçin!')
            return
        
        comment_id = int(self.table.item(current_row, 0).text())
        
        try:
            self.db.approve_comment(comment_id)
            QMessageBox.information(self, 'Başarılı', 'Yorum başarıyla onaylandı!')
            self.load_comments()
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Yorum onaylanırken hata oluştu: {str(e)}')
    
    def reject_comment(self):
        """Yorumu reddet (onayı kaldır)"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen reddetmek istediğiniz yorumu seçin!')
            return
        
        comment_id = int(self.table.item(current_row, 0).text())
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE comments SET is_approved = 0 WHERE id = ?', (comment_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, 'Başarılı', 'Yorum reddedildi!')
            self.load_comments()
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Yorum reddedilirken hata oluştu: {str(e)}')
    
    def delete_comment(self):
        """Yorumu sil"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz yorumu seçin!')
            return
        
        comment_id = int(self.table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, 'Onay', 
            'Bu yorumu silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_comment(comment_id)
                QMessageBox.information(self, 'Başarılı', 'Yorum başarıyla silindi!')
                self.load_comments()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Yorum silinirken hata oluştu: {str(e)}')
    
    def add_comment(self):
        """Test yorumu ekle"""
        businesses = self.db.get_businesses()
        if not businesses:
            QMessageBox.warning(self, 'Uyarı', 'Önce bir işletme oluşturmalısınız!')
            return
        
        dialog = AddCommentDialog(self, businesses)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO comments (text, rating, author, business_id, is_approved)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data['text'], data['rating'], data['author'], data['business_id'], data['is_approved']))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Başarılı', 'Yorum başarıyla eklendi!')
                self.load_comments()
                
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Yorum eklenirken hata oluştu: {str(e)}')


class CommentDetailDialog(QDialog):
    def __init__(self, parent=None, comment_data=None):
        super().__init__(parent)
        self.comment_data = comment_data
        self.init_ui()
        
        if comment_data:
            self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('Yorum Detayı')
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Yorum Detayları')
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
        
        # Bilgi alanları
        info_layout = QFormLayout()
        
        self.author_label = QLabel()
        info_layout.addRow('Yazar:', self.author_label)
        
        self.rating_label = QLabel()
        info_layout.addRow('Puan:', self.rating_label)
        
        self.date_label = QLabel()
        info_layout.addRow('Tarih:', self.date_label)
        
        self.status_label = QLabel()
        info_layout.addRow('Durum:', self.status_label)
        
        layout.addLayout(info_layout)
        
        # Yorum metni
        layout.addWidget(QLabel('Yorum:'))
        self.comment_text = QTextEdit()
        self.comment_text.setReadOnly(True)
        self.comment_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.comment_text)
        
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
    
    def load_data(self):
        """Yorum verilerini yükle"""
        if self.comment_data:
            self.author_label.setText(self.comment_data[3] or 'Anonim')
            
            rating = self.comment_data[2] or 0
            stars = '★' * rating + '☆' * (5 - rating)
            self.rating_label.setText(f'{stars} ({rating}/5)')
            
            self.date_label.setText(self.comment_data[6] or 'Bilinmiyor')
            
            status = 'Onaylı' if self.comment_data[5] else 'Bekliyor'
            self.status_label.setText(status)
            
            self.comment_text.setPlainText(self.comment_data[1] or 'Yorum metni yok')


class AddCommentDialog(QDialog):
    def __init__(self, parent=None, businesses=None):
        super().__init__(parent)
        self.businesses = businesses or []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Test Yorumu Ekle')
        self.setModal(True)
        self.resize(400, 350)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Başlık
        title = QLabel('Yeni Yorum Ekle')
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
        
        # Yazar
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText('Yorum yazarının adı')
        form_layout.addRow('Yazar:', self.author_edit)
        
        # Puan
        self.rating_spin = QSpinBox()
        self.rating_spin.setMinimum(1)
        self.rating_spin.setMaximum(5)
        self.rating_spin.setValue(5)
        form_layout.addRow('Puan (1-5):', self.rating_spin)
        
        # Onaylı mı
        self.approved_check = QCheckBox('Otomatik onayla')
        self.approved_check.setChecked(True)
        form_layout.addRow('', self.approved_check)
        
        layout.addLayout(form_layout)
        
        # Yorum metni
        layout.addWidget(QLabel('Yorum Metni:'))
        self.comment_text = QTextEdit()
        self.comment_text.setMaximumHeight(120)
        self.comment_text.setPlaceholderText('Yorum içeriğini buraya yazın...')
        layout.addWidget(self.comment_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('Kaydet')
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
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
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
    
    def get_data(self):
        """Form verilerini döndür"""
        return {
            'business_id': self.business_combo.currentData(),
            'author': self.author_edit.text().strip() or 'Anonim',
            'rating': self.rating_spin.value(),
            'text': self.comment_text.toPlainText().strip(),
            'is_approved': self.approved_check.isChecked()
        }
    
    def accept(self):
        """Kaydetmeden önce validasyon"""
        if not self.comment_text.toPlainText().strip():
            QMessageBox.warning(self, 'Uyarı', 'Yorum metni boş olamaz!')
            return
        
        super().accept()