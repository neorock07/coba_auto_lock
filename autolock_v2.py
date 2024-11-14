import os
import subprocess
import json
import requests
from datetime import datetime
import ctypes
import time
import threading
import sys
import logging


API_URL = "https://konimex.com:447/peminjaman_mis/api_notebook/getInventaris"
# API_URL = "https://blbqfx2p-80.asse.devtunnels.ms/MonitorLaptop/api/v1/peminjaman/select"

id_inventaris = 1

# """
#     kode untuk mengakses hak admin (run as administrator)
#     uncomment saat dijalankan di Task Scheduler     
# """
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Jika script belum dijalankan sebagai admin, maka restart dengan hak admin
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# nama user PC
user_name = "HP"

def get_deadline(id_inventaris:int):
    """
        fungsi untuk mendapatkan tanggal pengembalian;
        - parameters:
            id_inventaris (int) : id inventararis yang dimaksud;
        - returns:
            data_return (str) : tanggal pengembalian jika tidak ada maka None;
    """
    try:
        data_return = None
        response = requests.get(API_URL, json={"id_inventaris" : id_inventaris})
        if response.status_code == 200:
            data = response.json()
            print(data)
            if data['tanggal_pengembalian'] != None:
                data_return = data['tanggal_pengembalian']
                #simpan ke json untuk file cadangan
                with open("data_peminjaman.json", "w") as file:
                    json.dump(data, file)
                    
                return data_return
            else:
                return data_return
        return data_return    
            
    except Exception as e:
        print(f"Error: {e}")
        # Kalo offline, baca data dari file lokal
        try:
            with open("data_peminjaman.json", "r") as file:
                local_data = json.load(file)
                return local_data["tanggal_pengembalian"]

        except FileNotFoundError:
            print("Data peminjaman lokal tidak ditemukan.")
            return None

def get_password(id_inventaris:int):
    """
        fungsi untuk mendapatkan password baru untuk lock-screen;
        - parameters:
            id_inventaris (int) : id inventararis yang dimaksud;
        - returns:
            data_return (str) : password baru jika tidak ada maka None;
    """
    try:
        data_pass_pinjam = None
        data_pass_kembali = None
        response = requests.get(API_URL, json={"id_inventaris" : id_inventaris})
        if response.status_code == 200:
            data = response.json()
            print(data)
            if data['password_peminjaman'] != None:
                data_pass_pinjam = data['password_peminjaman']
                data_pass_kembali = data['password_pengembalian']
                #simpan ke json untuk file cadangan
                with open("data_peminjaman.json", "w") as file:
                    json.dump(data, file)
                    
                return data_pass_pinjam, data_pass_kembali
            else:
                return data_pass_pinjam, data_pass_kembali
        return data_pass_pinjam, data_pass_kembali    
            
    except Exception as e:
        print(f"Error: {e}")
        # Kalo offline, baca data dari file lokal
        try:
            with open("data_peminjaman.json", "r") as file:
                local_data = json.load(file)
                return local_data["password_peminjaman"], local_data["password_pengembalian"]
        except FileNotFoundError:
            print("Data peminjaman lokal tidak ditemukan.")
            return None


   
def set_lock_password():
    """
        kode untuk menjalankan proses lock-screen dan mengubah password
    """ 
    os.system("rundll32.exe user32.dll,LockWorkStation")
    #ganti nama user sesuai PC
    #pakai command: >>net user
    
    new_password, password_kembali = get_password(id_inventaris)
    command = f'net user "{user_name}" "{password_kembali}"'
    subprocess.run(["powershell", "-Command", command], check=True)

def set_password_init():
    new_password, password_kembali = get_password(id_inventaris)
    command = f'net user "{user_name}" "{new_password}"'
    subprocess.run(["powershell", "-Command", command], check=True)

# """
#     kode untuk memunculkan pop-up dialog warning message
# """
def show_warning():
    """Menampilkan MessageBox sebagai peringatan di thread terpisah"""
    ctypes.windll.user32.MessageBoxW(0, "Waktu peminjaman laptop Anda hampir habis. Silakan kembalikan segera untuk menghindari sanksi.", "Peringatan Peminjaman", 1)

# """
#     kode untuk menintegrasikan semua komponen
# """
def main():
    """
        fungsi utama untuk menjalakan program ini.
    """
    
    
    due_date = get_deadline(id_inventaris)
    logging.debug(due_date)
    print(due_date)
    if due_date:
        sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if sekarang > due_date:
            # Menjalankan fungsi show_warning di thread terpisah
            warning_thread = threading.Thread(target=show_warning)
            warning_thread.start()

            # Tunggu sebentar biar warning muncul, lalu langsung lanjut ke instruksi lock screen
            time.sleep(5)
            set_lock_password()
            
        else:
            print("Masih dalam batas waktu peminjaman.")
            set_password_init()
    else:
        print("Gagal mendapatkan batas waktu peminjaman.")

main()        
    
    

