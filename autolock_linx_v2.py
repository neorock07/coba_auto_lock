"""
    ##################################################################################
    #                          HARAP BACA NOTE INI DAHULU                            #
    #                     PROGRAM AUTOLOCK FOR LINUX VERSION ONLY                    #
    ##################################################################################
    TERDAPAT BEBERAPA CATATAN UNTUK MENJALANKAN PROGRAM INI DENGAN BENAR :

    a) PADA KODE UNTUK MENGGANTI PASSWORD DIPERLUKAN ISIAN NAMA USER PC, INI HANYA DAPAT DILAKUKAN
       SECARA MANUAL KARENA SAAT DIJALANKAN DI CRONTAB KODE UNTUK MENDAPATKAN VARIABEL USER TIDAK DAPAT DIPAKAI.
       UNTUK ITU JALANKAN PERINTAH INI UNTUK MENGETAHUI NAMA USER :
       >> whoami
       LALU SALIN OUTPUT COMMAND ITU KE KODE PADA FUNGSI `set_lock_password`,
       PADA `command = f'echo "isi di sini:[password_baru_dari_server]" | sudo chpasswd'`

    b) MEMASTIKAN PROGRAM XSCREENSAVER BERJALAN KETIKA STARTUP, UNTUK MENAMBAHKAN PENGATURAN INI JALANKAN PADA USER `BUKAN` ROOT.
        >>nano ~/.profile
       LALU TAMBAHKAN KODE : `xscreensaver &`
       CONTOH FILE TERSEBUT :
       --------------------------------------------------------------------------------------
       # All other interactive shells will only read .bashrc; this is particularly
       # important for language settings, see below.

       test -z "$PROFILEREAD" && . /etc/profile || true
       xscreensaver &     <-- tambahkan di sini.

       # Most applications support several languages for their output.
       # To make use of this feature, simply uncomment one of the lines below or
       --------------------------------------------------------------------------------------

       `JANGAN` MEMBUAT FILE .xinitrc ATAU .xsession MISAL DENGAN MENJALANKAN COMMAND : >>nano ~/.xinitrc ATAU >>~/.xsession
       HAL INI DILARANG KARENA AKAN MENGGANGGU SISTEM SAAT STARTUP SEHINGGA AKAN ADA KEMUNGKINAN AKAN GAGAL LOGIN.
       APABILA TERLANJUR MEMBUAT FILE TERSEBUT DAN MENGAKIBATKAN KEGAGALAN LOGIN, MAKA MASUK KE TTY DENGAN MENEKAN
       TOMBOL CTRL+ALT+F2, KEMUDIAN MASUK DENGAN USER BUKAN ROOT. KEMUDIAN HAPUS FILE TERSEBUT, LALU REBOOT DENGAN
       COMMAND >>sudo reboot.

       PROGRAM XSCREENSAVER MEMERLUKAN LOKASI VARIABEL $XAUTHORITY AGAR DAPAT MENGAKSES DISPLAY, LOKASI VARIABEL TERSEBUT PADA
       /run/user/1000/xauth_* , FILE xauth_* INI MEMILIKI NAMA YANG SELALU BERUBAH SETELAH PC BOOTING KARENA MEMULAI PROGRAM X11
       MEMULAI SESSION BARU, MAKA DARI ITU PADA PROGRAM INI SUDAH DITERAPKAN PENCARIAN VARIABEL XAUTHORITY SECARA OTOMATIS PADA
       FUNGSI `set_crontab_variable()`.

    c) PADA CRONTAB ISIKAN SEPERTI CONTOH SESUAI LOKASI FILE PYTHON DAN PROGRAM AUTOLOCK INI.

       */10 * * * * /usr/bin/python3.9 /home/user/Downloads/autolock_linx_v2.py >> /home/user/Downloads/logfile_program.log 2>&1

       PADA CONTOH TERSEBUT CRONTAB AKAN MENAJALANKAN PROGRAM SETIAP 10 MENIT.

    d) SETIAP KALI PROGRAM DIJALANKAN AKAN MEMBUAT FILE `data_peminjaman.json` YANG BERISI JSON TANGGAL PENGEMBALIAN DAN PASSWORD BARU,
       INI DIGUNAKAN SEBAGAI CADANGAN KETIKA PC TIDAK TERKONEKSI INTERNET, FILE INI AKAN TERSIMPAN SE-FOLDER DENGAN PROGRAM INI DILETAKKAN,
       MAKA DARI ITU **JANGAN MENGUBAH LOKASI FILE INI**.

    e) PROGRAM INI HANYA DAPAT BERJALAN NORMAL PADA VERSI PYTHON >= 3.9 (pengujian telah berhasil pada versi tersebut, dan gagal pada versi di bawah-nya)

    f) AGAR SAAT CRONTAB MENGEKSEKUSI PROGRAM PYHTON INI TIDAK MUNCUL KONFIRMASI SUDO, MAKA TAMBAHKAN PERMISSION PADA SUDOERS AGAR
       DAPAT DIJALANKAN TANPA HARUS KONFIRMASI SUDO.
       >>sudo visudo
       LALU TAMBAHKAN :
       user ALL=NOPASSWD:/usr/bin/python3.9


"""



import os
import subprocess
import json
import requests
from datetime import datetime
import time
import threading
import sys
import logging




# alamat API
API_URL = "https://konimex.com:447/peminjaman_mis/api_notebook/getInventaris"

# variabel untuk id inventaris/laptop diambil dari databse
nomor_inventaris = 1


def get_deadline(nomor_inventaris:int):
    """
        fungsi untuk mendapatkan tanggal pengembalian;
        - parameters:
            nomor_inventaris (int) : id inventararis yang dimaksud;
        - returns:
            data_return (str) : tanggal pengembalian jika tidak ada maka None;
    """
    try:
        data_return = None
        response = requests.get(API_URL, json={"nomor_inventaris" : nomor_inventaris})
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

def get_password(nomor_inventaris:int):
    """
        fungsi untuk mendapatkan password baru untuk lock-screen;
        
        :param nomor_inventaris (int): id inventararis yang dimaksud; 
        :return passwd_pinjam (str): password baru jika tidak ada maka None;
        :return passwd_kembali (str): password untuk pengembalian / reset
    """
    try:
        passwd_pinjam = None
        passwd_kembali = None
        response = requests.get(API_URL, json={"nomor_inventaris" : nomor_inventaris})
        if response.status_code == 200:
            data = response.json()
            print(data)
            if data['password_peminjaman'] != None:
                passwd_pinjam = data['password_peminjaman']
                passwd_kembali = data['password_pengembalian']
                #simpan ke json untuk file cadangan
                with open("data_peminjaman.json", "w") as file:
                    json.dump(data, file)
                    
                return passwd_pinjam, passwd_kembali
            else:
                return passwd_pinjam, passwd_kembali
        return passwd_pinjam, passwd_kembali
            
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



def set_crontab_variable():
    """
        kode untuk set variabel pengaturan untuk xscreensaver pada Crontab
        untuk memberikan permission pada crontab untuk dapat mengakses display.
    """
    
    #mengatur agar menggunakan display ke-0
    os.environ["DISPLAY"] = ":0"
    #mencari key session untuk authority xscreensaver dengan pola (xauth_...)
    cm_find = "find /run/user/1000/ -type f -name 'xauth_*' 2>/dev/null | head -n 1"
    try:
        path_xauth = subprocess.check_output(
                cm_find,
                shell=True,
                text=True
            ).strip()
        if path_xauth:
            os.environ["XAUTHORITY"] = path_xauth
            print(f"PATH XAUTHORITY : {path_xauth}")
        else:
            print("XAUTHORITY NOT FOUND")
    except subprocess.CalledProcessError as e:
        print("Error when find XAUTHORITY")


def run_xscreensaver():
    """
        kode untuk mengaktifkan server xscreensaver, apabila xscreensaver off maka tidak bisa lock screen, jika sudah aktif
        hanya akan ada pesan warning `xsreensaver already running on display :0`
    """
    os.system("xscreensaver &")

def set_password_init():
    """
        Fungsi untuk set password saat masa peminjaman berlaku.
    """
    new_password, pass_kembali = get_password(nomor_inventaris)
    user_pc = "user"
    if new_password:
        print(f"password init : {new_password}")
        # kode ini berdasarkan command echo "nama user di PC:password baru" | sudo chpasswd
        command = f'echo "{user_pc}:{new_password}" | sudo chpasswd'
        subprocess.run(command, shell=True, check=True)


def set_lock_password():
    """
    Fungsi untuk menjalankan lock-screen dan mengganti password;
    """
    # jika OS pakai Gnome uncomment kode di bawah.
    # os.system("gnome-screensaver-command --lock")

    # jika OS pakai xscreensaver uncomment kode di bawah.
    os.system("xscreensaver-command -lock")

    # jika OS pakai xdg uncomment kode di bawah.
    # os.system("xdg-screensaver lock")

    
    # kode user_name ini hanya akan berjalan ketika dieksekusi di terminal secara manual,
    # jika dijalankan pada Crontab akan mengambil user secara keseluruhan atau root;
    # maka dari itu nilai variabel `user_name` TIDAK DIPAKAI pada Crontab.
    # user_name = os.environ.get("USER")
    # print(user_name)
    
    user_pc = "user"
    #mendaptkan password baru dari server
    new_pass, password_kembali = get_password(nomor_inventaris)
    if password_kembali:
        # kode ini berdasarkan command echo "nama user di PC:password baru" | sudo chpasswd
        command = f'echo "{user_pc}:{password_kembali}" | sudo chpasswd'
        subprocess.run(command, shell=True, check=True)
        print(f"ini yaa : {password_kembali}")


def show_warning():
    """
        Menampilkan dialog pop-up warning.
    """
    os.system("zenity --warning --text='Waktu peminjaman laptop Anda hampir habis. Silakan kembalikan segera untuk menghindari sanksi.'")

def main():
    """
        Fungsi utama yang meng-integrasikan setiap elemen kode untuk menjalankan program sebagai satu kesatuan.
    """
    set_crontab_variable()

    # Kode untuk menjalankan server xscreen dan berjalan pada thread lain, agar dapat paralel.
    # Kode untuk mengunci screen dan berjalan pada thread lain, agar dapat paralel.
    # screen_saver_thread = threading.Thread(target=run_xscreensaver)
    # screen_saver_thread.start()

    # mendapatkan data tanggal pengembalian dari server.
    due_date = get_deadline(nomor_inventaris)
    logging.debug(due_date)
    print(due_date)

    if due_date:
        # mendapatkan data waktu sekarang
        sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # periksa apakah tanggal sekarang lebih dari tanggal pengembalian,
        # jika ya maka itu terlambat dan mengeksekusi lokc screen and change password
        if sekarang > due_date:
            # Menampilkan dialog warning yang berjalan pada thread berbeda agar kode ini dapat berjalan paralel
            # dengan kode di bawah-nya.
            warning_thread = threading.Thread(target=show_warning)
            warning_thread.start()


            # Tunggu lima second sebelum mengeksekusi change password user (bukan root/sudo)
            time.sleep(5)
            set_lock_password()
            
        else:
            print("Masih dalam batas waktu peminjaman.")
            # Set password untuk masa peminjaman berlaku
            set_password_init()
    else:
        print("Gagal mendapatkan batas waktu peminjaman.")

# Menjalankan xscreensaver server untuk jaga-jaga apabila di startup tidak running.
screen_saver_thread = threading.Thread(target=run_xscreensaver)
screen_saver_thread.start()
#jalankan kode main
main()
