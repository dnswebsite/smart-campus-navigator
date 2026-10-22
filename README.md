# Smart Campus Navigator — UIN Maulana Malik Ibrahim Malang

*Created by Danu Seno Bhakti Utomo — 240601110022*

Aplikasi graf interaktif (UTS Komputasi Graf, Proyek 01): rute terpendek antargedung dan efek penutupan satu jalan.

## Cara menjalankan
```bash
python -m venv .venv && .venv\Scripts\activate      # Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python tests.py            # uji otomatis
streamlit run app.py
```
Ulangi pembuatan data dari OSM (opsional): `python build_graph.py map.osm`

## Model graf
- **Denah**: bentuk dan penamaan mengikuti denah kampus (`denah.py`: gedung, jalan, bundaran, gerbang, area utara hingga selatan). Unsur acara/parkir tidak digambar.
- **Titik** (20, sesuai batas 10–20): 3 gerbang, bundaran, 5 persimpangan, dan 11 gedung. Gedung lain pada denah tampil sebagai latar visual, bukan titik graf. Koordinat gedung berasal dari centroid bangunan OSM (`osm_id` di `data/campus.json`); titik tanpa padanan OSM diestimasi dengan transformasi affine denah→OSM.
- **Sisi** (29): jalan/akses yang dapat dilalui. **Tak berarah** (semua jalan dua arah).
- **Bobot**: jarak haversine (meter); alternatif waktu = jarak / 1,2 m/s.
- **Pertanyaan**: rute terpendek dari titik asal ke tujuan, dan bagaimana rute berubah bila satu jalan ditutup.

## Algoritma
Dijkstra (antrean prioritas `heapq`), implementasi sendiri dengan pencatatan tiap langkah untuk animasi.
Pembanding validasi: `networkx.dijkstra_path_length`.

## Validasi
`python tests.py`: Dijkstra = NetworkX untuk semua pasangan titik (kedua bobot), dan untuk semua penutupan satu jalan; kasus tak terjangkau terdeteksi. Di aplikasi, tab **Validasi** memeriksa ketetanggaan tiap pasangan berurutan dan menjumlahkan bobot secara mandiri.

## Dua skenario uji (asal: Gerbang Depan Selatan, tujuan: Ged. Saintek, bobot jarak)
| Skenario | Jalan ditutup | Total | Rute |
|---|---|---|---|
| Awal | — | 186.6 m | Gerbang Depan (Selatan) → Simpang Tengah-Rektorat → Simpang Tengah-Perpustakaan → Ged. Saintek |
| Uji 1 (tutup di rute) | E08 Simpang Tengah-Rektorat ↔ Simpang Tengah-Perpustakaan | 264.7 m | Gerbang Depan (Selatan) → Simpang Tengah-Rektorat → Simpang Utara-Rektorat → Simpang Utara-Perpustakaan → Ged. Saintek |
| Uji 2 (tutup di luar rute) | E01 Gerbang Depan (Utara) ↔ Simpang Utara-Rektorat | 186.6 m | Gerbang Depan (Selatan) → Simpang Tengah-Rektorat → Simpang Tengah-Perpustakaan → Ged. Saintek (tidak berubah) |
| Batas | E21 Sport Center ↔ Khadijah (asal Gerbang Utara) | tak terjangkau | Khadijah hanya punya satu akses |

## Batas interpretasi
Hasil hanya berlaku untuk bobot dan kondisi jalan dalam data (jarak garis lurus antar titik, jalan dianggap dua arah); tidak mewakili kondisi lalu lintas atau jalur sebenarnya. Pemetaan denah → OSM berupa estimasi (mis. Ged. Megawati = Fakultas Ekonomi UIN pada OSM; Masjid Ma'had Putri = Masjid Ulul Albab).

## Tangkapan layar / demo
Tambahkan di folder `screenshots/`.
