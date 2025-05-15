Cara Penggunaan:
1. Silahkan download semua file.
2. Buka "Combine.py".
3. Klik "Browse Image" dan gunakan gambar sunspot yang anda mau analisis.
4. Tentukan "Threshold for Sun Disk Ceter Detection" untuk membuat program mendeteksi piringan matahari (rentang nilai 1-255)
5. Klik "Start Measuring Radius" dan klik di pusat piringan matahari dan tepi piringan matahari.
6. Tentukan "Adjust Sunspot Threshold" untuk membuat program mendeteksi luas bintik matahari (rentang nilai 1-255) *Disarankan untuk menggunakan nilai yang sama dengan threshold sebelumnya.
7. Klik "Start Measuring Sunspot's Area" dan tarik cursor sehingga menutupi keseluruhan sunspot.
8. Klik "Start Find Sunspot's Coordinates" dan tekan pusat sunspot.
9. Masukan tanggal dan jam dengan format yang tertera lalu tekan "Calculate Solar Parameter",
10. Tekan "Calculate Real Area of Sunspot" dan area sunspot akan muncul dengan satuan 1/1000000.


Jika terjadi error dan tidak ada program yang keluar ketika membuka "Combine.py":
1. Tekan tombol windows di keyboard dan cari "CMD Prompt" atau "Command Prompt".
2. masukan code berikut "pip install opencv-python numpy"

## Contoh Hasil Program

Berikut adalah contoh hasil pengukuran bintik matahari:

![Contoh Hasil](Hasil%20Program.png)
