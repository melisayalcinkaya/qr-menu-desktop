from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QFrame, QPushButton, QScrollArea,
                            QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
import sqlite3

class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.stat_cards = {}  # ÖNEMLİ: İlk önce tanımla
        self.init_ui()
        self.setup_timer()
        QTimer.singleShot(200, self.refresh_data)  # UI hazır olduktan sonra yükle
    
    def init_ui(self):
        # Ana scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Ana widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Başlık
        title = QLabel('Dashboard - Genel Bakış')
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
        main_layout.addWidget(title)
        
        # İstatistik kartları
        stats_layout = QGridLayout()
        
        # Kartları oluştur
        self.create_stat_cards(stats_layout)
        main_layout.addLayout(stats_layout)
        
        # Son aktiviteler bölümü
        activities_layout = QVBoxLayout()
        
        activities_title = QLabel('Son Aktiviteler')
        activities_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px 0 10px 0;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
            }
        """)
        activities_layout.addWidget(activities_title)
        
        # Aktivite tablosu
        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(4)
        self.activities_table.setHorizontalHeaderLabels(['Tür', 'İşletme', 'Detay', 'Tarih'])
        self.activities_table.setMaximumHeight(300)
        self.activities_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        activities_layout.addWidget(self.activities_table)
        
        main_layout.addLayout(activities_layout)
        
        # Yenile butonu
        refresh_btn = QPushButton('🔄 Verileri Yenile')
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                margin: 20px 0;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        main_layout.addWidget(refresh_btn)
        
        main_layout.addStretch()
        
        scroll.setWidget(main_widget)
        
        # Ana layout
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def create_stat_cards(self, layout):
        """İstatistik kartlarını oluştur"""
        # Kart bilgileri: (başlık, değer_attr, renk, ikon)
        cards_info = [
            ('Toplam İşletme', 'businesses_count', '#27ae60', '🏢'),
            ('Toplam Kategori', 'categories_count', '#e74c3c', '📋'),
            ('Toplam Ürün', 'products_count', '#f39c12', '🍽️'),
            ('Bekleyen Yorumlar', 'pending_comments', '#9b59b6', '💬'),
            ('Garson Çağrıları', 'waiter_calls', '#e67e22', '🔔'),
            ('Aktif QR Kodlar', 'qr_codes_count', '#1abc9c', '📱')
        ]
        
        for i, (title, attr, color, icon) in enumerate(cards_info):
            card = self.create_stat_card(title, '0', color, icon)
            self.stat_cards[attr] = card
            
            row = i // 3
            col = i % 3
            layout.addWidget(card, row, col)
    
    def create_stat_card(self, title, value, color, icon):
        """Tek bir istatistik kartı oluştur"""
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }}
            QFrame:hover {{
                border-color: {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout()
        card.setLayout(layout)
        
        # Üst kısım - ikon ve değer
        top_layout = QHBoxLayout()
        
        # İkon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                color: {color};
                background-color: rgba({self.hex_to_rgba(color)}, 0.1);
                border-radius: 20px;
                padding: 8px;
                max-width: 40px;
                max-height: 40px;
            }}
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        # Değer
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
            }}
        """)
        value_label.setAlignment(Qt.AlignRight)
        top_layout.addWidget(value_label)
        
        layout.addLayout(top_layout)
        
        # Alt kısım - başlık
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
                margin-top: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Değer labelını kart nesnesine ekle (daha sonra güncellemek için)
        card.value_label = value_label
        
        return card
    
    def hex_to_rgba(self, hex_color):
        """Hex rengi RGBA'ya çevir"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    
    def setup_timer(self):
        """Otomatik yenileme timer'ı"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # 30 saniyede bir yenile
    
    def refresh_data(self):
        """Tüm verileri yenile"""
        try:
            self.load_statistics()
            self.load_recent_activities()
        except Exception as e:
            import traceback
            print(f"Veri yenileme hatası: {e}")
            print(traceback.format_exc())
    
    def load_statistics(self):
        """İstatistikleri yükle"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # İşletme sayısı
            cursor.execute('SELECT COUNT(*) FROM businesses WHERE is_active = 1')
            result = cursor.fetchone()
            businesses_count = result[0] if result else 0
            if 'businesses_count' in self.stat_cards:
                self.stat_cards['businesses_count'].value_label.setText(str(businesses_count))
                self.stat_cards['businesses_count'].value_label.update()
            
            # Kategori sayısı
            cursor.execute('SELECT COUNT(*) FROM categories WHERE is_active = 1')
            result = cursor.fetchone()
            categories_count = result[0] if result else 0
            if 'categories_count' in self.stat_cards:
                self.stat_cards['categories_count'].value_label.setText(str(categories_count))
                self.stat_cards['categories_count'].value_label.update()
            
            # Ürün sayısı
            cursor.execute('SELECT COUNT(*) FROM products WHERE is_available = 1')
            result = cursor.fetchone()
            products_count = result[0] if result else 0
            if 'products_count' in self.stat_cards:
                self.stat_cards['products_count'].value_label.setText(str(products_count))
                self.stat_cards['products_count'].value_label.update()
            
            # Bekleyen yorumlar
            cursor.execute('SELECT COUNT(*) FROM comments WHERE is_approved = 0')
            result = cursor.fetchone()
            pending_comments = result[0] if result else 0
            if 'pending_comments' in self.stat_cards:
                self.stat_cards['pending_comments'].value_label.setText(str(pending_comments))
                self.stat_cards['pending_comments'].value_label.update()
            
            # Garson çağrıları
            cursor.execute('SELECT COUNT(*) FROM waiter_calls WHERE status = "pending"')
            result = cursor.fetchone()
            waiter_calls = result[0] if result else 0
            if 'waiter_calls' in self.stat_cards:
                self.stat_cards['waiter_calls'].value_label.setText(str(waiter_calls))
                self.stat_cards['waiter_calls'].value_label.update()
            
            # QR kod sayısı
            cursor.execute('SELECT COUNT(*) FROM qr_codes')
            result = cursor.fetchone()
            qr_codes_count = result[0] if result else 0
            if 'qr_codes_count' in self.stat_cards:
                self.stat_cards['qr_codes_count'].value_label.setText(str(qr_codes_count))
                self.stat_cards['qr_codes_count'].value_label.update()
            
            conn.close()
            
            # Tüm widgetları güncelle
            self.update()
            QTimer.singleShot(50, self.update)  # Ekstra güncelleme
            
            print(f"İstatistikler yüklendi: İşletme={businesses_count}, Kategori={categories_count}, Ürün={products_count}")
            
        except Exception as e:
            import traceback
            print(f"İstatistik yükleme hatası: {e}")
            print(traceback.format_exc())
    
    def load_recent_activities(self):
        """Son aktiviteleri yükle"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            activities = []
            
            # Son eklenen işletmeler
            try:
                cursor.execute('''
                    SELECT 'İşletme' as type, name, 'Yeni işletme eklendi', created_at 
                    FROM businesses 
                    WHERE is_active = 1 
                    ORDER BY created_at DESC 
                    LIMIT 5
                ''')
                activities.extend(cursor.fetchall())
            except:
                pass
            
            # Son eklenen ürünler
            try:
                cursor.execute('''
                    SELECT 'Ürün' as type, b.name, p.name || ' ürünü eklendi', p.created_at
                    FROM products p
                    JOIN businesses b ON p.business_id = b.id
                    WHERE p.is_available = 1
                    ORDER BY p.created_at DESC
                    LIMIT 5
                ''')
                activities.extend(cursor.fetchall())
            except:
                pass
            
            # Son yorumlar
            try:
                cursor.execute('''
                    SELECT 'Yorum' as type, b.name, 
                           CASE WHEN c.is_approved = 1 THEN 'Yeni yorum onaylandı' 
                                ELSE 'Yeni yorum bekliyor' END,
                           c.created_at
                    FROM comments c
                    JOIN businesses b ON c.business_id = b.id
                    ORDER BY c.created_at DESC
                    LIMIT 5
                ''')
                activities.extend(cursor.fetchall())
            except:
                pass
            
            # Son garson çağrıları
            try:
                cursor.execute('''
                    SELECT 'Garson' as type, b.name, 
                           'Masa ' || w.table_number || ' garson çağırdı',
                           w.created_at
                    FROM waiter_calls w
                    JOIN businesses b ON w.business_id = b.id
                    WHERE w.status = 'pending'
                    ORDER BY w.created_at DESC
                    LIMIT 5
                ''')
                activities.extend(cursor.fetchall())
            except:
                pass
            
            conn.close()
            
            # Tarihe göre sırala - None değerleri kontrol et
            activities = [a for a in activities if a[3] is not None]
            if activities:
                activities.sort(key=lambda x: str(x[3]), reverse=True)
                activities = activities[:20]
            
            # Tabloya ekle
            self.activities_table.setRowCount(len(activities))
            for row, activity in enumerate(activities):
                self.activities_table.setItem(row, 0, QTableWidgetItem(str(activity[0])))
                self.activities_table.setItem(row, 1, QTableWidgetItem(str(activity[1])))
                self.activities_table.setItem(row, 2, QTableWidgetItem(str(activity[2])))
                
                # Tarihi formatla
                date_str = str(activity[3]) if activity[3] else ''
                if len(date_str) > 16:
                    date_str = date_str[:16].replace('T', ' ')
                self.activities_table.setItem(row, 3, QTableWidgetItem(date_str))
            
            # Sütun genişliklerini ayarla
            self.activities_table.resizeColumnsToContents()
            
            print(f"{len(activities)} aktivite yüklendi")
            
        except Exception as e:
            import traceback
            print(f"Aktivite yükleme hatası: {e}")
            print(traceback.format_exc())
    
    def closeEvent(self, event):
        """Sayfa kapatılırken timer'ı durdur"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()