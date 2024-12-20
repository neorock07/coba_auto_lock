# FILE autolock_v2.py IS FOR WINDOWS VERSION ONLY. 
# CARA SETTING TASK SCHEDULER UNTUK MENJALANKAN PROGRAM INI.

1. BUKA TASK-SCHEDULER PADA PC, KLIK CREATE TASK PADA PANEL 
SEBELAH KANAN

2. PADA KOTAK DIALOG, DI TAB GENERAL BAGIAN BAWAH ATUR CONFIGURE
FOR KE WINDOWS YANG SESUAI VERSI PC. ATUR JUGA NAME DAN DESCRIPTION 
AGAR MEMUDAHKAN MEMBEDAKAN DENGAN SERVICE YANG LAIN.

3. PINDAH KE TAB TRIGGER, ATUR BEGIN THE TASK KE `AT START-UP`,
PADA BAGIAN ADVANCED SETTINGS, CENTANG `REPEAT TASK EVERY` KEMUDIAN
SESUAIKAN. ATUR FOR A DURATION OF KE `INDEFINITELY`.

4. PINDAH KE TAB ACTION, ATUR ACTION KE `START A PROGRAM`, KEMUDIAN 
PADA BAGIAN SETTINGS PROGRAM/SCRIPT PILIH LOKASI PROGRAM.

5. PASTIKAN SEMUA SETTINGAN DENGAN BENAR, LALU SIMPAN DENGAN KLIK OK.

6. APABILA INGIN MEMATIKAN SERVICE INI, BUKA TASK SCHEDULER LALU CARI PADA 
DAFTAR SERVICE YANG BERJALAN, KLIK KIRI, LALU KLIK DELETE.        


# FILE autolock_linx_v2.py IS FOR LINUX VERSION ONLY. 
# TERDAPAT BEBERAPA CATATAN UNTUK MENJALANKAN PROGRAM INI DENGAN BENAR :

1. PADA KODE UNTUK MENGGANTI PASSWORD DIPERLUKAN ISIAN NAMA USER PC, INI HANYA DAPAT DILAKUKAN
SECARA MANUAL KARENA SAAT DIJALANKAN DI CRONTAB KODE UNTUK MENDAPATKAN VARIABEL USER TIDAK DAPAT DIPAKAI.
UNTUK ITU JALANKAN PERINTAH INI UNTUK MENGETAHUI NAMA USER :
>> whoami
LALU SALIN OUTPUT COMMAND ITU KE KODE PADA FUNGSI `set_lock_password`,
PADA `command = f'echo "isi di sini:[password_baru_dari_server]" | sudo chpasswd'`

2. MEMASTIKAN PROGRAM XSCREENSAVER BERJALAN KETIKA STARTUP, UNTUK MENAMBAHKAN PENGATURAN INI JALANKAN PADA USER `BUKAN` ROOT.
>>nano ~/.profile
LALU TAMBAHKAN KODE : `xscreensaver &`
CONTOH FILE TERSEBUT :
--------------------------------------------------------------------------------------
> #All other interactive shells will only read .bashrc; this is particularly
> #important for language settings, see below.

> test -z "$PROFILEREAD" && . /etc/profile || true
> xscreensaver &     <-- tambahkan di sini.

> #Most applications support several languages for their output.
> #To make use of this feature, simply uncomment one of the lines below or
--------------------------------------------------------------------------------------

**JANGAN** MEMBUAT FILE .xinitrc ATAU .xsession MISAL DENGAN MENJALANKAN COMMAND : `>>nano ~/.xinitrc` ATAU `>>~/.xsession`
HAL INI DILARANG KARENA AKAN MENGGANGGU SISTEM SAAT STARTUP SEHINGGA AKAN ADA KEMUNGKINAN AKAN GAGAL LOGIN.
APABILA TERLANJUR MEMBUAT FILE TERSEBUT DAN MENGAKIBATKAN KEGAGALAN LOGIN, MAKA MASUK KE TTY DENGAN MENEKAN
TOMBOL `CTRL+ALT+F2`, KEMUDIAN MASUK DENGAN USER BUKAN ROOT. KEMUDIAN HAPUS FILE TERSEBUT, LALU REBOOT DENGAN
COMMAND `>>sudo reboot`.

PROGRAM **XSCREENSAVER** MEMERLUKAN LOKASI VARIABEL `$XAUTHORITY` AGAR DAPAT MENGAKSES DISPLAY, LOKASI VARIABEL TERSEBUT PADA
`/run/user/1000/xauth_*` , FILE `xauth_*` INI MEMILIKI NAMA YANG SELALU BERUBAH SETELAH PC BOOTING KARENA MEMULAI PROGRAM X11
MEMULAI SESSION BARU, MAKA DARI ITU PADA PROGRAM INI SUDAH DITERAPKAN PENCARIAN VARIABEL XAUTHORITY SECARA OTOMATIS PADA
FUNGSI `set_crontab_variable()`.

3. PADA CRONTAB ISIKAN SEPERTI CONTOH SESUAI LOKASI FILE PYTHON DAN PROGRAM AUTOLOCK INI.

`*/10 * * * * /usr/bin/python3.9 /home/user/Downloads/autolock_linx_v2.py >> /home/user/Downloads/logfile_program.log 2>&1`

PADA CONTOH TERSEBUT CRONTAB AKAN MENAJALANKAN PROGRAM SETIAP 10 MENIT.

4. SETIAP KALI PROGRAM DIJALANKAN AKAN MEMBUAT FILE `data_peminjaman.json` YANG BERISI JSON TANGGAL PENGEMBALIAN DAN PASSWORD BARU,
INI DIGUNAKAN SEBAGAI CADANGAN KETIKA PC TIDAK TERKONEKSI INTERNET, FILE INI AKAN TERSIMPAN SE-FOLDER DENGAN PROGRAM INI DILETAKKAN,
MAKA DARI ITU **JANGAN MENGUBAH LOKASI FILE INI**.

5. PROGRAM INI HANYA DAPAT BERJALAN NORMAL PADA VERSI PYTHON >= 3.9 (pengujian telah berhasil pada versi tersebut, dan gagal pada versi di bawah-nya)

6. AGAR SAAT CRONTAB MENGEKSEKUSI PROGRAM PYHTON INI TIDAK MUNCUL KONFIRMASI SUDO, MAKA TAMBAHKAN PERMISSION PADA SUDOERS AGAR DAPAT DIJALANKAN TANPA HARUS KONFIRMASI SUDO.
>>sudo visudo
LALU TAMBAHKAN :
`user ALL=NOPASSWD:/usr/bin/python3.9`
