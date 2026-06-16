import heapq
import streamlit as st
import random
from datetime import datetime # Ditambahkan hanya untuk mengambil waktu log admin

# --- 1. PENGATURAN HALAMAN & CSS THEME ---
st.set_page_config(layout="wide", page_title="SAS KERETA API")

# Injeksi CSS Custom untuk Background Gambar Kereta + Efek Blur + Glassmorphism Card
st.markdown(
    """
    <style>
    /* Mengunci background secara mutlak di lapisan paling belakang */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(rgba(11, 25, 44, 0.85), rgba(11, 25, 44, 0.85)), 
                    url("https://images.unsplash.com/photo-1532103054090-334e6e60ab29?q=80&w=2070") no-repeat center center fixed !important;
        background-size: cover !important;
    }

    /* Efek Blur pada Glassmorphism Konten Utama */
    [data-testid="stHeader"], [data-testid="stAppViewContainer"] {
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
    }
    
    /* Warna Judul Utama dan Subheader */
    h1, h2, h3, h4 {
        color: #00D2C4 !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
    }
    
    /* Memaksa Semua Teks Standar Menjadi Terang */
    p, b, span, label, .stWidgetLabel p {
        color: #E2E8F0 !important;
    }

    /* Styling Kotak Khusus untuk Judul */
    .header-box {
        background-color: rgba(15, 32, 67, 0.75) !important;
        padding: 25px 35px;
        border-radius: 20px;
        border: 2px solid rgba(0, 210, 196, 0.5) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 25px;
    }
    .header-box h1 {
        margin: 0 !important;
        padding-bottom: 5px !important;
    }
    .header-box p {
        margin: 0 !important;
        font-size: 16px !important;
        color: #94A3B8 !important;
    }

    /* Desain Kartu Wadah Konten di Bawah Menu Navigasi (Transparan Gelap & Estetik) */
    .content-container-card {
        background-color: rgba(15, 32, 67, 0.8) !important;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid rgba(0, 210, 196, 0.4) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        margin-top: 20px;
    }

    /* Tombol Utama (Primary) - Kontras (Warna Orange/Coral) */
    .stButton>button[data-testid="baseButton-primary"] {
        background-color: #FF5733 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    
    .stButton>button[data-testid="baseButton-primary"]:hover {
        background-color: #FF785A !important;
        box-shadow: 0 0 15px rgba(255, 87, 51, 0.6) !important;
    }

    /* Tombol Secondary (Inactive) - Outline */
    .stButton>button[data-testid="baseButton-secondary"] {
        background-color: transparent !important;
        color: #FF5733 !important;
        border: 1px solid #FF5733 !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        width: 100%;
    }

    .stButton>button[data-testid="baseButton-secondary"]:hover {
        background-color: rgba(255, 87, 51, 0.1) !important;
        box-shadow: 0 0 15px rgba(255, 87, 51, 0.4) !important;
    }
    
    /* Box Peringatan / Info / Tiket */
    .stAlert {
        border-radius: 15px !important;
        border: 1px solid rgba(0, 210, 196, 0.4) !important;
        background-color: rgba(11, 25, 44, 0.85) !important;
    }

    /* Simulasi Desain Tiket Fisik */
    .ticket-box {
        background: linear-gradient(135deg, #1E3E62, #0B192C);
        border: 2px dashed #00D2C4;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
    }

    /* Kartu Informasi Komponen Rute Modern */
    .route-card {
        background: rgba(11, 25, 44, 0.6);
        border: 1px solid rgba(0, 210, 196, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- JALUR JUDUL UTAMA DALAM KOTAK ---
st.markdown(
    """
    <div class="header-box">
        <h1>🚇 SAS Train Route KA </h1>
        <p>Sistem Navigasi Jalur Indonesia</p>
    </div>
    """, 
    unsafe_allow_html=True
)


# --- 2. STRUKTUR DATA GRAPH ---
class GraphKereta:
    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def tambah_rute(self, asal, tujuan, jarak_km):
        asal = asal.strip()
        tujuan = tujuan.strip()
        if asal and tujuan and asal != tujuan:
            self.nodes.add(asal)
            self.nodes.add(tujuan)
            if asal not in self.edges: self.edges[asal] = []
            if tujuan not in self.edges: self.edges[tujuan] = []
            if not any(node == tujuan for node, _ in self.edges[asal]):
                self.edges[asal].append((tujuan, jarak_km))
                self.edges[tujuan].append((asal, jarak_km))
                
    def hapus_rute(self, asal, tujuan):
        if asal in self.edges:
            self.edges[asal] = [edge for edge in self.edges[asal] if edge[0] != tujuan]
        if tujuan in self.edges:
            self.edges[tujuan] = [edge for edge in self.edges[tujuan] if edge[0] != asal]

# Inisialisasi Data Graph Tetap
if "graph_kereta" not in st.session_state:
    geo_graph = GraphKereta()
    rute_nasional = [
        ("Jakarta", "Bandung", 150), ("Jakarta", "Cirebon", 210),
        ("Bandung", "Cirebon", 139), ("Bandung", "Yogyakarta", 495),
        ("Cirebon", "Semarang", 228), ("Semarang", "Yogyakarta", 144),
        ("Semarang", "Surabaya", 350), ("Yogyakarta", "Surabaya", 330),
        ("Surabaya", "Malang", 90), ("Surabaya", "Banyuwangi", 285),
        ("Tangerang", "Bandung", 29), ("Palembang", "Lampung", 389),
        ("Makassar", "Parepare", 145), ("Banyuwangi", "Makassar", 820)
    ]
    for asal_st, tujuan_st, jarak_st in rute_nasional:
        geo_graph.tambah_rute(asal_st, tujuan_st, jarak_st)
    st.session_state.graph_kereta = geo_graph

graph = st.session_state.graph_kereta
daftar_stasiun = sorted(list(graph.nodes))


# --- 3. FUNGSI ALGORITMA DIJKSTRA & ESTIMASI PERJALANAN ---
def hitung_dijkstra(asal, tujuan):
    queue = [(0, asal)]
    dist = {n: float("inf") for n in graph.nodes}
    dist[asal] = 0
    prev = {n: None for n in graph.nodes}

    while queue:
        d, curr = heapq.heappop(queue)
        if curr == tujuan: break
        if d > dist[curr]: continue
        for neighbor, weight in graph.edges.get(curr, []):
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = curr
                heapq.heappush(queue, (new_dist, neighbor))

    path = []
    temp = tujuan
    while temp:
        path.append(temp)
        temp = prev[temp]
    path.reverse()
    return dist[tujuan], path

def hitung_estimasi_waktu(jarak_km, kecepatan=80):
    total_jam = jarak_km / kecepatan
    jam = int(total_jam)
    menit = int((total_jam - jam) * 60)
    
    waktu_str = ""
    if jam > 0:
        waktu_str += f"{jam} jam "
    if menit > 0 or jam == 0:
        waktu_str += f"{menit} menit"
    return waktu_str


# ==================== UPDATE DATA USER & PASSWORD BARU (3 ADMIN) ====================
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "aulia": {"password": "admin", "role": "Admin"},
        "syauqi": {"password": "admin", "role": "Admin"},
        "suci": {"password": "admin", "role": "Admin"},
        "user_biasa": {"password": "user123", "role": "User"}
    }

if "admin_logs" not in st.session_state:
    st.session_state.admin_logs = []

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    st.session_state.current_user = None
    st.session_state.current_role = None


# ==================== LOGIKA PENGECEKAN LOGIN & VALIDASI TENDANG AKUN ====================
if not st.session_state.is_logged_in:
    st.markdown('<div class="content-container-card">', unsafe_allow_html=True)
    st.subheader("🔐 Silakan Login Terlebih Dahulu")
    user_input = st.text_input("Username:")
    pass_input = st.text_input("Password:", type="password")
    
    if st.button("Masuk Aplikasi", type="primary"):
        if user_input in st.session_state.users_db:
            if st.session_state.users_db[user_input]["password"] == pass_input:
                st.session_state.is_logged_in = True
                st.session_state.current_user = user_input
                st.session_state.current_role = st.session_state.users_db[user_input]["role"]
                st.session_state.menu_aktif = "📍 Cari Rute"
                st.rerun()
            else:
                st.error("Password yang Anda masukkan salah!")
        else:
            st.error("Akun Anda tidak ditemukan atau sudah dihapus oleh Admin!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# VALIDASI: Jika akun yang sedang login dihapus oleh Admin di tab sebelah, otomatis kick out!
if st.session_state.current_user not in st.session_state.users_db:
    st.session_state.is_logged_in = False
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.error("Akun Anda telah dihapus oleh Admin! Anda tidak dapat lagi mengakses aplikasi ini.")
    if st.button("Kembali ke Login"):
        st.rerun()
    st.stop()


# --- 4. PEMBUATAN MENU NAVIGASI HORIZONTAL DENGAN COLUMNS ---
if "menu_aktif" not in st.session_state:
    st.session_state.menu_aktif = "📍 Cari Rute"
if "riwayat_tiket" not in st.session_state:
    st.session_state.riwayat_tiket = []

# Tampilan Menu bertambah 1 kolom (menjadi 8) jika login sebagai Admin
is_admin = st.session_state.current_role == "Admin"
jumlah_kolom = 8 if is_admin else 7
kolom_menu = st.columns(jumlah_kolom)

with kolom_menu[0]:
    if st.button("📍 Cari Rute", type="primary" if st.session_state.menu_aktif == "📍 Cari Rute" else "secondary", use_container_width=True):
        st.session_state.menu_aktif = "📍 Cari Rute"
        st.rerun()
with kolom_menu[1]:
    if st.button("⏱️ Estimasi Waktu", type="primary" if st.session_state.menu_aktif == "⏱️ Estimasi Waktu" else "secondary", use_container_width=True):
        st.session_state.menu_aktif = "⏱️ Estimasi Waktu"
        st.rerun()
with kolom_menu[2]:
    if st.button("🎫 Pesan Tiket ", type="primary" if st.session_state.menu_aktif == "🎫 Pesan Tiket " else "secondary", use_container_width=True):
        st.session_state.menu_aktif = "🎫 Pesan Tiket "
        st.rerun()
with kolom_menu[3]:
    if st.button("🕒 Jadwal Kereta", type="primary" if st.session_state.menu_aktif == "🕒 Jadwal Kereta" else "secondary", use_container_width=True):
        st.session_state.menu_aktif = "🕒 Jadwal Kereta"
        st.rerun()
with kolom_menu[4]:
    if st.button("🎰 Live Traffic", type="primary" if st.session_state.menu_aktif == "🎰 Live Traffic" else "secondary", use_container_width=True):
        st.session_state.menu_aktif = "🎰 Live Traffic"
        st.rerun()
with kolom_menu[5]:
    if st.button("🗂️ Papan Kartu Info", type="primary" if st.session_state.menu_aktif == "🗂️ Papan Kartu Info" else "secondary", use_container_width=True):
        st.session_state.menu_aktif = "🗂️ Papan Kartu Info"
        st.rerun()
with kolom_menu[6]:
    if st.button("🛍️ Penjualan", type="primary" if st.session_state.menu_aktif == "🛍️ Penjualan" else "secondary", use_container_width=True):
        st.session_state.menu_aktif = "🛍️ Penjualan"
        st.rerun()

# Kolom ke-8 murni tombol dinamis tambahan khusus Admin
if is_admin:
    with kolom_menu[7]:
        if st.button("🛠️ Panel Admin", type="primary" if st.session_state.menu_aktif == "🛠️ Panel Admin" else "secondary", use_container_width=True):
            st.session_state.menu_aktif = "🛠️ Panel Admin"
            st.rerun()


# BUNGKUS SELURUH KONTEN DI DALAM KOTAK TRANSPARAN CSS
st.markdown('<div class="content-container-card">', unsafe_allow_html=True)

# Tampilkan Status User Aktif di Sidebar
st.sidebar.markdown(f"### 👤 Logged in as:\n**{st.session_state.current_user}** (`{st.session_state.current_role}`)")
if st.sidebar.button("🚪 Logout Aplikasi", use_container_width=True):
    st.session_state.is_logged_in = False
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.rerun()

# ==================== MENU 1: CARI RUTE TERBAIK ====================
if st.session_state.menu_aktif == "📍 Cari Rute":
    st.subheader("📍 Optimasi Jalur Kereta")
    col_asal, col_tujuan = st.columns(2)
    with col_asal:
        st_asal = st.selectbox("Titik Keberangkatan:", daftar_stasiun, key="rute_asal")
    with col_tujuan:
        st_tujuan = st.selectbox("Titik Tujuan Akhir:", daftar_stasiun, index=len(daftar_stasiun)-1, key="rute_tujuan")

    if st.button("Mulai Hitung ", type="primary", key="btn_nav"):
        if st_asal == st_tujuan:
            st.warning("Stasiun asal and tujuan tidak boleh sama!")
        else:
            jarak, jalur = hitung_dijkstra(st_asal, st_tujuan)
            if jarak == float("inf"):
                st.error("Maaf, jalur rel antarkota tersebut belum terhubung.")
            else:
                st.success(f"🏁 Rute Ditemukan! Total Jarak Tempuh: {jarak} KM")
                st.info(" ➔ ".join([f"*{s}*" for s in jalur]))


# ==================== MENU 2: ESTIMASI WAKTU PERJALANAN ====================
elif st.session_state.menu_aktif == "⏱️ Estimasi Waktu":
    st.subheader("⏱️Estimasi Waktu Perjalanan")
    st.write("berapa lama waktu yang kamu butuhkan berdasarkan kecepatan laju kereta api.")
    
    col_est1, col_est2 = st.columns(2)
    with col_est1:
        st_est_asal = st.selectbox("Pilih Stasiun Asal:", daftar_stasiun, key="est_asal")
        st_est_tujuan = st.selectbox("Pilih Stasiun Tujuan:", daftar_stasiun, index=len(daftar_stasiun)-1, key="est_tujuan")
    with col_est2:
        kecepatan_pilihan = st.slider("Atur Kecepatan Rata-Rata Kereta (KM/Jam):", min_value=50, max_value=120, value=80, step=5)

    if st.button("Hitung Durasi", type="primary", key="btn_estimasi"):
        if st_est_asal == st_est_tujuan:
            st.warning("Stasiun asal dan tujuan tidak boleh sama!")
        else:
            jarak_est, jalur_est = hitung_dijkstra(st_est_asal, st_est_tujuan)
            if jarak_est == float("inf"):
                st.error("Rute tidak terhubung, estimasi waktu tidak dapat dihitung.")
            else:
                waktu_hasil = hitung_estimasi_waktu(jarak_est, kecepatan_pilihan)
                st.metric(label=f"Durasi Perjalanan ({kecepatan_pilihan} km/jam)", value=waktu_hasil)
                st.write(f"ℹ️ Jarak total yang akan ditempuh melewati rute ini adalah *{jarak_est} KM*.")


# ==================== MENU 3: PESAN TIKET MANDIRI ====================
elif st.session_state.menu_aktif == "🎫 Pesan Tiket ":
    st.subheader("🎫 Sistem Booking Tiket ")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        nama_penumpang = st.text_input("Nama Lengkap Penumpang:", placeholder="Contoh: Budi Santoso")
        st_tiket_asal = st.selectbox("Stasiun Asal:", daftar_stasiun, key="tk_asal")
        st_tiket_tujuan = st.selectbox("Stasiun Tujuan:", daftar_stasiun, index=1, key="tk_tujuan")
    
    with col_p2:
        kelas_ka = st.selectbox("Kelas Kereta Api:", ["Eksekutif (Premium)", "Bisnis (Nyaman)", "Ekonomi (Hemat)"])
        tanggal_perjalanan = st.date_input("Tanggal Keberangkatan:")
        posisi_kursi = st.selectbox("Pilihan Nomor Kursi:", [f"{baris}{kolom}" for baris in range(1,15) for kolom in ['A','B','C','D']])

    if st_tiket_asal != st_tiket_tujuan:
        jarak_real, _ = hitung_dijkstra(st_tiket_asal, st_tiket_tujuan)
        if jarak_real != float("inf"):
            pengali_kelas = {"Eksekutif (Premium)": 1500, "Bisnis (Nyaman)": 900, "Ekonomi (Hemat)": 500}
            total_harga = jarak_real * pengali_kelas[kelas_ka]
            estimasi_waktu_tiket = hitung_estimasi_waktu(jarak_real)
            
            st.markdown(f"### 💰 Estimasi Biaya: *Rp {total_harga:,.0f}*")
            
            if st.button("Cetak E-Ticket", type="primary", key="btn_tiket"):
                if not nama_penumpang:
                    st.error("Mohon isi nama penumpang terlebih dahulu!")
                else:
                    kode_booking = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
                    
                    # Simpan ke riwayat tiket
                    tiket_baru = {
                        "kode": kode_booking,
                        "nama": nama_penumpang,
                        "asal": st_tiket_asal,
                        "tujuan": st_tiket_tujuan,
                        "kelas": kelas_ka,
                        "tanggal": str(tanggal_perjalanan),
                        "kursi": posisi_kursi,
                        "harga": total_harga
                    }
                    st.session_state.riwayat_tiket.append(tiket_baru)
                    
                    st.success("Transaksi Berhasil! E-Ticket Anda telah diterbitkan di bawah ini:")
                    
                    st.markdown(
                        f"""
                        <div class="ticket-box">
                            <h3 style='color: #00D2C4; margin-top:0;'>SAS KERETA API - E-TICKET</h3>
                            <hr style='border-color: rgba(0, 210, 196, 0.3);'>
                            <table style='width:100%; border:none; font-size:15px; color:#E2E8F0;'>
                                <tr><td><b>Kode Booking</b></td><td>: <span style='color:#00D2C4; font-weight:bold;'>{kode_booking}</span></td></tr>
                                <tr><td><b>Nama Penumpang</b></td><td>: {nama_penumpang}</td></tr>
                                <tr><td><b>Perjalanan</b></td><td>: {st_tiket_asal} ➔ {st_tiket_tujuan} ({jarak_real} KM)</td></tr>
                                <tr><td><b>Estimasi Perjalanan</b></td><td>: {estimasi_waktu_tiket}</td></tr>
                                <tr><td><b>Tanggal / Kursi</b></td><td>: {tanggal_perjalanan} / Kursi {posisi_kursi}</td></tr>
                                <tr><td><b>Kelas & Tarif</b></td><td>: {kelas_ka} - <b>Rp {total_harga:,.0f}</b></td></tr>
                            </table>
                            <p style='font-size:11px; color:#94A3B8; margin-top:15px; text-align:center;'>*Tunjukkan kode booking ini saat melakukan boarding di stasiun.</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
        else:
            st.error("Rute stasiun tidak terhubung, tiket tidak dapat dipesan.")
    else:
        st.warning("Silakan pilih stasiun asal dan tujuan yang berbeda untuk menghitung tarif tiket.")


# ==================== MENU 4: JADWAL KEBERANGKATAN ====================
elif st.session_state.menu_aktif == "🕒 Jadwal Kereta":
    st.subheader("🕒 Informasi Jadwal Keberangkatan")
    st_pilih_jadwal = st.selectbox("Pilih Stasiun Keberangkatan untuk Melihat Jadwal:", daftar_stasiun, key="jd_stasiun")
    
    random.seed(len(st_pilih_jadwal)) 
    kereta_list = ["Argo Bromo Anggrek", "Gajayana", "Argo Lawu", "Taksaka", "Brawijaya", "Kertajaya", "Jayakarta", "Logawa", "Argo Parahyangan"]
    
    tujuan_tersedia = [tujuan for tujuan, _ in graph.edges.get(st_pilih_jadwal, [])]
    if not tujuan_tersedia:
        tujuan_tersedia = [s for s in daftar_stasiun if s != st_pilih_jadwal]
    
    for i in range(4): 
        nama_ka = kereta_list[(len(st_pilih_jadwal) + i) % len(kereta_list)]
        jam = f"{8 + (i*4):02d}:{random.choice([0,15,30,45]):02d}"
        tujuan_ka = tujuan_tersedia[i % len(tujuan_tersedia)]
        status = random.choice(["ON TIME", "ON TIME", "DELAY 10 MNT", "BOARDING"])
        
        with st.expander(f"⏱️ Jam {jam} — {nama_ka} (Tujuan Akhir: {tujuan_ka})"):
            st.write(f"Status Keberangkatan: *{status}*")
            st.write("Silakan bersiap di peron jalur yang sesuai.")


# ==================== MENU 5: LIVE TRAFFIC & SIMULATOR KEPADATAN ====================
elif st.session_state.menu_aktif == "🎰 Live Traffic":
    st.subheader("🎰 Live Traffic")
    st.write("Memantau status keramaian dan lalu lintas stasiun ")
    
    st_pilih_simulasi = st.selectbox("Pilih Stasiun yang Ingin Dipantau:", daftar_stasiun, key="sim_stasiun")
    
    status_preset = {
        "Bandung": {"persen": 65, "penumpang": 1200, "antrean": 4, "teks": "🟡 CUKUP PADAT ", "alert": "ramai"},
        "Semarang": {"persen": 58, "penumpang": 950, "antrean": 3, "teks": "🟡 CUKUP PADAT ", "alert": "ramai"},
        "Yogyakarta": {"persen": 70, "penumpang": 1650, "antrean": 5, "teks": "🟡 CUKUP PADAT ", "alert": "ramai"},
        "Cirebon": {"persen": 50, "penumpang": 780, "antrean": 2, "teks": "🟡 CUKUP PADAT ", "alert": "ramai"},
        
        "Malang": {"persen": 92, "penumpang": 2100, "antrean": 8, "teks": "🔴 SANGAT PADAT", "alert": "macet"},
        "Jakarta": {"persen": 96, "penumpang": 2450, "antrean": 11, "teks": "🔴 SANGAT PADAT", "alert": "macet"},
        "Surabaya": {"persen": 88, "penumpang": 1980, "antrean": 7, "teks": "🔴 SANGAT PADAT", "alert": "macet"},
        
        "Banyuwangi": {"persen": 25, "penumpang": 220, "antrean": 1, "teks": "🟢 SANGAT LANCAR", "alert": "lancar"},
        "Tangerang": {"persen": 25, "penumpang":230, "antrean": 1, "teks": "🟢 SANGAT LANCAR ", "alert": "lancar"},
        "Lampung": {"persen": 30, "penumpang": 340, "antrean": 2, "teks": "🟢 SANGAT LANCAR ", "alert": "lancar"},
        "Makassar": {"persen": 20, "penumpang": 180, "antrean": 1, "teks": "🟢 SANGAT LANCAR ", "alert": "lancar"},
        "Palembang": {"persen": 28, "penumpang": 290, "antrean": 1, "teks": "🟢 SANGAT LANCAR ", "alert": "lancar"},
        "Parepare": {"persen": 18, "penumpang": 140, "antrean": 1, "teks": "🟢 SANGAT LANCAR ", "alert": "lancar"}
    }
    
    data_stasiun = status_preset.get(st_pilih_simulasi, {"persen": 30, "penumpang": 300, "antrean": 1, "teks": "🟢 SANGAT LANCAR / SEPI", "alert": "lancar"})
    
    kepadatan_persen = data_stasiun["persen"]
    jumlah_penumpang = data_stasiun["penumpang"]
    jumlah_antrean = data_stasiun["antrean"]
    status_teks = data_stasiun["teks"]
    warna_alert = data_stasiun["alert"]
    
    if warna_alert == "lancar":
        tips = "Kondisi stasiun sangat kondusif. Waktu yang tepat untuk melakukan boarding tanpa antri."
    elif warna_alert == "ramai":
        tips = "Volume penumpang sedang meningkat. Harap datang 30 menit lebih awal sebelum jam keberangkatan."
    else:
        tips = "⚠️ PERINGATAN: Stasiun mengalami lonjakan parah!. Disarankan segera menuju stasiun."

    st.write("") 
    if warna_alert == "lancar":
        st.success(f"🟢 *Status Stasiun {st_pilih_simulasi}:* Saat ini terpantau sangat lancar.")
    elif warna_alert == "ramai":
        st.warning(f"🟡 *Perhatian:* Stasiun {st_pilih_simulasi} dalam kondisi cukup padat/ramai.")
    else:
        st.error(f"🚨 *Peringatan:* Stasiun {st_pilih_simulasi} dalam kondisi sangat padat!")
    st.write("")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric(label="Status Arus Lalu Lintas", value=status_teks)
    with col_s2:
        st.metric(label="Estimasi Penumpang Aktif", value=f"{jumlah_penumpang} Orang")
    with col_s3:
        st.metric(label="Jumlah Kereta Bersandar/Antri", value=f"{jumlah_antrean} KA")
        
    st.write("---")
    st.write("*Grafik Batas Kapasitas Area Peron Stasiun:*")
    st.progress(kepadatan_persen / 100)
    st.write(f"Tingkat keterisian area tunggu: *{kepadatan_persen}%*")
    
    st.markdown(
        f"""
        <div style="background-color: rgba(15, 32, 67, 0.9); padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 210, 196, 0.3); margin-top: 15px;">
            <b style="color: #00D2C4;">📢 Rekomendasi Dari Kami Stasiun {st_pilih_simulasi}:</b><br>
            <span style="font-size: 14px; color: #E2E8F0;">{tips}</span>
        </div>
        """, unsafe_allow_html=True
    )

# ==================== MENU 6: PAPAN KARTU INFORMASI RUTE ====================
elif st.session_state.menu_aktif == "🗂️ Papan Kartu Info":
    st.subheader("🗂️ Papan Informasi Jaringan Rel")
    st.write("Daftar lengkap seluruh koneksi rel langsung antarkota.")

    data_j = []
    for s, t_list in graph.edges.items():
        for t, j in t_list:
            if (t, s, j) not in data_j: 
                data_j.append((s, t, j))
                
    data_j.sort(key=lambda x: x[0])

    opsi_filter = st.selectbox("Filter Tampilan Berdasarkan Kondisi Jalur:", ["Semua Jalur Kereta", "Hanya Jalur Normal", "Hanya Jalur Perbaikan"])
    st.write("---")

    col_grid1, col_grid2, col_grid3 = st.columns(3)
    
    kartu_terbuat = 0
    for i, (asal_r, tujuan_r, jarak_r) in enumerate(data_j):
        status_kondisi = "✅ JALUR NORMAL" if i % 5 != 0 else "⚠️ DALAM PERBAIKAN"
        warna_status = "#00D2C4" if i % 5 != 0 else "#FF4B4B"
        
        if opsi_filter == "Hanya Jalur Normal" and status_kondisi != "✅ JALUR NORMAL":
            continue
        if opsi_filter == "Hanya Jalur Perbaikan" and status_kondisi != "⚠️ DALAM PERBAIKAN":
            continue

        if kartu_terbuat % 3 == 0:
            target_col = col_grid1
        elif kartu_terbuat % 3 == 1:
            target_col = col_grid2
        else:
            target_col = col_grid3
            
        target_col.markdown(
            f"""
            <div class="route-card">
                <span style="font-size: 11px; color: {warna_status}; font-weight: bold; float: right;">{status_kondisi}</span>
                <h4 style="margin: 0 0 10px 0; font-size: 17px; color: #E2E8F0;">🚂 Koridor Rel</h4>
                <p style="font-size: 16px; font-weight: bold; margin: 5px 0;">{asal_r} &harr; {tujuan_r}</p>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">
                <table style="width: 100%; font-size: 13px; color: #94A3B8; border: none;">
                    <tr><td>📐 Jarak Utama</td><td style="text-align: right; color: #E2E8F0;"><b>{jarak_r} KM</b></td></tr>
                    <tr><td>⏱️ Waktu Tempuh</td><td style="text-align: right; color: #00D2C4;"><b>{hitung_estimasi_waktu(jarak_r)}</b></td></tr>
                </table>
            </div>
            """, 
            unsafe_allow_html=True
        )
        kartu_terbuat += 1

    if kartu_terbuat == 0:
        st.info("Tidak ada rute rel yang sesuai dengan pilihan Anda.")

# ==================== MENU 7: MENU PENJUALAN (RIWAYAT) ====================
elif st.session_state.menu_aktif == "🛍️ Penjualan":
    st.subheader("🛍️ Riwayat Pembelian Tiket")
    
    if not st.session_state.riwayat_tiket:
        st.info("Belum ada tiket yang dibeli pada sesi ini.")
    else:
        for i, tiket in enumerate(st.session_state.riwayat_tiket):
            st.markdown(f"""
            <div class="ticket-box" style="margin-bottom: 15px;">
                <h4 style="color: #FF5733; margin-top:0;">E-Ticket #{i+1} - Kode Booking: {tiket['kode']}</h4>
                <hr style='border-color: rgba(255, 87, 51, 0.3);'>
                <p><b>Nama Penumpang:</b> {tiket['nama']} | <b>Kelas Kereta:</b> {tiket['kelas']}</p>
                <p><b>Rute Perjalanan:</b> {tiket['asal']} &rarr; {tiket['tujuan']}</p>
                <p><b>Tanggal Keberangkatan:</b> {tiket['tanggal']} | <b>Nomor Kursi:</b> {tiket['kursi']}</p>
                <p style="color: #00D2C4; font-weight: bold; font-size: 18px; margin-top: 10px;">Total Pembayaran: Rp {tiket['harga']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)


# ==================== MENU 8: KELOLA ADMIN (3 ADMIN UTAMA) ====================
elif st.session_state.menu_aktif == "🛠️ Panel Admin" and is_admin:
    st.subheader("🛠️ Panel Kendali Utama (Aulia, Syauqi, & Suci)")
    
    t1, t2, t3 = st.tabs(["📌 Manipulasi Rute Rel (Graph Goods)", "👥 Manajemen Akun User", "📜 History Logs Aktivitas"])
    
    # TAB 1: Tambah / Hapus Rute Rel Kereta
    with t1:
        st.write("### ➕ Tambah Rute Baru Kedalam Sistem")
        col_ad1, col_ad2, col_ad3 = st.columns(3)
        with col_ad1: in_asal = st.text_input("Nama Stasiun Keberangkatan Baru:")
        with col_ad2: in_tujuan = st.text_input("Nama Stasiun Kedatangan Baru:")
        with col_ad3: in_jarak = st.number_input("Input Jarak Jalur (KM):", min_value=1, value=50)
        
        if st.button("Simpan Rute Baru Ke Graph", type="primary"):
            if in_asal and in_tujuan:
                graph.tambah_rute(in_asal, in_tujuan, in_jarak)
                waktu_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.admin_logs.append(f"[{waktu_log}] Admin {st.session_state.current_user} berhasil MENAMBAHKAN rute rel baru: {in_asal} ↔ {in_tujuan} ({in_jarak} KM)")
                st.success("Rute baru berhasil ditambahkan dinamis ke memori Graph!")
                st.rerun()
                
        st.write("---")
        st.write("### 🗑️ Hapus Jalur Rel dari Sistem")
        st_hp_asal = st.selectbox("Pilih Stasiun Asal Jalur Rel:", daftar_stasiun, key="h_asal")
        st_hp_tuj = st.selectbox("Pilih Stasiun Tujuan Jalur Rel:", daftar_stasiun, key="h_tuj")
        if st.button("Bongkar / Hapus Jalur Rel", type="primary"):
            graph.hapus_rute(st_hp_asal, st_hp_tuj)
            waktu_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.admin_logs.append(f"[{waktu_log}] Admin {st.session_state.current_user} berhasil MENGHAPUS jalur rel: {st_hp_asal} ↔ {st_hp_tuj}")
            st.success("Jalur rel berhasil dicabut dari sistem data!")
            st.rerun()

    # TAB 2: Tambah Akun / Hapus Akun User
    with t2:
        st.write("### ➕ Daftarkan Akun Akses Baru")
        reg_user = st.text_input("Buat Username Baru:")
        reg_pass = st.text_input("Buat Password Baru:", type="password")
        reg_role = st.selectbox("Pilih Hak Akses Role:", ["User", "Admin"])
        
        if st.button("Simpan User Baru", type="primary"):
            if reg_user and reg_pass:
                st.session_state.users_db[reg_user] = {"password": reg_pass, "role": reg_role}
                waktu_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.admin_logs.append(f"[{waktu_log}] Admin {st.session_state.current_user} mendaftarkan akun baru: Username [{reg_user}] dengan Hak Akses [{reg_role}]")
                st.success(f"Akun [{reg_user}] berhasil terdaftar ke database!")
                st.rerun()
                
        st.write("---")
        st.write("### 🔒 Daftar Seluruh Akun Aplikasi")
        for username, data_akun in list(st.session_state.users_db.items()):
            col_u1, col_u2 = st.columns([3, 1])
            with col_u1:
                st.write(f"👤 Username: **{username}** | Role Akses: `{data_akun['role']}`")
            with col_u2:
                # Proteksi agar 3 admin utama tidak bisa saling hapus akun satu sama lain
                if username in ["aulia", "syauqi", "suci"]:
                    st.write("⚙️ Akun Developer")
                else:
                    if st.button(f"Hapus Akun {username}", key=f"btn_del_{username}"):
                        del st.session_state.users_db[username]
                        waktu_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.admin_logs.append(f"[{waktu_log}] Admin {st.session_state.current_user} MENGHAPUS secara permanen akun user: [{username}]")
                        st.success(f"Akun {username} sukses didelete!")
                        st.rerun()

    # TAB 3: History Log pencatatan aktivitas Admin
    with t3:
        st.write("### 📜 Riwayat Modifikasi Data Sistem Admin")
        if not st.session_state.admin_logs:
            st.info("Belum ada tindakan admin apapun yang tercatat pada sesi ini.")
        else:
            for log_item in reversed(st.session_state.admin_logs):
                st.text_area("Log Action:", value=log_item, height=60, disabled=True, label_visibility="collapsed")

# MENUTUP PEMBUNGKUS KOTAK TRANSPARAN CSS
st.markdown('</div>', unsafe_allow_html=True)
