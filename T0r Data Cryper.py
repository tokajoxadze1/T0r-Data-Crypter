import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import sys
import logging
import threading
import time
import secrets
import hashlib
from datetime import datetime
import json

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class FixedDataCrypter:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("T0R - DATA CRYPTER v2.2 - FIXED")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # ცვლადები
        self.current_operation = None
        self.stop_requested = False
        self.encryption_methods = {
            "AES-256-GCM": "AES-256-GCM",
            "ChaCha20": "ChaCha20", 
            "AES-256-CBC": "AES-256-CBC"
        }
        self.password_visible = False
        
        self.setup_advanced_logging()
        self.create_enhanced_gui()
        
    def setup_advanced_logging(self):
        self.logger = logging.getLogger('T0RCrypter')
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler('t0r_fixed.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def create_enhanced_gui(self):
        self.main_container = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_header()
        self.create_content()
        self.create_status_bar()
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_container, height=80, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="T0R DATA CRYPTER - FIXED VERSION",
            font=ctk.CTkFont("Courier New", size=24, weight="bold"),
            text_color="#00ff88"
        )
        title_label.pack(pady=5)
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="გაშიფვრის პრობლემა მოგვარებულია!",
            font=ctk.CTkFont("Arial", size=12),
            text_color="#00ccff"
        )
        subtitle_label.pack()
        
        self.system_status = ctk.CTkLabel(
            header_frame,
            text="🔓 სისტემა მზადაა",
            font=ctk.CTkFont("Arial", size=10, weight="bold"),
            text_color="#00ff00"
        )
        self.system_status.place(relx=0.95, rely=0.5, anchor="e")
        
    def create_content(self):
        content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # მარცხენა პანელი
        left_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # დისკის არჩევა
        disk_section = ctk.CTkFrame(left_frame, corner_radius=8)
        disk_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            disk_section,
            text="💾 დისკის მართვა",
            font=ctk.CTkFont("Arial", size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        disk_path_frame = ctk.CTkFrame(disk_section, fg_color="transparent")
        disk_path_frame.pack(fill="x", padx=10, pady=5)
        
        self.disk_path = ctk.CTkEntry(
            disk_path_frame,
            placeholder_text="აირჩიეთ დისკი ან დირექტორია...",
            height=35
        )
        self.disk_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            disk_path_frame,
            text="📁 არჩევა",
            width=80,
            command=self.browse_disk
        ).pack(side="right")
        
        self.disk_info = ctk.CTkLabel(
            disk_section,
            text="დისკი არ არის არჩეული",
            font=ctk.CTkFont("Arial", size=10),
            text_color="#888888"
        )
        self.disk_info.pack(anchor="w", padx=10, pady=(0, 10))
        
        # დაშიფვრის პარამეტრები
        crypto_section = ctk.CTkFrame(left_frame, corner_radius=8)
        crypto_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            crypto_section,
            text="🔐 დაშიფვრის პარამეტრები",
            font=ctk.CTkFont("Arial", size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        algo_frame = ctk.CTkFrame(crypto_section, fg_color="transparent")
        algo_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(algo_frame, text="ალგორითმი:").pack(side="left")
        
        self.algo_var = ctk.StringVar(value="AES-256-GCM")
        algo_combo = ctk.CTkComboBox(
            algo_frame,
            values=list(self.encryption_methods.keys()),
            variable=self.algo_var,
            width=150
        )
        algo_combo.pack(side="right")
        
        # პაროლის ველი თვალის ღილაკით
        password_frame = ctk.CTkFrame(crypto_section, fg_color="transparent")
        password_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(password_frame, text="მასტერ-პაროლი:").pack(anchor="w")
        
        password_input_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        password_input_frame.pack(fill="x", pady=5)
        
        self.password_entry = ctk.CTkEntry(
            password_input_frame,
            placeholder_text="შეიყვანეთ მასტერ-პაროლი...",
            show="•",
            height=35
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        self.eye_button = ctk.CTkButton(
            password_input_frame,
            text="👁️",
            width=50,
            height=35,
            command=self.toggle_password_visibility,
            fg_color="#2b2b2b",
            hover_color="#3b3b3b"
        )
        self.eye_button.pack(side="right", padx=(5, 0))
        
        # პაროლის სიძლიერე
        self.password_strength = ctk.CTkProgressBar(password_frame, height=4)
        self.password_strength.pack(fill="x")
        self.password_strength.set(0)
        
        self.strength_label = ctk.CTkLabel(
            password_frame,
            text="პაროლი არ არის შეყვანილი",
            font=ctk.CTkFont("Arial", size=10),
            text_color="#888888"
        )
        self.strength_label.pack(anchor="e")
        
        # გაფრთხილება
        warning_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        warning_frame.pack(fill="x", pady=(5, 0))
        
        warning_text = "⚠️ გაფრთხილება: შეიყვანეთ პაროლი სწორად და დაიმახსოვრეთ იგი! პაროლის დაკარგვის შემთხვევაში მონაცემების აღდგენა შეუძლებელი იქნება!"
        
        self.warning_label = ctk.CTkLabel(
            warning_frame,
            text=warning_text,
            font=ctk.CTkFont("Arial", size=10, weight="bold"),
            text_color="#ff9900",
            wraplength=500,
            justify="left"
        )
        self.warning_label.pack(anchor="w", fill="x")
        
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)
        
        # ოპერაციების ღილაკები
        ops_section = ctk.CTkFrame(left_frame, corner_radius=8)
        ops_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            ops_section,
            text="⚡ ოპერაციები",
            font=ctk.CTkFont("Arial", size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        button_frame = ctk.CTkFrame(ops_section, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.encrypt_btn = ctk.CTkButton(
            button_frame,
            text="🔒 დაშიფვრა",
            command=self.start_encryption,
            fg_color="#00aa44",
            hover_color="#008833",
            height=40,
            font=ctk.CTkFont("Arial", size=12, weight="bold")
        )
        self.encrypt_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.decrypt_btn = ctk.CTkButton(
            button_frame,
            text="🔓 გაშიფვრა",
            command=self.start_decryption,
            fg_color="#cc5500",
            hover_color="#aa4400",
            height=40,
            font=ctk.CTkFont("Arial", size=12, weight="bold")
        )
        self.decrypt_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹️ გაჩერება",
            command=self.stop_operation,
            fg_color="#666666",
            hover_color="#555555",
            height=40,
            state="disabled"
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # პროგრესის ზოლი
        progress_section = ctk.CTkFrame(left_frame, corner_radius=8)
        progress_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            progress_section,
            text="📊 პროგრესი",
            font=ctk.CTkFont("Arial", size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_section, height=12, corner_radius=6)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        stats_frame = ctk.CTkFrame(progress_section, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_label = ctk.CTkLabel(
            stats_frame,
            text="მოლოდინის რეჟიმი...",
            font=ctk.CTkFont("Arial", size=10)
        )
        self.progress_label.pack(side="left")
        
        self.speed_label = ctk.CTkLabel(
            stats_frame,
            text="სიჩქარე: 0 MB/s",
            font=ctk.CTkFont("Arial", size=10)
        )
        self.speed_label.pack(side="right")
        
        # მარჯვენა პანელი - ლოგი
        right_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(
            right_frame,
            text="📝 სისტემის ლოგი",
            font=ctk.CTkFont("Arial", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.log_text = ctk.CTkTextbox(
            right_frame,
            font=ctk.CTkFont("Consolas", size=11),
            fg_color="#000000",
            text_color="#00ff88",
            corner_radius=8
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        log_controls = ctk.CTkFrame(right_frame, fg_color="transparent")
        log_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            log_controls,
            text="🧹 ლოგის გასუფთავება",
            width=120,
            command=self.clear_log
        ).pack(side="left")
        
        ctk.CTkButton(
            log_controls,
            text="💾 ლოგის შენახვა",
            width=120,
            command=self.save_log
        ).pack(side="right")
        
    def create_status_bar(self):
        status_frame = ctk.CTkFrame(self.main_container, height=30, corner_radius=8)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="სისტემა მზადაა მუშაობისთვის - გაშიფვრა მოგვარებულია!",
            font=ctk.CTkFont("Arial", size=10)
        )
        self.status_label.pack(side="left", padx=15)
        
        self.stats_label = ctk.CTkLabel(
            status_frame,
            text="დაშიფრული ფაილები: 0 | გაშიფრული ფაილები: 0",
            font=ctk.CTkFont("Arial", size=10)
        )
        self.stats_label.pack(side="right", padx=15)
    
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        
        if self.password_visible:
            self.password_entry.configure(show="")
            self.eye_button.configure(text="🔒", fg_color="#1f6aa5", hover_color="#144870")
            self.log_message("პაროლი ხილვადია", "INFO")
        else:
            self.password_entry.configure(show="•")
            self.eye_button.configure(text="👁️", fg_color="#2b2b2b", hover_color="#3b3b3b")
            self.log_message("პაროლი დამალულია", "INFO")
    
    def browse_disk(self):
        path = filedialog.askdirectory()
        if path:
            self.disk_path.delete(0, tk.END)
            self.disk_path.insert(0, path)
            self.update_disk_info(path)
            
    def update_disk_info(self, path):
        try:
            total_size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                        file_count += 1
                    except:
                        continue
            
            size_mb = total_size / (1024 * 1024)
            self.disk_info.configure(
                text=f"ფაილები: {file_count} | ზომა: {size_mb:.1f} MB"
            )
        except Exception as e:
            self.disk_info.configure(text="შეცდომა დისკის ანალიზისას")
            
    def check_password_strength(self, event=None):
        password = self.password_entry.get()
        if not password:
            self.password_strength.set(0)
            self.strength_label.configure(text="პაროლი არ არის შეყვანილი")
            return
            
        strength = 0
        if len(password) >= 8: strength += 0.2
        if len(password) >= 12: strength += 0.2
        if any(c.islower() for c in password): strength += 0.2
        if any(c.isupper() for c in password): strength += 0.2
        if any(c.isdigit() for c in password): strength += 0.1
        if any(not c.isalnum() for c in password): strength += 0.1
        
        self.password_strength.set(strength)
        
        if strength < 0.4:
            color = "#ff4444"
            text = "სუსტი"
        elif strength < 0.7:
            color = "#ffaa00"
            text = "საშუალო"
        else:
            color = "#00ff44"
            text = "ძლიერი"
            
        self.strength_label.configure(text=text, text_color=color)
        
    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.insert("end", formatted_message + "\n")
        self.log_text.see("end")
        
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
            
    def clear_log(self):
        self.log_text.delete("1.0", "end")
        
    def save_log(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get("1.0", "end"))
                self.log_message("ლოგი შენახულია", "INFO")
            except Exception as e:
                self.log_message(f"ლოგის შენახვის შეცდომა: {str(e)}", "ERROR")
                
    def start_encryption(self):
        if not self.validate_inputs():
            return
            
        self.current_operation = "encrypt"
        self.stop_requested = False
        self.toggle_buttons(False)
        self.system_status.configure(text="🔒 დაშიფვრა მიმდინარეობს...", text_color="#ffaa00")
        
        threading.Thread(target=self.process_operation, daemon=True).start()
        
    def start_decryption(self):
        if not self.validate_inputs():
            return
            
        self.current_operation = "decrypt"
        self.stop_requested = False
        self.toggle_buttons(False)
        self.system_status.configure(text="🔓 გაშიფვრა მიმდინარეობს...", text_color="#ffaa00")
        
        threading.Thread(target=self.process_operation, daemon=True).start()
        
    def stop_operation(self):
        self.stop_requested = True
        self.log_message("ოპერაცია გაჩერებულია მომხმარებლის მოთხოვნით", "WARNING")
        
    def toggle_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        self.encrypt_btn.configure(state=state)
        self.decrypt_btn.configure(state=state)
        self.stop_btn.configure(state="normal" if not enabled else "disabled")
        
    def validate_inputs(self):
        path = self.disk_path.get()
        password = self.password_entry.get()
        
        if not path or not os.path.exists(path):
            messagebox.showerror("შეცდომა", "გთხოვთ აირჩიოთ არსებული დისკი/დირექტორია")
            return False
            
        if not password:
            messagebox.showerror("შეცდომა", "გთხოვთ შეიყვანოთ მასტერ-პაროლი")
            return False
            
        if len(password) < 8:
            messagebox.showerror("შეცდომა", "პაროლი უნდა იყოს მინიმუმ 8 სიმბოლო")
            return False
            
        if not messagebox.askyesno(
            "გაფრთხილება", 
            "⚠️ დარწმუნებული ხართ რომ დაიმახსოვრეთ პაროლი?\n\n" +
            "პაროლის დაკარგვის შემთხვევაში მონაცემების აღდგენა შეუძლებელი იქნება!\n\n" +
            "გავაგრძელოთ ოპერაცია?"
        ):
            return False
            
        return True
        
    def process_operation(self):
        try:
            path = self.disk_path.get()
            password = self.password_entry.get()
            algorithm = self.algo_var.get()
            
            self.log_message(f"დაწყებულია {self.current_operation} ოპერაცია...", "INFO")
            self.log_message(f"გზა: {path}", "INFO")
            self.log_message(f"ალგორითმი: {algorithm}", "INFO")
            
            files = self.collect_files(path)
            total_files = len(files)
            processed = 0
            success_count = 0
            
            start_time = time.time()
            
            for file_path in files:
                if self.stop_requested:
                    break
                    
                try:
                    if self.current_operation == "encrypt":
                        success = self.encrypt_file_fixed(file_path, password, algorithm)
                    else:
                        success = self.decrypt_file_fixed(file_path, password, algorithm)
                        
                    if success:
                        success_count += 1
                        status = "დაშიფრული" if self.current_operation == "encrypt" else "გაშიფრული"
                        self.log_message(f"{status}: {os.path.basename(file_path)}")
                    else:
                        self.log_message(f"შეცდომა: {os.path.basename(file_path)}", "ERROR")
                        
                except Exception as e:
                    self.log_message(f"კრიტიკული შეცდომა {file_path}: {str(e)}", "ERROR")
                    
                processed += 1
                progress = processed / total_files if total_files > 0 else 0
                
                self.update_progress(progress, processed, total_files, start_time)
                
            operation_name = "დაშიფვრა" if self.current_operation == "encrypt" else "გაშიფვრა"
            self.log_message(f"{operation_name} დასრულდა! წარმატებით: {success_count}/{total_files}", "INFO")
            
            self.system_status.configure(text="✅ ოპერაცია დასრულდა", text_color="#00ff00")
            
        except Exception as e:
            self.log_message(f"კრიტიკული შეცდომა: {str(e)}", "ERROR")
            self.system_status.configure(text="❌ ოპერაცია ჩავარდა", text_color="#ff4444")
            
        finally:
            self.toggle_buttons(True)
            self.progress_bar.set(0)
            
    def collect_files(self, path):
        files = []
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    # გამოვტოვოთ უკვე დაშიფრული ფაილები ფიქსირებული გაშიფვრისთვის
                    if not filename.endswith('.encrypted'):
                        files.append(os.path.join(dirpath, filename))
        except Exception as e:
            self.log_message(f"შეცდომა ფაილების კოლექციისას: {str(e)}", "ERROR")
        return files
        
    def update_progress(self, progress, processed, total, start_time):
        self.root.after(0, lambda: self._update_progress_gui(progress, processed, total, start_time))
        
    def _update_progress_gui(self, progress, processed, total, start_time):
        self.progress_bar.set(progress)
        
        elapsed = time.time() - start_time
        speed = processed / elapsed if elapsed > 0 else 0
        
        self.progress_label.configure(
            text=f"დამუშავებული: {processed}/{total} ({progress*100:.1f}%)"
        )
        self.speed_label.configure(text=f"სიჩქარე: {speed:.1f} ფაილი/წმ")
    
    # 🔧 გამოსწორებული დაშიფვრის ფუნქცია
    def encrypt_file_fixed(self, file_path, password, algorithm):
        try:
            with open(file_path, 'rb') as f:
                original_data = f.read()
            
            # გასაღების გენერაცია
            salt = os.urandom(32)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA512(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            
            encrypted_data = b""
            tag = b""
            
            if algorithm == "AES-256-GCM":
                # AES-GCM დაშიფვრა
                iv = os.urandom(12)  # 96 bits for GCM
                cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
                encryptor = cipher.encryptor()
                encrypted_data = encryptor.update(original_data) + encryptor.finalize()
                tag = encryptor.tag
                
            elif algorithm == "AES-256-CBC":
                # AES-CBC დაშიფვრა
                iv = os.urandom(16)
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                encryptor = cipher.encryptor()
                
                # Padding
                padder = padding.PKCS7(128).padder()
                padded_data = padder.update(original_data) + padder.finalize()
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                tag = b""  # No tag for CBC
                
            elif algorithm == "ChaCha20":
                # ChaCha20 დაშიფვრა
                iv = os.urandom(16)
                cipher = Cipher(algorithms.ChaCha20(key, iv), mode=None, backend=default_backend())
                encryptor = cipher.encryptor()
                encrypted_data = encryptor.update(original_data)
                tag = b""  # No tag for ChaCha20
            
            # შენახვა ახალ ფაილში
            encrypted_file_path = file_path + '.encrypted'
            
            with open(encrypted_file_path, 'wb') as f:
                # ჰედერის ჩაწერა: salt + iv + tag + encrypted_data
                f.write(salt)
                f.write(iv)
                if tag:
                    f.write(tag)
                f.write(encrypted_data)
            
            # ორიგინალის წაშლა და დაშიფრულის გადარქმევა
            os.remove(file_path)
            os.rename(encrypted_file_path, file_path)
            
            return True
            
        except Exception as e:
            self.log_message(f"დაშიფვრის შეცდომა {file_path}: {str(e)}", "ERROR")
            return False
    
    # 🔧 გამოსწორებული გაშიფვრის ფუნქცია
    def decrypt_file_fixed(self, file_path, password, algorithm):
        try:
            with open(file_path, 'rb') as f:
                # ჰედერის წაკითხვა
                salt = f.read(32)
                
                if algorithm == "AES-256-GCM":
                    iv = f.read(12)
                    tag = f.read(16)
                    encrypted_data = f.read()
                else:
                    iv = f.read(16)
                    tag = b""
                    encrypted_data = f.read()
            
            # გასაღების რეკონსტრუქცია
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA512(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            
            decrypted_data = b""
            
            if algorithm == "AES-256-GCM":
                # AES-GCM გაშიფვრა
                cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
                
            elif algorithm == "AES-256-CBC":
                # AES-CBC გაშიფვრა
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
                
                # Unpadding
                unpadder = padding.PKCS7(128).unpadder()
                decrypted_data = unpadder.update(padded_data) + unpadder.finalize()
                
            elif algorithm == "ChaCha20":
                # ChaCha20 გაშიფვრა
                cipher = Cipher(algorithms.ChaCha20(key, iv), mode=None, backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_data = decryptor.update(encrypted_data)
            
            # შენახვა დროებით ფაილში
            decrypted_file_path = file_path + '.decrypted'
            
            with open(decrypted_file_path, 'wb') as f:
                f.write(decrypted_data)
            
            # დაშიფრულის წაშლა და გაშიფრულის გადარქმევა
            os.remove(file_path)
            os.rename(decrypted_file_path, file_path)
            
            return True
            
        except Exception as e:
            self.log_message(f"გაშიფვრის შეცდომა {file_path}: {str(e)}", "ERROR")
            return False
            
    def run(self):
        self.log_message("T0R DATA CRYPTER v2.2 - FIXED გაეშვა", "INFO")
        self.log_message("გაშიფვრის პრობლემა მოგვარებულია!", "INFO")
        self.log_message("სისტემა მზადაა მუშაობისთვის", "INFO")
        self.root.mainloop()

if __name__ == "__main__":
    app = FixedDataCrypter()
    app.run()