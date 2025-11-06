import sqlite3
import os
import hashlib
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = 'qrmenu.db'
        self.init_database()
    
    def init_database(self):
        """Tüm tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Kullanıcılar tablosu (Login/Register için)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'admin',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. İşletmeler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                phone TEXT,
                address TEXT,
                logo TEXT,
                qr_code TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. Kategoriler tablosu (3 menü tipi için)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                business_id INTEGER,
                menu_type INTEGER DEFAULT 1,
                banner_image TEXT,
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # 4. Ürünler tablosu (3 menü tipi için)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image TEXT,
                category_id INTEGER,
                business_id INTEGER,
                menu_type INTEGER DEFAULT 1,
                rating REAL DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                is_available BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # 5. Yorumlar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                author TEXT DEFAULT 'Anonim',
                business_id INTEGER,
                is_approved BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # 6. Garson çağırma tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waiter_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER NOT NULL,
                business_id INTEGER,
                message TEXT DEFAULT 'Garson çağırıldı',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # 7. WiFi ayarları tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wifi_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                wifi_name TEXT NOT NULL,
                wifi_password TEXT,
                is_public BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # 8. QR kodları tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qr_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                menu_type INTEGER,
                qr_url TEXT NOT NULL,
                qr_image_path TEXT,
                table_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Varsayılan admin kullanıcı oluştur
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            admin_password = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_password, 'admin@qrmenu.com', 'admin'))
        
        conn.commit()
        conn.close()
        print("Veritabanı başarıyla oluşturuldu!")
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def hash_password(self, password):
        """Şifreyi hash'le"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ===== KULLANICI İŞLEMLERİ =====
    def login(self, username, password):
        """Kullanıcı girişi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = self.hash_password(password)
        
        cursor.execute('''
            SELECT id, username, role FROM users 
            WHERE username = ? AND password = ? AND is_active = 1
        ''', (username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        return user
    
    def register_user(self, username, password, email='', role='admin'):
        """Yeni kullanıcı kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, email, role))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    # ===== İŞLETME İŞLEMLERİ =====
    def add_business(self, name, slug, description='', phone='', address='', logo=''):
        """İşletme ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO businesses (name, slug, description, phone, address, logo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, slug, description, phone, address, logo))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_businesses(self):
        """Tüm işletmeleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM businesses WHERE is_active = 1 ORDER BY created_at DESC')
        businesses = cursor.fetchall()
        conn.close()
        return businesses if businesses else []
    
    def update_business(self, business_id, name, slug, description='', phone='', address='', logo=''):
        """İşletme güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE businesses 
            SET name=?, slug=?, description=?, phone=?, address=?, logo=?
            WHERE id=?
        ''', (name, slug, description, phone, address, logo, business_id))
        conn.commit()
        conn.close()
    
    def delete_business(self, business_id):
        """İşletme sil (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE businesses SET is_active = 0 WHERE id = ?', (business_id,))
        conn.commit()
        conn.close()
    
    # ===== KATEGORİ İŞLEMLERİ =====
    def add_category(self, name, business_id, menu_type=1, banner_image=''):
        """Kategori ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name, business_id, menu_type, banner_image)
            VALUES (?, ?, ?, ?)
        ''', (name, business_id, menu_type, banner_image))
        conn.commit()
        category_id = cursor.lastrowid
        conn.close()
        return category_id
    
    def get_categories(self, business_id=None, menu_type=None):
        """Kategorileri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM categories WHERE is_active = 1'
        params = []
        
        if business_id:
            query += ' AND business_id = ?'
            params.append(business_id)
        
        if menu_type:
            query += ' AND menu_type = ?'
            params.append(menu_type)
        
        query += ' ORDER BY sort_order, created_at DESC'
        
        cursor.execute(query, params)
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    # ===== ÜRÜN İŞLEMLERİ =====
    def add_product(self, name, description, price, category_id, business_id, menu_type=1, image=''):
        """Ürün ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, description, price, category_id, business_id, menu_type, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, price, category_id, business_id, menu_type, image))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return product_id
    
    def get_products(self, business_id=None, category_id=None, menu_type=None):
        """Ürünleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''SELECT p.*, c.name as category_name 
                  FROM products p 
                  LEFT JOIN categories c ON p.category_id = c.id 
                  WHERE p.is_available = 1'''
        params = []
        
        if business_id:
            query += ' AND p.business_id = ?'
            params.append(business_id)
        
        if category_id:
            query += ' AND p.category_id = ?'
            params.append(category_id)
        
        if menu_type:
            query += ' AND p.menu_type = ?'
            params.append(menu_type)
        
        query += ' ORDER BY p.sort_order, p.created_at DESC'
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        conn.close()
        return products
    
    # ===== YORUM İŞLEMLERİ =====
    def get_comments(self, business_id=None):
        """Yorumları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if business_id:
            cursor.execute('SELECT * FROM comments WHERE business_id = ? ORDER BY created_at DESC', (business_id,))
        else:
            cursor.execute('SELECT * FROM comments ORDER BY created_at DESC')
        comments = cursor.fetchall()
        conn.close()
        return comments
    
    def approve_comment(self, comment_id):
        """Yorumu onayla"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE comments SET is_approved = 1 WHERE id = ?', (comment_id,))
        conn.commit()
        conn.close()
    
    def delete_comment(self, comment_id):
        """Yorum sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.commit()
        conn.close()
    
    # ===== GARSON ÇAĞIRMA İŞLEMLERİ =====
    def get_waiter_calls(self, business_id=None, status='pending'):
        """Garson çağrılarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if business_id:
            cursor.execute('''SELECT * FROM waiter_calls 
                             WHERE business_id = ? AND status = ? 
                             ORDER BY created_at DESC''', (business_id, status))
        else:
            cursor.execute('SELECT * FROM waiter_calls WHERE status = ? ORDER BY created_at DESC', (status,))
        calls = cursor.fetchall()
        conn.close()
        return calls
    
    def resolve_waiter_call(self, call_id):
        """Garson çağrısını çöz"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE waiter_calls 
                         SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP 
                         WHERE id = ?''', (call_id,))
        conn.commit()
        conn.close()
    
    # ===== WIFI AYARLARI =====
    def add_wifi_setting(self, business_id, wifi_name, wifi_password='', is_public=False):
        """WiFi ayarı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wifi_settings (business_id, wifi_name, wifi_password, is_public)
            VALUES (?, ?, ?, ?)
        ''', (business_id, wifi_name, wifi_password, is_public))
        conn.commit()
        wifi_id = cursor.lastrowid
        conn.close()
        return wifi_id
    
    def get_wifi_settings(self, business_id):
        """WiFi ayarlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wifi_settings WHERE business_id = ?', (business_id,))
        wifi_settings = cursor.fetchall()
        conn.close()
        return wifi_settings
    
    # ===== QR KOD İŞLEMLERİ =====
    def save_qr_code(self, business_id, menu_type, qr_url, qr_image_path, table_number=None):
        """QR kod kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO qr_codes (business_id, menu_type, qr_url, qr_image_path, table_number)
            VALUES (?, ?, ?, ?, ?)
        ''', (business_id, menu_type, qr_url, qr_image_path, table_number))
        conn.commit()
        qr_id = cursor.lastrowid
        conn.close()
        return qr_id
    
    def get_qr_codes(self, business_id):
        """QR kodlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM qr_codes WHERE business_id = ? ORDER BY created_at DESC', (business_id,))
        qr_codes = cursor.fetchall()
        conn.close()
        return qr_codes