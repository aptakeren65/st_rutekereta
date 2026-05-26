import heapq
import streamlit as st

# --- 1. PENGATURAN HALAMAN UTAMA ---
st.set_page_config(layout="wide", page_title="Sistem Navigasi Rute Kereta")
st.title("🚇 Aplikasi Pencari Rute Terpendek Kereta Api")
st.write("Implementasi Struktur Data **Graph (Adjacency List)** dan **Algoritma Dijkstra**")
st.markdown("---")


# --- 2. STRUKTUR DATA GRAPH (DENGAN OPERASI CRUD) ---
class GraphKereta:

    def __init__(self):
        self.nodes = set()
        self.edges = {}

    # [C]REATE: Menambahkan Stasiun & Rute Baru
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

    # [U]PDATE: Memperbarui Jarak/Bobot Rute yang Sudah Ada
    def update_jarak_rute(self, asal, tujuan, jarak_baru):
        if asal in self.edges:
            self.edges[asal] = [(node, jarak_baru) if node == tujuan else (node, j) for node, j in self.edges[asal]]
        if tujuan in self.edges:
            self.edges[tujuan] = [(node, jarak_baru) if node == asal else (node, j) for node, j in self.edges[tujuan]]

    # [D]ELETE: Menghapus Rute dari Jaringan Graph
    def hapus_rute(self, asal, tujuan):
        if asal in self.edges:
            self.edges[asal] = [item for item in self.edges[asal] if item[0] != tujuan]
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

# --- 4. PEMBUATAN 5 MENU UTAMA (TABS) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Cari Rute Terpendek", 
    "🗺️ Jaringan Rel Aktif", 
    "⚙️ Panel CRUD Peta", 
    "📊 Analisis & Statistik",
    "📋 Log & Status Graph"
])

# ==================== MENU 1: CARI RUTE [R - READ] ====================
with tab1:
    st.subheader("🔍 Parameter Pencarian Lintasan Terpendek")
    daftar_stasiun = sorted(list(graph.nodes))

    if len(daftar_stasiun) < 2:
        st.info("Silakan tambahkan data stasiun terlebih dahulu di menu Panel CRUD Peta.")
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

# ==================== MENU 2: JARINGAN REL [R - READ] ====================
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

# ==================== MENU 3: PANEL MANAGEMENT [C - U - D] ====================
with tab3:
    st.subheader("⚙️ Pusat Operasi Basis Data Jaringan (CRUD)")
    st.write("Kelola penambahan, modifikasi bobot, dan penghapusan relasi rel kereta api secara dinamis.")
    st.markdown("---")
    
    col_c, col_u, col_d = st.columns(3)
    
    # 1. [C]REATE SECTION
    with col_c:
        st.markdown("### ➕ [C]reate Rute")
        input_asal = st.text_input("Nama Stasiun Asal Baru:", key="c_asal")
        input_tujuan = st.text_input("Nama Stasiun Tujuan Baru:", key="c_tujuan")
        input_jarak = st.number_input("Jarak Rel (KM):", min_value=1, value=50, step=1, key="c_jarak")
        
        if st.button("Tambah Rute Baru", type="primary"):
            if not input_asal or not input_tujuan:
                st.error("Nama stasiun tidak boleh kosong!")
            elif input_asal.strip().lower() == input_tujuan.strip().lower():
                st.error("Stasiun asal dan tujuan tidak boleh sama!")
            else:
                graph.tambah_rute(input_asal, input_tujuan, input_jarak)
                st.success(f"Berhasil menambahkan rute {input_asal.strip()} ↔️ {input_tujuan.strip()}!")
                st.rerun()

    # Ekstraksi rute yang ada untuk fitur Update & Delete
    rute_tersedia = []
    for st_asal, tetanggas in graph.edges.items():
        for st_tujuan, jarak in tetanggas:
            if (st_tujuan, st_asal, jarak) not in rute_tersedia:
                rute_tersedia.append((st_asal, st_tujuan, jarak))
    
    # 2. [U]PDATE SECTION
    with col_u:
        st.markdown("### 📝 [U]pdate Jarak")
        if not rute_tersedia:
            st.info("Tidak ada rute untuk diubah.")
        else:
            opsi_update = [f"{a} ↔️ {t} ({j} km)" for a, t, j in sorted(rute_tersedia)]
            pilihan_update = st.selectbox("Pilih Jalur yang Ingin Diubah:", opsi_update, key="u_select")
            jarak_baru = st.number_input("Masukkan Jarak Baru (KM):", min_value=1, value=100, step=1, key="u_jarak")
            
            if st.button("Perbarui Jarak Rel", type="secondary"):
                idx_u = opsi_update.index(pilihan_update)
                st_asal_u, st_tujuan_u, _ = sorted(rute_tersedia)[idx_u]
                graph.update_jarak_rute(st_asal_u, st_tujuan_u, jarak_baru)
                st.success(f"Jarak rute {st_asal_u} ↔️ {st_tujuan_u} diperbarui menjadi {jarak_baru} KM!")
                st.rerun()

    # 3. [D]ELETE SECTION
    with col_d:
        st.markdown("### 🗑️ [D]elete Rute")
        if not rute_tersedia:
            st.info("Tidak ada rute yang bisa dihapus.")
        else:
            opsi_hapus = [f"{a} ↔️ {t}" for a, t, _ in sorted(rute_tersedia)]
            pilihan_hapus = st.selectbox("Pilih Jalur yang Ingin Dihapus:", opsi_hapus, key="d_select")
            
            if st.button("Hapus Jalur Ini"):
                idx_d = opsi_hapus.index(pilihan_hapus)
                st_asal_d, st_tujuan_d, _ = sorted(rute_tersedia)[idx_d]
                graph.hapus_rute(st_asal_d, st_tujuan_d)
                st.success(f"Jalur {st_asal_d} ↔️ {st_tujuan_d} berhasil diputus!")
                st.rerun()

# ==================== MENU 4: ANALISIS & STATISTIK ====================
with tab4:
    st.subheader("📊 Analisis Konektivitas Stasiun (*Centrality*)")
    st.write("Analisis stasiun mana yang paling krusial dan memiliki percabangan rute terbanyak di Indonesia.")
    
    statistik_koneksi = {stasiun: len(jalur) for stasiun, jalur in graph.edges.items()}
    
    if not statistik_koneksi:
        st.info("Data Graph kosong, tidak ada statistik yang bisa dianalisis.")
    else:
        stasiun_terpadat = max(statistik_koneksi, key=statistik_koneksi.get)
        jumlah_koneksi_maks = statistik_koneksi[stasiun_terpadat]
        
        st.info(f"🏆 **Stasiun Utama / Hub Terpadat Saat Ini:** Stasiun **{stasiun_terpadat}** dengan total **{jumlah_koneksi_maks} jalur** percabangan.")
        st.markdown("---")
        
        col_grafik1, col_grafik2 = st.columns([1, 1])
        
        with col_grafik1:
            st.write("#### 📈 Grafik Jumlah Percabangan Rel per Stasiun")
            st.bar_chart(statistik_koneksi)
            
        with col_grafik2:
            st.write("#### 📋 Tabel Detail Frekuensi Jalur")
            tabel_data = [{"Stasiun / Kota": k, "Jumlah Rute Terhubung": v} for k, v in sorted(statistik_koneksi.items(), key=lambda x: x[1], reverse=True)]
            st.dataframe(tabel_data, use_container_width=True)

# ==================== MENU 5: LOG GRAPH ====================
with tab5:
    st.subheader("📋 Status Teknis Algoritma & Struktur Data")
    st.write("Informasi ukuran matriks/list dari objek Graph di memori aplikasi saat ini:")
    
    c_box1, c_box2 = st.columns(2)
    with c_box1:
        st.metric(label="Total Simpul (Nodes / Vertices)", value=f"{len(graph.nodes)} Stasiun")
    with c_box2:
        total_koneksi = sum(len(j) for j in graph.edges.values()) // 2
        st.metric(label="Total Sisi (Edges / Jalur Rel)", value=f"{total_koneksi} Hubungan")
        
    st.markdown("---")
    st.markdown("### 🔍 Struktur Adjacency List (Raw Python Dictionary)")
    st.write("Dosen dapat melihat representasi asli struktur data di memori melalui objek dictionary di bawah ini:")
    st.json(graph.edges)
