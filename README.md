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


Aplikasi akan mengenali payload sebagai serangan *WAF Evasion* yang sukses dan langsung mengembalikan simulasi terminal berisi Flag bonus:
```text
root@scada-system:~# FLAG{ELITE_WAF_BYPASS_ACHIEVED_2026}
```


