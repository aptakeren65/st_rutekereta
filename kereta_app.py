import heapq
import math
import streamlit as st

# --- 1. PENGATURAN HALAMAN & TEMA WARNA PINK (CSS INJECTION) ---
st.set_page_config(layout="wide", page_title="Sistem Navigasi & Tiketing Kereta")

st.markdown(
    """
    <style>
    .stApp { background-color: #fff0f6; }
    h1, h2, h3, h4 { color: #d63384 !important; }
    p, b, span { color: #495057; }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #fcc2d7;
        box-shadow: 0 10px 15px rgba(214, 51, 132, 0.05);
        margin-top: 15px;
    }
    button[data-baseweb="tab"] { font-size: 18px; font-weight: bold; }
    button[aria-selected="true"] { color: #d63384 !important; border-bottom-color: #d63384 !important; }
    .stButton>button {
        background-color: #ff85a1; color: white !important;
        border-radius: 12px; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #d63384; color: white !important; }
    .stAlert { border-radius: 15px; border: 1px solid #fcc2d7; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💖 Train Planner & Smart Ticketing System")
st.write("Aplikasi Navigasi Rute Terpendek sekaligus **Estimasi Biaya Tiket & Kelas Perjalanan Kereta**.")
st.markdown("---")


# --- FUNGSIONAL MATEMATIKA: FORMULA HAVERSINE ---
def hitung_jarak_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    rad_lat1, rad_lon1 = math.radians(lat1), math.radians(lon1)
    rad_lat2, rad_lon2 = math.radians(lat2), math.radians(lon2)
    
    dlat = rad_lat2 - rad_lat1
    dlon = rad_lon2 - rad_lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c)


# --- 2. STRUKTUR DATA GRAPH DENGAN KALKULASI OTOMATIS ---
class GraphKeretaOtomatis:
    def __init__(self):
        self.nodes = set()
        self.edges = {}
        self.koordinat = {}

    def tambah_stasiun(self, nama_stasiun, lat, lon):
        nama_stasiun = nama_stasiun.strip()
        if nama_stasiun:
            self.nodes.add(nama_stasiun)
            self.koordinat[nama_stasiun] = (float(lat), float(lon))
            if nama_stasiun not in self.edges:
                self.edges[nama_stasiun] = []

    def tambah_rute_otomatis(self, asal, tujuan):
        asal, tujuan = asal.strip(), tujuan.strip()
        if asal in self.koordinat and tujuan in self.koordinat and asal != tujuan:
            jarak_km = hitung_jarak_haversine(self.koordinat[asal][0], self.koordinat[asal][1], 
                                              self.koordinat[tujuan][0], self.koordinat[tujuan][1])
            if not any(node == tujuan for node, _ in self.edges[asal]):
                self.edges[asal].append((tujuan, jarak_km))
                self.edges[tujuan].append((asal, jarak_km))

    def update_koordinat_stasiun(self, nama_stasiun, lat_baru, lon_baru):
        if nama_stasiun in self.koordinat:
            self.koordinat[nama_stasiun] = (float(lat_baru), float(lon_baru))
            for asal, tetanggas in list(self.edges.items()):
                for i, (tujuan, _) in enumerate(tetanggas):
                    jarak_baru = hitung_jarak_haversine(self.koordinat[asal][0], self.koordinat[asal][1], 
                                                       self.koordinat[tujuan][0], self.koordinat[tujuan][1])
                    self.edges[asal][i] = (tujuan, jarak_baru)

    def hapus_rute(self, asal, tujuan):
        if asal in self.edges:
            self.edges[asal] = [item for item in self.edges[asal] if item[0] != tujuan]
        if tujuan in self.edges:
            self.edges[tujuan] = [item for item in self.edges[tujuan] if item[0] != asal]


# --- 3. DATA DEFAULT KOTA BESAR INDONESIA ---
if "graph_kereta" not in st.session_state:
    geo_graph = GraphKeretaOtomatis()
    stasiun_indonesia = [
        ("Jakarta", -6.1751, 106.8272), ("Bandung", -6.9175, 107.6191),
        ("Cirebon", -6.7320, 108.5555), ("Semarang", -6.9667, 110.4167),
        ("Yogyakarta", -7.7956, 110.3695), ("Surabaya", -7.2575, 112.7521),
        ("Malang", -7.9839, 112.6214), ("Banyuwangi", -8.2192, 114.3692),
        ("Medan", 3.5952, 98.6722), ("Palembang", -2.9909, 104.7567),
        ("Makassar", -5.1476, 119.4327)
    ]
    for nama, lat, lon in stasiun_indonesia:
        geo_graph.tambah_stasiun(nama, lat, lon)
        
    rute_default = [
        ("Jakarta", "Bandung"), ("Jakarta", "Cirebon"), ("Bandung", "Cirebon"),
        ("Bandung", "Yogyakarta"), ("Cirebon", "Semarang"), ("Semarang", "Yogyakarta"),
        ("Semarang", "Surabaya"), ("Yogyakarta", "Surabaya"), ("Surabaya", "Malang"),
        ("Surabaya", "Banyuwangi"), ("Jakarta", "Palembang"), ("Banyuwangi", "Makassar")
    ]
    for asal_st, tujuan_st in rute_default:
        geo_graph.tambah_rute_otomatis(asal_st, tujuan_st)
    st.session_state.graph_kereta = geo_graph

graph = st.session_state.graph_kereta

# --- 4. PEMBUATAN MENU UTAMA TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎫 Cari Rute & Beli Tiket", "🗺️ Jaringan Rel & Koordinat", "⚙️ CRUD Panel Otomatis", "📊 Statistik Jaringan", "📋 Dev Log"
])

# ==================== MENU 1: CARI RUTE & ESTIMASI TIKET ====================
with tab1:
    st.subheader("🌸 Temukan Perjalanan & Estimasi Tiket Anda")
    daftar_stasiun = sorted(list(graph.nodes))

    if len(daftar_stasiun) < 2:
        st.info("Tambahkan stasiun terlebih dahulu.")
    else:
        col_asal, col_tujuan, col_jumlah = st.columns([2, 2, 1])
        with col_asal:
            st_asal = st.selectbox("Stasiun Berangkat:", daftar_stasiun, key="asal_s")
        with col_tujuan:
            st_tujuan = st.selectbox("Stasiun Tujuan:", daftar_stasiun, index=len(daftar_stasiun)-1, key="tujuan_s")
        with col_jumlah:
            jumlah_tiket = st.number_input("Jumlah Penumpang:", min_value=1, value=1, step=1)

        if st.button("Mulai Analisis Perjalanan", type="primary"):
            if st_asal == st_tujuan:
                st.warning("Stasiun asal dan tujuan tidak boleh sama!")
            else:
                # Dijkstra Logic
                queue = [(0, st_asal)]
                dist = {n: float("inf") for n in graph.nodes}
                dist[st_asal] = 0
                prev = {n: None for n in graph.nodes}

                while queue:
                    d, curr = heapq.heappop(queue)
                    if curr == st_tujuan: break
                    if d > dist[curr]: continue
                    for neighbor, weight in graph.edges.get(curr, []):
                        new_dist = d + weight
                        if new_dist < dist[neighbor]:
                            dist[neighbor] = new_dist
                            prev[neighbor] = curr
                            heapq.heappush(queue, (new_dist, neighbor))

                path = []
                temp = st_tujuan
                while temp:
                    path.append(temp)
                    temp = prev[temp]
                path.reverse()

                total_jarak = dist[st_tujuan]

                if total_jarak == float("inf"):
                    st.error("Jalur kereta tidak terhubung untuk kedua kota tersebut.")
                else:
                    st.balloons()
                    st.success(f"🎉 Analisis Selesai! Berhasil Menemukan Jalur Terbaik.")
                    
                    # Tampilkan Urutan Rute
                    st.markdown("### 🔀 Alur Lintasan Stasiun:")
                    st.info(" ➔ ".join([f"**{s}**" for s in path]))
                    
                    # Hitung Estimasi Waktu (Kecepatan rata-rata 80 KM/jam)
                    waktu_jam = total_jarak / 80
                    jam = int(waktu_jam)
                    menit = int((waktu_jam - jam) * 60)
                    
                    # Layout Informasi Hasil & Tarif Kelas Tiket
                    c_res1, c_res2 = st.columns([1, 2])
                    with c_res1:
                        st.markdown("### 📏 Info Perjalanan:")
                        st.metric(label="Total Jarak Tempuh", value=f"{total_jarak} KM")
                        st.metric(label="Estimasi Waktu Tempuh", value=f"{jam} Jam {menit} Menit")
                        
                    with c_res2:
                        st.markdown("### 🎫 Pilihan Kelas & Estimasi Total Harga Tiket:")
                        
                        # Rumus Tarif per Kelas
                        harga_ekonomi = total_jarak * 500 * jumlah_tiket
                        harga_bisnis = total_jarak * 1000 * jumlah_tiket
                        harga_eksekutif = total_jarak * 2000 * jumlah_tiket
                        
                        st.write(f"🟢 **Kelas Ekonomi:** Rp {harga_ekonomi:,} *({jumlah_tiket} Penumpang)*")
                        st.write(f"🔵 **Kelas Bisnis:** Rp {harga_bisnis:,} *({jumlah_tiket} Penumpang)*")
                        st.write(f"🔴 **Kelas Eksekutif:** Rp {harga_eksekutif:,} *({jumlah_tiket} Penumpang)*")
                        st.caption("ℹ️ Tarif dasar: Ekonomi Rp500/km, Bisnis Rp1.000/km, Eksekutif Rp2.000/km.")

# ==================== MENU 2: JARINGAN REL & KOORDINAT ====================
with tab2:
    st.subheader("🗺️ Jaringan Rel Aktif & Basis Data Koordinat GPS")
    col_tabel1, col_tabel2 = st.columns([2, 3])
    with col_tabel1:
        st.write("#### 📍 Posisi Koordinat Stasiun")
        data_koor = [{"Stasiun": k, "Latitude": v[0], "Longitude": v[1]} for k, v in sorted(graph.koordinat.items())]
        st.dataframe(data_koor, use_container_width=True)
    with col_tabel2:
        st.write("#### 🛤️ Hubungan Rel Aktif (Hasil Hitung Otomatis)")
        data_j = []
        for s, t_list in graph.edges.items():
            for t, j in t_list:
                if (t, s, j) not in data_j: data_j.append((s, t, j))
        for i, (a, b, j) in enumerate(sorted(data_j)):
            st.write(f"🌸 **{a}** ↔️ **{b}** ➔ **{j} KM**")

# ==================== MENU 3: CRUD PANEL OTOMATIS ====================
with tab3:
    st.subheader("⚙️ Pusat Kendali Data Otomatis (Koordinat CRUD)")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### ➕ 1. Tambah Rute / Stasiun")
        new_asal = st.text_input("Nama Stasiun A:", value="Solo", key="na")
        lat_a = st.number_input("Latitude A:", value=-7.5667, format="%.4f", key="la")
        lon_a = st.number_input("Longitude A:", value=110.8167, format="%.4f", key="lo_a")
        new_tujuan = st.text_input("Nama Stasiun B:", value="Semarang", key="nb")
        lat_b = st.number_input("Latitude B:", value=-6.9667, format="%.4f", key="lb")
        lon_b = st.number_input("Longitude B:", value=110.4167, format="%.4f", key="lo_b")
        if st.button("Simpan & Sambungkan Otomatis"):
            graph.tambah_stasiun(new_asal, lat_a, lon_a)
            graph.tambah_stasiun(new_tujuan, lat_b, lon_b)
            graph.tambah_rute_otomatis(new_asal, new_tujuan)
            st.success("Stasiun disimpan dan jarak KM berhasil dihitung otomatis!")
            st.rerun()
    with c2:
        st.markdown("### 📝 2. Update Koordinat")
        stasiun_pilihan = st.selectbox("Pilih Stasiun:", sorted(list(graph.nodes)), key="sb_u")
        lat_update = st.number_input("Latitude Baru:", value=graph.koordinat[stasiun_pilihan][0] if list(graph.nodes) else 0.0, format="%.4f")
        lon_update = st.number_input("Longitude Baru:", value=graph.koordinat[stasiun_pilihan][1] if list(graph.nodes) else 0.0, format="%.4f")
        if st.button("Perbarui Posisi & Rekalkulasi"):
            graph.update_koordinat_stasiun(stasiun_pilihan, lat_update, lon_update)
            st.success(f"Koordinat {stasiun_pilihan} diubah, seluruh rute dikalkulasi ulang!")
            st.rerun()
    with c3:
        st.markdown("### 🗑️ 3. Hapus Jalur")
        current_routes = []
        for s, t_list in graph.edges.items():
            for t, j in t_list:
                if (t, s, j) not in current_routes: current_routes.append((s, t, j))
        if current_routes:
            d_opsi = [f"{a} ↔️ {t}" for a, t, j in sorted(current_routes)]
            d_sel = st.selectbox("Pilih Rute yang Ingin Dihapus:", d_opsi, key="ds")
            if st.button("Eksekusi Hapus Jalur"):
                a_d, t_d = d_sel.split(" ↔️ ")
                graph.hapus_rute(a_d, t_d)
                st.success("Jalur rel berhasil diputus!")
                st.rerun()

# ==================== MENU 4: ANALISIS STATISTIK ====================
with tab4:
    st.subheader("📊 Analisis Jaringan Pink")
    stats = {k: len(v) for k, v in graph.edges.items()}
    if stats:
        st.bar_chart(stats)
        st.dataframe([{"Stasiun": k, "Koneksi": v} for k, v in stats.items()], use_container_width=True)

# ==================== MENU 5: DEV LOG ====================
with tab5:
    st.subheader("📋 JSON Graph Data")
    st.json(graph.edges)
