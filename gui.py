import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import os
import time
from database import DocumentDatabase

class DocumentManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Document Management System")  # Pencere başlığını belirler
        self.geometry("900x400")  # Pencere boyutunu ayarlar
        self.db = DocumentDatabase()  # DocumentDatabase sınıfından bir örnek oluşturur
        self.create_widgets()  # Kullanıcı arayüzü bileşenlerini oluşturur

    def create_widgets(self):
        # Dosya yükleme düğmesini ekler
        self.upload_file_btn = tk.Button(self, text="Upload File", command=self.upload_file)
        self.upload_file_btn.pack(pady=5)
        
        # Klasör yükleme düğmesini ekler
        self.upload_folder_btn = tk.Button(self, text="Upload Folder", command=self.upload_folder)
        self.upload_folder_btn.pack(pady=5)
        
        # Seçilen belgeleri silme düğmesini ekler
        self.delete_btn = tk.Button(self, text="Delete Selected Documents", command=self.delete_documents)
        self.delete_btn.pack(pady=5)
        
        # Seçilen belgeleri kaydetme düğmesini ekler
        self.save_btn = tk.Button(self, text="Save Selected Documents", command=self.save_documents)
        self.save_btn.pack(pady=5)

        # Belge Listesi
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Size", "Created", "Modified"), show="headings", selectmode="extended")
        self.tree.heading("ID", text="ID")  # ID sütununun başlığını belirler
        self.tree.heading("Name", text="Name")  # Name sütununun başlığını belirler
        self.tree.heading("Size", text="Size (MB)")  # Size sütununun başlığını belirler
        self.tree.heading("Created", text="Created At")  # Created sütununun başlığını belirler
        self.tree.heading("Modified", text="Modified At")  # Modified sütununun başlığını belirler
        self.tree.column("Size", width=120, anchor="e")  # Size sütununun genişliğini ve hizalamasını ayarlar
        self.tree.column("Created", width=150)  # Created sütununun genişliğini ayarlar
        self.tree.column("Modified", width=150)  # Modified sütununun genişliğini ayarlar
        self.tree.pack(fill=tk.BOTH, expand=True)  # Treeview bileşenini ekler ve genişlemesine izin verir
        self.load_documents()  # Belgeleri yükler ve Treeview'da görüntüler

    def get_file_dates(self, file_path):
        #Bir dosyanın oluşturulma ve değiştirilme tarihlerini alır ve formatlar.
        stats = os.stat(file_path)
        # Zaman damgalarını formatlar
        created_at = time.ctime(stats.st_birthtime) if hasattr(stats, 'st_birthtime') else 'Unavailable'
        modified_at = time.ctime(stats.st_mtime)
        return created_at, modified_at

    def upload_file(self):
        #Kullanıcıdan bir dosya seçmesini sağlar ve bu dosyayı veritabanına yükler.
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            created_at, modified_at = self.get_file_dates(file_path)
            with open(file_path, 'rb') as file:
                file_content = file.read()
            self.db.add_document(file_name, file_content, created_at, modified_at)
            self.load_documents()  # Belgeleri tekrar yükler
            messagebox.showinfo("Success", f"File '{file_name}' uploaded successfully!")  # Başarı mesajı gösterir

    def upload_folder(self):
        #Kullanıcıdan bir klasör seçmesini sağlar ve bu klasördeki tüm dosyaları veritabanına yükler.
        folder_path = filedialog.askdirectory()
        if folder_path:
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    created_at, modified_at = self.get_file_dates(file_path)
                    with open(file_path, 'rb') as file:
                        file_content = file.read()
                    self.db.add_document(file_name, file_content, created_at, modified_at)
            self.load_documents()  # Belgeleri tekrar yükler
            messagebox.showinfo("Success", f"Folder '{os.path.basename(folder_path)}' uploaded successfully!")  # Başarı mesajı gösterir

    def delete_documents(self):
        #Seçili belgeleri veritabanından siler.
        selected_items = self.tree.selection()
        if selected_items:
            for selected_item in selected_items:
                document_id = self.tree.item(selected_item, "values")[0]
                self.db.delete_document(document_id)
            self.load_documents()  # Belgeleri tekrar yükler
            messagebox.showinfo("Success", "Selected documents deleted successfully!")  # Başarı mesajı gösterir
        else:
            messagebox.showwarning("Warning", "No documents selected.")  # Uyarı mesajı gösterir

    def save_documents(self):
        #Seçili belgeleri belirtilen bir klasöre kaydeder.
        selected_items = self.tree.selection()
        if selected_items:
            save_directory = filedialog.askdirectory()
            if save_directory:
                for selected_item in selected_items:
                    document_id, document_name, _, _ , _ = self.tree.item(selected_item, "values")
                    content = self.db.get_document_content(document_id)
                    
                    # Yeni isim isteme
                    new_name = simpledialog.askstring("Save As", f"Enter new name for {document_name}:", initialvalue=document_name)
                    if new_name:
                        save_path = os.path.join(save_directory, new_name)
                        with open(save_path, 'wb') as file:
                            file.write(content)
                messagebox.showinfo("Success", "Selected documents saved successfully!")  # Başarı mesajı gösterir
            else:
                messagebox.showwarning("Warning", "No save directory selected.")  # Uyarı mesajı gösterir
        else:
            messagebox.showwarning("Warning", "No documents selected.")  # Uyarı mesajı gösterir

    def load_documents(self):
        #Veritabanındaki belgeleri Treeview'da gösterir.
        for row in self.tree.get_children():
            self.tree.delete(row)
        for document in self.db.get_documents():
            document_id, name, size_bytes, created_at, modified_at = document
            size_mb = size_bytes / (1024 * 1024)  # Baytları megabaytlara dönüştürür
            self.tree.insert("", tk.END, values=(document_id, name, f"{size_mb:.2f}", created_at, modified_at))

if __name__ == "__main__":
    app = DocumentManagerApp()
    app.mainloop()
