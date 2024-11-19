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


# """
#     kode untuk mengakses hak admin (run as administrator)
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
        
        :param id_inventaris (int): id inventararis yang dimaksud;
        :returns data_return (str): password baru jika tidak ada maka None;
    """
    try:
        data_return = None
        response = requests.get(API_URL, json={"id_inventaris" : id_inventaris})
        if response.status_code == 200:
            data = response.json()
            print(data)
            if data['password_inventaris'] != None:
                data_return = data['password_inventaris']
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
                return local_data["password_inventaris"]
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
    user_name = "HP"
    new_password = get_password(3)
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
    
    id_inventaris = 1
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
    else:
        print("Gagal mendapatkan batas waktu peminjaman.")

main()        
    
    


