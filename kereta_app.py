import heapq
import streamlit as st

# --- 1. PENGATURAN HALAMAN UTAMA ---
st.set_page_config(layout="wide", page_title="Sistem Navigasi Rute Kereta")
st.title("🚇 Aplikasi Pencari Rute Terpendek Kereta Api")
st.write("Implementasi Struktur Data **Graph (Adjacency List)** dan **Algoritma Dijkstra**")
st.markdown("---")


# --- 2. STRUKTUR DATA GRAPH ---
class GraphKereta:

    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def tambah_stasiun(self, nama_stasiun):
        nama_stasiun = nama_stasiun.strip()
        if nama_stasiun:
            self.nodes.add(nama_stasiun)
            if nama_stasiun not in self.edges:
                self.edges[nama_stasiun] = []

    def tambah_rute(self, asal, tujuan, jarak_km):
        asal = asal.strip()
        tujuan = tujuan.strip()
        if asal and tujuan and asal != tujuan:
            self.tambah_stasiun(asal)
            self.tambah_stasiun(tujuan)
            # Mencegah duplikasi rute yang persis sama
            if not any(node == tujuan for node, _ in self.edges[asal]):
                self.edges[asal].append((tujuan, jarak_km))
                self.edges[tujuan].append((asal, jarak_km))

    def hapus_rute(self, asal, tujuan):
        # Menghapus jalur dari asal ke tujuan
        if asal in self.edges:
            self.edges[asal] = [item for item in self.edges[asal] if item[0] != tujuan]
        # Menghapus jalur dari tujuan ke asal (karena Undirected Graph)
        if tujuan in self.edges:
            self.edges[tujuan] = [item for item in self.edges[tujuan] if item[0] != asal]


# --- 3. DATA DEFAULT (SESSION STATE) ---
if "graph_kereta" not in st.session_state:
    geo_graph = GraphKereta()
    rute_nasional = [
        # === JALUR TRANS-JAWA ===
        ("Jakarta", "Bandung", 150),
        ("Jakarta", "Cirebon", 210),
        ("Bandung", "Cirebon", 130),
        ("Bandung", "Yogyakarta", 400),
        ("Cirebon", "Semarang", 230),
        ("Semarang", "Yogyakarta", 120),
        ("Semarang", "Surabaya", 350),
        ("Yogyakarta", "Surabaya", 330),
        ("Surabaya", "Malang", 90),
        ("Yogyakarta", "Malang", 390),
        ("Surabaya", "Banyuwangi", 290),
        
        # === JALUR TRANS-SUMATERA ===
        ("Medan", "Binjai", 22),
        ("Medan", "Rantau Prapat", 260),
        ("Padang", "Pariaman", 60),
        ("Palembang", "Prabumulih", 78),
        ("Prabumulih", "Lubuklinggau", 224),
        ("Palembang", "Tanjung Karang Lampung", 389),
        
        # === JALUR TRANS-SULAWESI ===
        ("Makassar", "Maros", 30),
        ("Maros", "Barru", 41),
        ("Barru", "Parepare", 74),
        
        # === SIMULASI KONEKSI INTEGRASI MARITIM ===
        ("Banyuwangi", "Makassar", 820),
        ("Jakarta", "Palembang", 450)
    ]
    for asal_st, tujuan_st, jarak_st in rute_nasional:
        geo_graph.tambah_rute(asal_st, tujuan_st, jarak_st)
    st.session_state.graph_kereta = geo_graph

graph = st.session_state.graph_kereta

# --- 4. PEMBUATAN 4 MENU UTAMA (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Cari Rute Terpendek", 
    "🗺️ Jaringan Rel Aktif", 
    "⚙️ Kelola Peta Jaringan", 
    "📋 Log & Status Graph"
])

# ==================== MENU 1: CARI RUTE ====================
with tab1:
    st.subheader("🔍 Parameter Pencarian Lintasan Terpendek")
    daftar_stasiun = sorted(list(graph.nodes))

    if len(daftar_stasiun) < 2:
        st.info("Silakan tambahkan data stasiun terlebih dahulu di menu Kelola Peta Jaringan.")
    else:
        col_asal, col_tujuan = st.columns(2)
        with col_asal:
            stasiun_asal = st.selectbox("Pilih Stasiun Asal:", daftar_stasiun, index=0, key="asal_select")
        with col_tujuan:
            stasiun_tujuan = st.selectbox("Pilih Stasiun Tujuan:", daftar_stasiun, index=len(daftar_stasiun) - 1, key="tujuan_select")

        tombol_cari = st.button("Hitung Rute Terbaik", type="primary")

        if tombol_cari:
            if stasiun_asal == stasiun_tujuan:
                st.warning("Stasiun asal dan tujuan tidak boleh sama!")
            else:
                queue = [(0, stasiun_asal)]
                jarak_terpendek = {node: float("inf") for node in graph.nodes}
                jarak_terpendek[stasiun_asal] = 0
                rute_sebelumnya = {node: None for node in graph.nodes}

                while queue:
                    jarak_sekarang, stasiun_sekarang = heapq.heappop(queue)

                    if stasiun_sekarang == stasiun_tujuan:
                        break

                    if jarak_sekarang > jarak_terpendek[stasiun_sekarang]:
                        continue

                    for tetangga, jarak_ke_tetangga in graph.edges.get(stasiun_sekarang, []):
                        total_jarak_baru = jarak_sekarang + jarak_ke_tetangga

                        if total_jarak_baru < jarak_terpendek[tetangga]:
                            jarak_terpendek[tetangga] = total_jarak_baru
                            rute_sebelumnya[tetangga] = stasiun_sekarang
                            heapq.heappush(queue, (total_jarak_baru, tetangga))

                jalur = []
                stasiun_aktif = stasiun_tujuan
                while stasiun_aktif is not None:
                    jalur.append(stasiun_aktif)
                    stasiun_aktif = rute_sebelumnya[stasiun_aktif]
                jalur.reverse()

                total_jarak = jarak_terpendek[stasiun_tujuan]

                if total_jarak == float("inf"):
                    st.error("Tidak ada rel penghubung antara kedua stasiun tersebut.")
                else:
                    st.success("🎉 Rute Terbaik Berhasil Ditemukan!")
                    panah_rute = " ➔ ".join([f"**{st}**" for st in jalur])
                    
                    c_hasil1, c_hasil2 = st.columns([2, 1])
                    with c_hasil1:
                        st.markdown("### 🔀 Jalur Lintasan yang Dilewati:")
                        st.info(panah_rute)
                    with c_hasil2:
                        st.markdown("### 📏 Total Jarak:")
                        st.metric(label="Hasil Akumulasi", value=f"{total_jarak} KM")

# ==================== MENU 2: JARINGAN REL ====================
with tab2:
    st.subheader("🗺️ Daftar Seluruh Jaringan Rel Kereta Aktif")
    st.write("Daftar koneksi antar stasiun yang saat ini dapat dilewati oleh sistem kereta api:")
    
    data_jalur = []
    for st_asal, tetanggas in graph.edges.items():
        for st_tujuan, jarak in tetanggas:
            if (st_tujuan, st_asal, jarak) not in data_jalur:
                data_jalur.append((st_asal, st_tujuan, jarak))

    if not data_jalur:
        st.info("Tidak ada rute kereta aktif saat ini.")
    else:
        col_rel1, col_rel2 = st.columns(2)
        for i, (asal_p, tujuan_p, jarak_p) in enumerate(sorted(data_jalur)):
            if i % 2 == 0:
                with col_rel1:
                    st.write(f"• **{asal_p}** ↔️ **{tujuan_p}** ({jarak_p} km)")
            else:
                with col_rel2:
                    st.write(f"• **{asal_p}** ↔️ **{tujuan_p}** ({jarak_p} km)")

# ==================== MENU 3: KELOLA PETA ====================
with tab3:
    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        st.subheader("➕ Tambah Hubungan Rel Baru")
        input_asal = st.text_input("Nama Kota/Stasiun Asal Baru:")
        input_tujuan = st.text_input("Nama Kota/Stasiun Tujuan Baru:")
        input_jarak = st.number_input("Jarak Antar Kota (KM):", min_value=1, value=50, step=1)
        
        if st.button("Simpan Data Rute", type="primary"):
            if not input_asal or not input_tujuan:
                st.error("Form input stasiun tidak boleh kosong!")
            elif input_asal.strip().lower() == input_tujuan.strip().lower():
                st.error("Stasiun asal dan tujuan tidak boleh sama!")
            else:
                graph.tambah_rute(input_asal, input_tujuan, input_jarak)
                st.success(f"Berhasil menyambungkan {input_asal.strip()} ↔️ {input_tujuan.strip()} ({input_jarak} km)!")
                st.rerun()
                
    with col_in2:
        st.subheader("🗑️ Hapus Jalur Kereta")
        st.write("Putuskan jalur rel tertentu secara permanen dari sistem jaringan.")
        
        # Ambil daftar rute unik untuk menu dropdown hapus
        rute_untuk_dihapus = []
        for st_asal, tetanggas in graph.edges.items():
            for st_tujuan, jarak in tetanggas:
                if (st_tujuan, st_asal) not in rute_untuk_dihapus:
                    rute_untuk_dihapus.append((st_asal, st_tujuan))
                    
        if not rute_untuk_dihapus:
            st.info("Tidak ada rute yang bisa dihapus.")
        else:
            opsi_hapus = [f"{a} ↔️ {t}" for a, t in sorted(rute_untuk_dihapus)]
            pilihan_hapus = st.selectbox("Pilih Jalur Rel yang Ingin Dihapus:", opsi_hapus)
            
            if st.button("Hapus Jalur Ini", type="secondary"):
                # Memilah kembali teks pilihan menjadi stasiun asal dan tujuan asli
                idx = opsi_hapus.index(pilihan_hapus)
                st_asal_hapus, st_tujuan_hapus = sorted(rute_untuk_dihapus)[idx]
                
                graph.hapus_rute(st_asal_hapus, st_tujuan_hapus)
                st.success(f"Jalur rel {st_asal_hapus} ↔️ {st_tujuan_hapus} berhasil dihapus dari sistem!")
                st.rerun()
