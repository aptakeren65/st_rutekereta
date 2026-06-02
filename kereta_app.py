import heapq
import streamlit as st
import random

# --- 1. PENGATURAN HALAMAN & CSS THEME ---
st.set_page_config(layout="wide", page_title="Sistem Navigasi & Tiket Kereta")

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

    /* Desain Kartu pada Tabs (Transparan Gelap & Estetik) */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: rgba(15, 32, 67, 0.8) !important;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid rgba(0, 210, 196, 0.4) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        margin-top: 15px;
    }

    /* Styling Menu Tab */
    button[data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #94A3B8 !important;
    }
    
    button[aria-selected="true"] {
        color: #00D2C4 !important;
        border-bottom-color: #00D2C4 !important;
    }

    /* Tombol Utama (Cyan) */
    .stButton>button {
        background-color: #00D2C4 !important;
        color: #0B192C !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #00F5E6 !important;
        box-shadow: 0 0 15px rgba(0, 210, 196, 0.6) !important;
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
    </style>
    """,
    unsafe_allow_html=True
)

# --- JALUR JUDUL UTAMA DALAM KOTAK ---
st.markdown(
    """
    <div class="header-box">
        <h1>🚇 SAS Train Route </h1>
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

# Inisialisasi Data Graph Tetap (Sifatnya Read-Only Sekarang)
if "graph_kereta" not in st.session_state:
    geo_graph = GraphKereta()
    rute_nasional = [
        ("Jakarta", "Bandung", 150), ("Jakarta", "Cirebon", 210),
        ("Bandung", "Cirebon", 130), ("Bandung", "Yogyakarta", 400),
        ("Cirebon", "Semarang", 230), ("Semarang", "Yogyakarta", 120),
        ("Semarang", "Surabaya", 350), ("Yogyakarta", "Surabaya", 330),
        ("Surabaya", "Malang", 90), ("Surabaya", "Banyuwangi", 290),
        ("Medan", "Binjai", 22), ("Palembang", "Lampung", 389),
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

def hitung_estimasi_waktu(jarak_km):
    # Asumsi kecepatan rata-rata kereta api Indonesia adalah 80 km/jam
    kecepatan = 80
    total_jam = jarak_km / kecepatan
    jam = int(total_jam)
    menit = int((total_jam - jam) * 60)
    
    waktu_str = ""
    if jam > 0:
        waktu_str += f"{jam} jam "
    if menit > 0 or jam == 0:
        waktu_str += f"{menit} menit"
    return waktu_str


# --- 4. PEMBUATAN MENU UTAMA (TABS BARU) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Cari Rute ", 
    "🎫 Pesan Tiket ", 
    "🕒 Jadwal Keberangkatan", 
    "🗺️ Peta Jaringan Rel"
])


# ==================== MENU 1: CARI RUTE ====================
with tab1:
    st.subheader("📍 Optimasi Jalur Kereta ")
    col_asal, col_tujuan = st.columns(2)
    with col_asal:
        st_asal = st.selectbox("Titik Keberangkatan:", daftar_stasiun, key="rute_asal")
    with col_tujuan:
        st_tujuan = st.selectbox("Titik Tujuan Akhir:", daftar_stasiun, index=len(daftar_stasiun)-1, key="rute_tujuan")

    if st.button("Mulai Hitung", type="primary", key="btn_nav"):
        if st_asal == st_tujuan:
            st.warning("Stasiun asal dan tujuan tidak boleh sama!")
        else:
            jarak, jalur = hitung_dijkstra(st_asal, st_tujuan)
            if jarak == float("inf"):
                st.error("Maaf, jalur rel antarkota tersebut belum terhubung.")
            else:
                estimasi_waktu = hitung_estimasi_waktu(jarak)
                st.success(f"Rute Terbaik Ditemukan! Total Jarak Tempuh: {jarak} KM")
                
                # Menampilkan Estimasi Perjalanan
                st.info(f"⏱️ **Estimasi Waktu Perjalanan:** {estimasi_waktu} (dengan kecepatan rata-rata 80 km/jam)")
                st.info(" ➔ ".join([f"**{s}**" for s in jalur]))


# ==================== MENU 2: PESAN TIKET KA ====================
with tab2:
    st.subheader("🎫 Sistem Booking Tiket Mandiri")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        nama_penumpang = st.text_input("Nama Lengkap Penumpang:", placeholder="Contoh: Budi Santoso")
        st_tiket_asal = st.selectbox("Stasiun Asal:", daftar_stasiun, key="tk_asal")
        st_tiket_tujuan = st.selectbox("Stasiun Tujuan:", daftar_stasiun, index=1, key="tk_tujuan")
    
    with col_p2:
        kelas_ka = st.selectbox("Kelas Kereta Api:", ["Eksekutif (Premium)", "Bisnis (Nyaman)", "Ekonomi (Hemat)"])
        tanggal_perjalanan = st.date_input("Tanggal Keberangkatan:")
        posisi_kursi = st.selectbox("Pilihan Nomor Kursi:", [f"{baris}{kolom}" for baris in range(1,15) for kolom in ['A','B','C','D']])

    # Hitung tarif otomatis berdasarkan jarak real algoritma Dijkstra
    if st_tiket_asal != st_tiket_tujuan:
        jarak_real, _ = hitung_dijkstra(st_tiket_asal, st_tiket_tujuan)
        if jarak_real != float("inf"):
            # Simulasi harga per km berdasarkan kelas
            pengali_kelas = {"Eksekutif (Premium)": 1500, "Bisnis (Nyaman)": 900, "Ekonomi (Hemat)": 500}
            total_harga = jarak_real * pengali_kelas[kelas_ka]
            estimasi_waktu_tiket = hitung_estimasi_waktu
