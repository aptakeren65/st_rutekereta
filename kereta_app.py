import heapq
import streamlit as st

# --- 1. PENGATURAN HALAMAN & TEMA WARNA PINK (CSS INJECTION) ---
st.set_page_config(layout="wide", page_title="Sistem Navigasi Kereta Pink Edition")

# Injeksi CSS Custom untuk Tema Pink
st.markdown(
    """
    <style>
    /* 1. Latar Belakang Halaman Utama (Soft Pink) */
    .stApp {
        background-color: #fff0f6;
    }
    
    /* 2. Warna Judul dan Teks Utama (Deep Pink / Rose) */
    h1, h2, h3, h4 {
        color: #d63384 !important;
    }
    
    p, b, span {
        color: #495057;
    }

    /* 3. Desain Kartu pada Tabs (White with Pink Border) */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #fcc2d7;
        box-shadow: 0 10px 15px rgba(214, 51, 132, 0.05);
        margin-top: 15px;
    }

    /* 4. Styling Tab Menu agar berwarna Pink saat aktif */
    button[data-baseweb="tab"] {
        font-size: 18px;
        font-weight: bold;
    }
    
    button[aria-selected="true"] {
        color: #d63384 !important;
        border-bottom-color: #d63384 !important;
    }

    /* 5. Custom Button (Pink Gradient) */
    .stButton>button {
        background-color: #ff85a1;
        color: white !important;
        border-radius: 12px;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #d63384;
        border: none;
        color: white !important;
    }
    
    /* 6. Info & Success Box Custom Color */
    .stAlert {
        border-radius: 15px;
        border: 1px solid #fcc2d7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚇 Train Route Planner ")
st.write("Navigasi Jalur Kereta Api Indonesia dengan **Algoritma Dijkstra**")
st.markdown("---")


# --- 2. STRUKTUR DATA GRAPH (DENGAN OPERASI CRUD) ---
class GraphKereta:

    def __init__(self):
        self.nodes = set()
        self.edges = {}

    # [C]REATE
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
            if not any(node == tujuan for node, _ in self.edges[asal]):
                self.edges[asal].append((tujuan, jarak_km))
                self.edges[tujuan].append((asal, jarak_km))

    # [U]PDATE
    def update_jarak_rute(self, asal, tujuan, jarak_baru):
        if asal in self.edges:
            self.edges[asal] = [(node, jarak_baru) if node == tujuan else (node, j) for node, j in self.edges[asal]]
        if tujuan in self.edges:
            self.edges[tujuan] = [(node, jarak_baru) if node == asal else (node, j) for node, j in self.edges[tujuan]]

    # [D]ELETE
    def hapus_rute(self, asal, tujuan):
        if asal in self.edges:
            self.edges[asal] = [item for item in self.edges[asal] if item[0] != tujuan]
        if tujuan in self.edges:
            self.edges[tujuan] = [item for item in self.edges[tujuan] if item[0] != asal]


# --- 3. DATA DEFAULT (SIMULASI JALUR INDONESIA) ---
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

# --- 4. PEMBUATAN 5 MENU UTAMA (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Cari Rute", "🗺️ Jaringan Rel", "⚙️ CRUD Panel", "📊 Statistik"
])

# ==================== MENU 1: CARI RUTE ====================
with tab1:
    st.subheader("🔍 Temukan Perjalanan Terpendek")
    daftar_stasiun = sorted(list(graph.nodes))

    if len(daftar_stasiun) < 2:
        st.info("Tambahkan stasiun terlebih dahulu.")
    else:
        col_asal, col_tujuan = st.columns(2)
        with col_asal:
            st_asal = st.selectbox("Titik Berangkat:", daftar_stasiun, key="asal_s")
        with col_tujuan:
            st_tujuan = st.selectbox("Titik Tiba:", daftar_stasiun, index=len(daftar_stasiun)-1, key="tujuan_s")

        if st.button("Mulai Hitung Rute", type="primary"):
            if st_asal == st_tujuan:
                st.warning("Asal dan tujuan tidak boleh sama!")
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

                if dist[st_tujuan] == float("inf"):
                    st.error("Jalur tidak terhubung.")
                else:
                    st.balloons()
                    st.success(f"🎉Rute terbaik ditemukan! Total Jarak: {dist[st_tujuan]} KM")
                    st.info(" ➔ ".join([f"**{s}**" for s in path]))

# ==================== MENU 2: JARINGAN REL ====================
with tab2:
    st.subheader("🗺️ Daftar Rel Aktif")
    data_j = []
    for s, t_list in graph.edges.items():
        for t, j in t_list:
            if (t, s, j) not in data_j: data_j.append((s, t, j))
    
    col_a, col_b = st.columns(2)
    for i, (a, b, j) in enumerate(sorted(data_j)):
        target_col = col_a if i % 2 == 0 else col_b
        target_col.write(f"🚇 **{a}** ↔️ **{b}** ({j} km)")

# ==================== MENU 3: CRUD PANEL ====================
with tab3:
    st.subheader("⚙️ Pusat Kendali Data (Pink CRUD)")
    c1, c2, c3 = st.columns(3)
    
    # Create
    with c1:
        st.markdown("### ➕ Tambah")
        in_a = st.text_input("Asal:", key="ca")
        in_b = st.text_input("Tujuan:", key="cb")
        in_j = st.number_input("Jarak (KM):", min_value=1, value=10, key="cj")
        if st.button("Simpan Baru"):
            graph.tambah_rute(in_a, in_b, in_j)
            st.rerun()

    # Get rute for U & D
    current_routes = []
    for s, t_list in graph.edges.items():
        for t, j in t_list:
            if (t, s, j) not in current_routes: current_routes.append((s, t, j))

    # Update
    with c2:
        st.markdown("### 📝 Update")
        if current_routes:
            u_opsi = [f"{a}-{t}" for a, t, j in sorted(current_routes)]
            u_sel = st.selectbox("Pilih Rute:", u_opsi, key="us")
            u_j = st.number_input("Jarak Baru:", min_value=1, key="uj")
            if st.button("Update Jarak"):
                a_u, t_u = u_sel.split("-")
                graph.update_jarak_rute(a_u, t_u, u_j)
                st.rerun()

    # Delete
    with c3:
        st.markdown("### 🗑️ Hapus")
        if current_routes:
            d_opsi = [f"{a}-{t}" for a, t, j in sorted(current_routes)]
            d_sel = st.selectbox("Hapus Rute:", d_opsi, key="ds")
            if st.button("Eksekusi Hapus"):
                a_d, t_d = d_sel.split("-")
                graph.hapus_rute(a_d, t_d)
                st.rerun()

# ==================== MENU 4: ANALISIS ====================
with tab4:
    st.subheader("📊 Analisis Jaringan Pink")
    stats = {k: len(v) for k, v in graph.edges.items()}
    if stats:
        st.bar_chart(stats)
        st.dataframe([{"Stasiun": k, "Koneksi": v} for k, v in stats.items()], use_container_width=True)
