import sqlite3

class DocumentDatabase:
    def __init__(self, db_name="documents.db"):
        #Veritabanı bağlantısını oluşturur ve tabloyu oluşturur.
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        #Belgeler için gerekli tabloyu oluşturur.
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS documents (
                                    id INTEGER PRIMARY KEY,  # Belge ID'si (otomatik artan)
                                    name TEXT NOT NULL,  # Belge adı
                                    content BLOB NOT NULL,  # Belge içeriği (ikili veri)
                                    size INTEGER NOT NULL,  # Belge boyutu (bayt cinsinden)
                                    created_at TEXT NOT NULL,  # Oluşturulma tarihi
                                    modified_at TEXT NOT NULL  # Değiştirilme tarihi
                                )''')

    def add_document(self, name, content, created_at, modified_at):
        #Yeni bir belge ekler.
        size = len(content)  # Belge boyutunu bayt cinsinden alır
        with self.conn:
            self.conn.execute(
                "INSERT INTO documents (name, content, size, created_at, modified_at) VALUES (?, ?, ?, ?, ?)",
                (name, content, size, created_at, modified_at)
            )

    def get_documents(self):
        #Tüm belgeleri getirir (ID, ad, boyut, oluşturulma tarihi, değiştirilme tarihi).
        with self.conn:
            return self.conn.execute("SELECT id, name, size, created_at, modified_at FROM documents").fetchall()

    def get_document_content(self, document_id):
        #Belirli bir belgenin içeriğini getirir.
        with self.conn:
            return self.conn.execute("SELECT content FROM documents WHERE id = ?", (document_id,)).fetchone()[0]
    
    def delete_document(self, document_id):
        #Belirli bir belgeyi veritabanından siler.
        with self.conn:
            self.conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
