import streamlit as st
import heapq


# --- 1. PENGATURAN HALAMAN STREAMLIT ---
st.set_page_config(layout="wide", page_title="Navigasi Rute Kereta Api")


# --- 2. INISIALISASI STRUKTUR DATA GRAPH ---
class GraphKereta:

    def __init__(self):
        # Graph direpresentasikan sebagai Adjacency List (Daftar Ketetanggaan)
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
            # Mencegah duplikasi rute yang memiliki kota asal dan tujuan sama
            if not any(node == tujuan for node, _ in self.edges[asal]):
                self.edges[asal].append((tujuan, jarak_km))
                self.edges[tujuan].append((asal, jarak_km))

    # --- 3. IMPLEMENTASI ALGORITMA DIJKSTRA ---
    def cari_rute_terpendek(self, asal, tujuan):
        queue = [(0, asal)]
        jarak_terpendek = {node: float("inf") for node in self.nodes}
        jarak_terpendek[asal] = 0
        rute_sebelumnya = {node: None for node in self.nodes}

        while queue:
            jarak_sekarang, stasiun_sekarang = heapq.heappop(queue)

            if stasiun_sekarang == tujuan:
                break

            if jarak_sekarang > jarak_terpendek[stasiun_sekarang]:
                continue

            for tetangga, jarak_ke_tetangga in self.edges.get(
                stasiun_sekarang, []
            ):
                total_jarak_baru = jarak_sekarang + jarak_ke_tetangga

                if total_jarak_baru < jarak_terpendek[tetangga]:
                    jarak_terpendek[tetangga] = total_jarak_baru
                    rute_sebelumnya[tetangga] = stasiun_sekarang
                    heapq.heappush(queue, (total_jarak_baru, tetangga))

        jalur = []
        stasiun_aktif = tujuan
        while stasiun_aktif is not None:
            jalur.append(stasiun_aktif)
            stasiun_aktif = rute_sebelumnya[stasiun_aktif]
        jalur.reverse()

        return jarak_terpendek[tujuan], jalur


# --- 4. INISIALISASI DATA DI DALAM SESSION STATE ---
if "graph_kereta" not in st.session_state:
    geo_graph = GraphKereta()
    # Data Default Jaringan Kereta Api Pulau Jawa
    rute_default = [
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
    ]
    for asal_st, tujuan_st, jarak_st in rute_default:
        geo_graph.tambah_rute(asal_st, tujuan_st, jarak_st)
    st.session_state.graph_kereta = geo_graph

graph = st.session_state.graph_kereta

# --- 5. PEMBUATAN MENU UTAMA DI SIDEBAR ---
with st.sidebar:
    st.title("🧭 Menu Navigasi")
    pilihan_menu = st.radio(
        "Pilih Halaman:",
        [
            "📍 Cari Rute Terpendek",
            "⚙️ Kelola Jaringan Peta",
            "📋 Informasi Algoritma",
        ],
    )
    st.markdown("---")
    st.caption("Proyek Akhir Struktur Data • Kategori: Bintang 3")

# ==================== PILIHAN MENU 1: CARI RUTE ====================
if pilihan_menu == "📍 Cari Rute Terpendek":
    st.title("🚇 Aplikasi Pencari Rute Terpendek Kereta Api")
    st.write("Temukan jalur kereta api tercepat menggunakan efisiensi algoritma.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Tentukan Tujuan Perjalanan")
        daftar_stasiun = sorted(list(graph.nodes))

        if len(daftar_stasiun) < 2:
            st.info("Peta kosong. Silakan tambahkan stasiun di menu Kelola Jaringan Peta.")
        else:
            stasiun_asal = st.selectbox("Pilih Stasiun Asal:", daftar_stasiun, index=0)
            stasiun_tujuan = st.selectbox(
                "Pilih Stasiun Tujuan:",
                daftar_stasiun,
                index=len(daftar_stasiun) - 1,
            )

            tombol_cari = st.button("Cari Rute Terbaik", type="primary")

            if tombol_cari:
                if stasiun_asal == stasiun_tujuan:
                    st.warning("Stasiun asal and tujuan tidak boleh sama!")
                else:
                    total_jarak, rute_terlewati = graph.cari_rute_terpendek(
                        stasiun_asal, stasiun_tujuan
                    )

                    if total_jarak == float("inf"):
                        st.error(
                            f"Maaf, tidak ada jalur kereta yang menghubungkan {stasiun_asal} dan {stasiun_tujuan}."
                        )
                    else:
                        st.success("🎉 Rute Terbaik Berhasil Ditemukan!")
                        panah_rute = " ➔ ".join(
                            [f"**{stasiun}**" for stasiun in rute_terlewati]
                        )
                        st.markdown("### 🔀 Rute yang Harus Dilewati:")
                        st.info(panah_rute)

                        st.markdown("### 📏 Total Jarak Tempuh:")
                        st.metric(label="Jarak Kumulatif", value=f"{total_jarak} KM")

    with col2:
        st.subheader("🗺️ Daftar Semua Jalur Kereta yang Tersedia")
        data_jalur = []
        for st_asal, tetanggas in graph.edges.items():
            for st_tujuan, jarak in tetanggas:
                if (st_tujuan, st_asal, jarak) not in data_jalur:
                    data_jalur.append((st_asal, st_tujuan, jarak))

        for asal_p, tujuan_p, jarak_p in sorted(data_jalur):
            st.write(f"- **{asal_p}** ↔️ **{tujuan_p}** ({jarak_p} km)")

# ==================== PILIHAN MENU 2: KELOLA PETA ====================
elif pilihan_menu == "⚙️ Kelola Jaringan Peta":
    st.title("⚙️ Panel Manajemen Jaringan Peta Kereta Api")
    st.write(
        "Tambahkan stasiun baru atau hubungkan rel antar kota secara dinamis ke dalam Graph."
    )
    st.markdown("---")

    kolom_input1, kolom_input2 = st.columns(2)

    with kolom_input1:
        st.subheader("➕ Tambahkan Jalur Baru")
        input_asal = st.text_input("Nama Stasiun Asal Baru:")
        input_tujuan = st.text_input("Nama Stasiun Tujuan Baru:")
        input_jarak = st.number_input(
            "Jarak Rel Kereta (KM):", min_value=1, value=50, step=1
        )

        if st.button("Simpan Hubungan Rute Baru", type="primary"):
            if not input_asal or not input_tujuan:
                st.error("Nama stasiun asal dan tujuan tidak boleh kosong!")
            elif input_asal.strip().lower() == input_tujuan.strip().lower():
                st.error("Nama stasiun asal dan tujuan tidak boleh sama!")
            else:
                graph.tambah_rute(input_asal, input_tujuan, input_jarak)
                st.success(
                    f"Berhasil menambahkan rute baru: {input_asal.strip()} ↔️ {input_tujuan.strip()} ({input_jarak} km)"
                )
                st.rerun()

    with kolom_input2:
        st.subheader("📋 Status Log Database Graph")
        st.write(f"• Total Stasiun Terdaftar (*Nodes*): **{len(graph.nodes)} Kota**")
        
        total_koneksi = sum(len(jalur) for jalur in graph.edges.values()) // 2
        st.write(f"• Total Rel Penghubung (*Edges*): **{total_koneksi} Jalur**")
        
        st.markdown("""
        ### 💡 Petunjuk Pengujian Dosen:
        1. Ketik stasiun baru di kolom kiri (Misal Asal: `Surabaya`, Tujuan: `Banyuwangi`, Jarak: `290`).
        2. Klik **Simpan Hubungan Rute Baru**.
        3. Pindah ke Menu **📍 Cari Rute Terpendek**, kota baru tersebut akan otomatis masuk ke sistem pencarian rute terbaik!
        """)

# ==================== PILIHAN MENU 3: INFORMASI ALGORITMA ====================
elif pilihan_menu == "📋 Informasi Algoritma":
    st.title("📋 Dokumentasi Sistem & Teori Struktur Data")
    st.write("Penjelasan teknis implementasi proyek untuk kebutuhan presentasi.")
    st.markdown("---")

    st.subheader("1. Representasi Graph (Struktur Data)")
    st.write(
        "Aplikasi ini menggunakan representasi **Adjacency List** berbasis objek `dict` di Python. "
        "Setiap stasiun bertindak sebagai *Node/Vertex*, dan jalur rel kereta bertindak sebagai *Edge* yang memiliki bobot (*weight*) berupa jarak dalam satuan kilometer."
    )

    st.subheader("2. Cara Kerja Algoritma Dijkstra")
    st.markdown(
        """
        Algoritma Dijkstra bekerja dengan prinsip *Greedy* untuk mencari lintasan terpendek dari satu titik awal ke semua titik lainnya:
        1. **Inisialisasi**: Jarak ke stasiun asal diatur `0`, sedangkan jarak ke stasiun lainnya diatur tak terhingga (`inf`).
        2. **Priority Queue (Min-Heap)**: Menggunakan modul `heapq` bawaan Python untuk selalu memilih stasiun dengan bobot akumulatif terkecil untuk dieksplorasi terlebih dahulu secara efisien.
        3. **Relaksasi**: Memeriksa seluruh stasiun tetangga yang terhubung langsung. Jika ditemukan rute baru yang menghasilkan jarak lebih pendek, data di memori akan diperbarui.
        """
        )
