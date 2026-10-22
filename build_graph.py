"""Membangun data/campus.json dari map.osm + denah kampus.

- Posisi tampilan denah: piksel pada gambar denah (px,py), konteks acara/parkir dibuang.
- Koordinat geografis: gedung bertanda osm_id memakai centroid bangunan OSM; titik lain
  (gerbang, persimpangan, Masjid Ma'had Putra) diestimasi dengan transformasi affine
  denah->OSM yang dicocokkan dari gedung-gedung yang punya osm_id.
- Bobot sisi = jarak haversine (meter). Graf tak berarah (semua jalan dua arah).
Jalankan:  python build_graph.py map.osm
"""
import json, math, sys
import numpy as np
import xml.etree.ElementTree as ET

def haversine(a, b):
    R = 6371000
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

# id, label, tipe, osm_way_id, (px,py)  -- maksimal 20 titik sesuai pedoman proyek
NODES = [
 ("G_UTARA",    "Gerbang Depan (Utara)",   "gerbang", None,      (626, 460)),
 ("G_SELATAN",  "Gerbang Depan (Selatan)", "gerbang", None,      (628, 570)),
 ("G_BELAKANG", "Gerbang Belakang",        "gerbang", None,      (170, 460)),
 ("BUNDARAN",   "Bundaran / Tower",        "simpang", None,      (218, 460)),
 ("J_A",        "Simpang Utara-Perpustakaan", "simpang", None,   (345, 460)),
 ("J_B",        "Simpang Utara-Rektorat",  "simpang", None,      (452, 460)),
 ("J_W",        "Simpang Barat-Tengah",    "simpang", None,      (220, 570)),
 ("J_C",        "Simpang Tengah-Perpustakaan", "simpang", None,  (345, 570)),
 ("J_D",        "Simpang Tengah-Rektorat", "simpang", None,      (452, 570)),
 ("SAINTEK",    "Ged. Saintek",            "gedung",  395873077, (280, 519)),
 ("PERPUS",     "Perpustakaan",            "gedung",  395873093, (404, 515)),
 ("REKTORAT",   "Ged. Rektorat",           "gedung",  395873080, (505, 515)),
 ("MEGAWATI",   "Ged. Megawati",           "gedung",  395873086, (292, 619)),
 ("GED_B",      "Ged. B",                  "gedung",  395873050, (422, 675)),
 ("GED_A",      "Ged. A",                  "gedung",  395873049, (576, 698)),
 ("GED_C",      "Ged. C / Pusat Bahasa",   "gedung",  395873051, (266, 717)),
 ("MASJID_PUTRI","Masjid Ma'had Putri",    "gedung",  395873067, (427, 807)),
 ("SPORT",      "Sport Center",            "gedung",  327351341, (339, 868)),
 ("KHADIJAH",   "Khadijah Al-Kubra",       "gedung",  395873063, (327, 933)),
 ("MASJID_PUTRA","Masjid Ma'had Putra",    "gedung",  None,      (290, 412)),
]
EDGES = [
 ("G_UTARA","J_B","Jalan Utara (depan)"), ("J_B","J_A","Jalan Utara"), ("J_A","BUNDARAN","Jalan Utara"),
 ("BUNDARAN","G_BELAKANG","Jalan Belakang"), ("BUNDARAN","MASJID_PUTRA","Jalan Utara Ma'had"),
 ("BUNDARAN","J_W","Jalan Barat"), ("J_W","J_C","Jalan Tengah"), ("J_C","J_D","Jalan Tengah"),
 ("J_D","G_SELATAN","Jalan Tengah (depan)"),
 ("J_A","J_C","Jalan Perpustakaan"), ("J_B","J_D","Jalan Rektorat"),
 ("J_W","GED_C","Jalan Barat Selatan"), ("GED_C","SPORT","Akses Ged. C - Sport Center"),
 ("J_D","GED_B","Jalan Ged. B"), ("G_SELATAN","GED_B","Jalan Ged. B (depan)"),
 ("G_SELATAN","GED_A","Jalan Ged. A"), ("GED_A","GED_B","Jalan Ged. A-B"),
 ("GED_B","MASJID_PUTRI","Jalan Selatan"), ("GED_A","MASJID_PUTRI","Jalan Masjid"),
 ("MASJID_PUTRI","SPORT","Jalan Selatan"), ("SPORT","KHADIJAH","Jalan Khadijah"),
 ("SAINTEK","J_A","Akses Saintek"), ("SAINTEK","J_C","Akses Saintek"),
 ("PERPUS","J_A","Akses Perpustakaan"), ("PERPUS","J_C","Akses Perpustakaan"),
 ("REKTORAT","J_B","Akses Rektorat"), ("REKTORAT","J_D","Akses Rektorat"),
 ("MEGAWATI","J_W","Akses Megawati"), ("MEGAWATI","J_C","Akses Megawati"),
]

def centroid(nd, way):
    pts = [nd[n.get("ref")] for n in way.findall("nd")]
    return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))

def main(osm_path):
    root = ET.parse(osm_path).getroot()
    nd = {n.get("id"): (float(n.get("lat")), float(n.get("lon"))) for n in root.findall("node")}
    ways = {w.get("id"): w for w in root.findall("way")}
    known = {n[0]: centroid(nd, ways[str(n[3])]) for n in NODES if n[3] is not None}
    # affine denah(px,py) -> (lat,lon) dari titik yang punya padanan OSM
    A = np.array([[n[4][0], n[4][1], 1] for n in NODES if n[0] in known], float)
    B = np.array([known[n[0]] for n in NODES if n[0] in known], float)
    coef, *_ = np.linalg.lstsq(A, B, rcond=None)
    res = [haversine(tuple(A[i] @ coef), tuple(B[i])) for i in range(len(A))]
    print(f"Fit affine: {len(A)} titik acuan, galat rata-rata {np.mean(res):.1f} m, maks {max(res):.1f} m")
    pos, nodes = {}, []
    for nid, label, typ, osm_id, (px, py) in NODES:
        ll = known.get(nid) or tuple(np.array([px, py, 1.0]) @ coef)
        pos[nid] = ll
        nodes.append(dict(id=nid, label=label, type=typ, lat=round(ll[0], 6), lon=round(ll[1], 6),
                          px=px, py=py, osm_id=osm_id))
    edges = [dict(id=f"E{i:02d}", u=u, v=v, nama=nm, jarak=round(haversine(pos[u], pos[v]), 1))
             for i, (u, v, nm) in enumerate(EDGES, 1)]
    meta = dict(sumber="OpenStreetMap (map.osm) + denah UIN Maulana Malik Ibrahim Malang",
                jenis_graf="tak berarah (semua jalan dua arah)",
                bobot="jarak (meter) = haversine antar titik; waktu = jarak / 1,2 m/s")
    json.dump(dict(meta=meta, nodes=nodes, edges=edges), open("data/campus.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(len(nodes), "titik,", len(edges), "sisi")
    for e in edges: print(e["id"], e["u"], "-", e["v"], e["jarak"], "m")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "map.osm")
