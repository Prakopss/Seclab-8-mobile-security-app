# Modul 8: Hacking IoT, OT, and Mobile Platforms
**Program: Cybersecurity Ethical Hacker — PT Vinix Seven Aurum**  
**Skenario Ujian:** Smart Factory Gateway & SCADA Control Panel  
**Entitas Simulasi:** PT Industri Otomasi Sejahtera  

---

## 1. Ringkasan Eksekutif & Karakteristik Aplikasi

Aplikasi ini dirancang sebagai lingkungan ujian praktikum berbasis simulasi realistis (*Black-box Assessment*) yang menggabungkan analisis aplikasi *Mobile (Android)*, autentikasi *IoT Gateway*, celah kredensial bawaan *OT/SCADA*, serta *OS Command Injection* pada fitur pembaruan firmware sensor.

* **Tampilan Realistis (No Hints):** Mengusung tema **Dark/Industrial Factory Dashboard** milik *PT Industri Otomasi Sejahtera*. Tidak ada kata kunci seperti *"Vulnerable"*, *"Lab"*, *"OWASP"*, atau *"Hacking"* di seluruh teks antarmuka maupun komentar HTML.
* **In-Memory Mobile Artifact (`io.BytesIO` & `zipfile`):** Paket sumber aplikasi Android (`AndroidManifest.xml` dan `strings.xml`) di-generate secara dinamis di memori saat diunduh tanpa menulis file sementara ke disk server.
* **Isolasi Penuh (Mocked Command Injection):** Demi keamanan server host (termasuk Replit), fitur *IoT Sensor Firmware Update* tidak pernah memanggil `os.system` atau `subprocess`. Seluruh respons *Command Injection* disimulasikan secara aman di sisi backend Python.

---

## 2. Struktur Direktori Proyek

```text
├── app.py                      # Aplikasi utama Flask, in-memory ZIP generator, & mocked logic
├── requirements.txt            # Dependensi Python (Flask, gunicorn)
├── .replit                     # Konfigurasi eksekusi instan di Replit
├── test_app.py                 # Unit test otomatis untuk memvalidasi alur & kepatuhan rules
├── templates/
│   ├── index.html              # Landing page Smart Factory Gateway & unduhan Mobile App
│   ├── gateway_login.html      # Halaman otorisasi IoT Gateway API Key
│   └── scada_panel.html        # Halaman OT/SCADA Panel, Override Modal, & Firmware Update
└── README.md                   # Panduan Mentor, instruksi eksekusi, & walkthrough solusi
```

---

## 3. Panduan Menjalankan Aplikasi

### A. Menjalankan di Lingkungan Lokal (Windows / Linux / macOS)

1. **Instal dependensi:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Jalankan server Flask:**
   ```bash
   python app.py
   ```
   Akses aplikasi melalui browser pada `http://127.0.0.1:5000`.
3. **Jalankan pengujian otomatis (Unit Test):**
   ```bash
   python test_app.py -v
   ```

### B. Menjalankan di Replit

1. Buat Repl baru dengan template **Python** di [Replit](https://replit.com).
2. Unggah seluruh file proyek (`app.py`, `requirements.txt`, `.replit`, dan folder `templates/`).
3. Tekan tombol **Run**. Konfigurasi `.replit` akan otomatis menjalankan `python3 app.py` pada port `5000`.

---

## 4. Panduan Mentor & Kunci Jawaban (Walkthrough Solusi)

### Tahap 1: Static Analysis Aplikasi Mobile Android (`/`)
1. Peserta membuka halaman utama **Smart Factory Gateway - PT Industri Otomasi Sejahtera** (`/`).
2. Peserta mengklik tombol **"Download Teknisi Mobile App (Android Source)"** yang mengarah ke `/download/mobile-app` dan mengunduh file `ios_teknisi_mobile_android_src.zip`.
3. Setelah diekstrak, terdapat 2 file:
   * `AndroidManifest.xml`: Memiliki komponen dengan konfigurasi `android:exported="true"`.
   * `strings.xml`: Menyimpan kredensial *hardcoded* menuju IoT Gateway:
     ```xml
     <string name="gateway_api_key">IOS_FACTORY_SECRET_9912</string>
     ```

### Tahap 2: Autentikasi IoT Gateway (`/gateway-login`)
1. Peserta membuka halaman `/gateway-login`.
2. Peserta memasukkan **Gateway API Key** yang ditemukan dari `strings.xml`:
   * **Gateway API Key:** `IOS_FACTORY_SECRET_9912`
3. Sistem memvalidasi kunci tersebut dan mengarahkan peserta ke halaman `/scada-panel`.

### Tahap 3: Eksploitasi Default Credentials OT/SCADA (`/scada-panel`)
1. Saat mengakses `/scada-panel`, peserta dihadapkan pada jendela modal **"SCADA Override Login"**.
2. Peserta mencoba kredensial klasik perangkat industri (OT Default Credentials):
   * **Username:** `admin`
   * **Password:** `password` (atau `admin`)
3. Dashboard SCADA terbuka dan menampilkan indikator **Suhu Mesin Utama (`78.4 °C`)**, **Tekanan Air Pendingin (`4.85 Bar`)**, serta form **"IoT Sensor Firmware Update"**.

### Tahap 4: Eksploitasi Command Injection pada IoT Firmware Update
1. Pada form **IoT Sensor Firmware Update**, apabila peserta memasukkan input normal `v2.1`, aplikasi mengembalikan pesan hijau:
   ```text
   Firmware v2.1 successfully deployed to sensors.
   ```
2. Peserta menguji celah *OS Command Injection* dengan menyisipkan operator pemisah perintah (`;`, `|`, atau `&&`) diikuti perintah sistem (`whoami`, `ls`, atau `cat`), misalnya:
   * `v2.1; whoami`
   * `v2.1 | ls`
   * `v2.1 && cat flag.txt`
3. Aplikasi menampilkan simulasi konsol terminal beserta Flag kelulusan:
   ```text
   root@scada-system:~# FLAG{IOT_SCADA_C0MPR0MISED_SUCCESS}
   ```

### Tahap 5 (Bonus): Linux Command Obfuscation (WAF Evasion)
Apabila peserta menguji teknik *WAF Evasion* tanpa menulis kata `"cat"` secara utuh melainkan menggunakan salah satu pola *obfuscation* berikut:
1. `c''at` (contoh: `v2.1; c''at flag.txt`)
2. `c\at` (contoh: `v2.1 | c\at flag.txt`)
3. `c""at` (contoh: `v2.1 && c""at flag.txt`)
4. `/bin/?at` (contoh: `v2.1; /bin/?at flag.txt`)

Aplikasi akan mengenali payload sebagai serangan *WAF Evasion* yang sukses dan langsung mengembalikan simulasi terminal berisi Flag bonus:
```text
root@scada-system:~# FLAG{ELITE_WAF_BYPASS_ACHIEVED_2026}
```


