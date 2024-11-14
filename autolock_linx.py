import os
import subprocess
import json
import requests
from datetime import datetime
import time
import threading
import sys
import logging

API_URL = "https://konimex.com:447/peminjaman_mis/api_notebook/getInventaris"


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
    # Lock the screen on Linux
    os.system("gnome-screensaver-command --lock")  
    # Or use `xdg-screensaver lock`
    
    user_name = os.environ.get("USER")  
    new_password = get_password(3)
    if new_password:
        command = f'echo "{user_name}:{new_password}" | sudo chpasswd'
        subprocess.run(command, shell=True, check=True)

def show_warning():
    # Show warning message in Linux using `zenity`
    os.system("zenity --warning --text='Waktu peminjaman laptop Anda hampir habis. Silakan kembalikan segera untuk menghindari sanksi.'")

def main():
    id_inventaris = 3
    due_date = get_deadline(id_inventaris)
    logging.debug(due_date)
    print(due_date)
    if due_date:
        sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if sekarang > due_date:
            # Run the show_warning function in a separate thread
            warning_thread = threading.Thread(target=show_warning)
            warning_thread.start()

            # Wait for a moment for the warning to show, then proceed to lock the screen
            time.sleep(5)
            set_lock_password()
            
        else:
            print("Masih dalam batas waktu peminjaman.")
    else:
        print("Gagal mendapatkan batas waktu peminjaman.")

main()
