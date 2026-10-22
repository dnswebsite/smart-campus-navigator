"""Latar denah kampus (mengikuti gambar denah UIN Maulana Malik Ibrahim Malang).
Koordinat = piksel gambar denah (768x1024, y ke bawah). Unsur acara/parkir sengaja tidak digambar.
Gedung yang menjadi titik graf tidak diberi label di sini (labelnya muncul dari titik graf)."""

def R(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

# (polygon, label|None)   label = (teks, px, py, posisi)
BUILDINGS = [
 # --- area utara ---
 ([(158,150),(186,118),(202,127),(178,167)], ("Rumah<br>Dewan<br>Pengasuh", 150, 150, "middle left")),
 (R(232,112,309,129),  ("Al-Faraby", 270, 120, "middle center")),
 (R(217,168,293,187),  ("Ibnu Khaldun", 255, 177, "middle center")),
 (R(259,211,293,236),  None),
 (R(303,190,325,249),  None),
 (R(217,243,283,262),  ("Ibnu Sina", 250, 252, "middle center")),
 (R(217,274,283,293),  ("Ibnu Rusyd", 250, 283, "middle center")),
 (R(153,230,175,305),  ("Ged. Halaqoh", 148, 268, "middle left")),
 (R(153,316,175,372),  None),
 (R(157,378,179,425),  None),
 (R(262,310,279,360),  ("Al-Ghazali", 285, 335, "middle left")),
 (R(230,372,252,398),  None),
 ([(250,412),(262,390),(329,412),(317,436)], None),            # Masjid Ma'had Putra (titik graf)
 (R(342,411,371,440),  ("El-Zawa", 357, 400, "middle center")),
 ([(388,420),(390,409),(452,426),(450,438)], ("Microteaching", 428, 398, "middle center")),
 (R(459,419,520,440),  ("Ged. Humbud", 490, 409, "middle center")),
 (R(527,419,557,440),  ("Sekretariat Penerimaan<br>Mahasiswa Baru", 612, 406, "middle center")),
 (R(182,515,203,548),  None),
 # --- area tengah ---
 (R(238,482,323,556),  None),                                   # Ged. Saintek (titik graf)
 (R(367,478,442,553),  None),                                   # Perpustakaan (titik graf)
 (R(466,475,544,555),  None),                                   # Ged. Rektorat (titik graf)
 (R(248,587,337,652),  None),                                   # Ged. Megawati (titik graf)
 (R(397,603,447,747),  None),                                   # Ged. B (titik graf)
 (R(540,652,612,744),  None),                                   # Ged. A (titik graf)
 (R(548,702,577,744),  None),                                   # bagian dalam Ged. A
 (R(243,665,290,770),  None),                                   # Ged. C / Pusat Bahasa (titik graf)
 # --- area selatan ---
 (R(404,789,450,826),  None),                                   # Masjid Ma'had Putri (titik graf)
 (R(291,838,387,899),  None),                                   # Sport Center (titik graf)
 (R(294,921,361,945),  None),                                   # Khadijah Al-Kubra (titik graf)
 (R(250,903,279,976),  ("Kantin<br>Ma'had<br>Putri", 246, 940, "middle left")),
 (R(412,840,441,930),  None),
 (R(458,810,483,887),  None),
 (R(458,901,483,962),  ("ABA", 470, 932, "middle center")),
]

# jalan: (polyline, lebar)
ROADS = [
 ([(218,460),(628,460)], 9),                                    # jalan utara
 ([(220,570),(628,570)], 9),                                    # jalan tengah
 ([(220,460),(220,768)], 9),                                    # jalan barat
 ([(345,460),(345,665)], 9),                                    # jalan antara Saintek-Perpustakaan
 ([(452,460),(452,560)], 9),                                    # jalan antara Perpustakaan-Rektorat
 ([(218,440),(214,400),(212,375),(205,330),(200,260),(200,155)], 5),   # jalan utara menuju Ma'had
 ([(214,368),(298,368)], 4), ([(298,364),(298,386)], 4),
]
GATES = [((628,440),(628,480)), ((631,548),(631,598)), ((169,440),(169,478))]
BUNDARAN = (218, 460, 20)
FREE_LABELS = [("Tower", 118, 500, "middle center")]
TOWER_LINE = ((206, 470), (140, 497))

C_ROAD, C_BLD_FILL, C_BLD_LINE, C_GATE = "#1d2a47", "rgba(120,150,200,0.13)", "#7088b0", "#a78bfa"

def shapes():
    out = []
    for pts, w in ROADS:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            out.append(dict(type="line", x0=x0, y0=-y0, x1=x1, y1=-y1, layer="below",
                            line=dict(color=C_ROAD, width=w, dash="solid")))
    for (x0, y0), (x1, y1) in GATES:
        out.append(dict(type="line", x0=x0, y0=-y0, x1=x1, y1=-y1, layer="below", line=dict(color=C_GATE, width=6)))
    cx, cy, r = BUNDARAN
    out.append(dict(type="circle", x0=cx-r, y0=-(cy-r), x1=cx+r, y1=-(cy+r), layer="below",
                    line=dict(color="#94a3b8", width=2), fillcolor="rgba(29,42,71,.9)"))
    (a, b), (c, d) = TOWER_LINE
    out.append(dict(type="line", x0=a, y0=-b, x1=c, y1=-d, layer="below", line=dict(color="#94a3b8", width=1.5, dash="dot")))
    for pts, _ in BUILDINGS:
        path = "M " + " L ".join(f"{x},{-y}" for x, y in pts) + " Z"
        out.append(dict(type="path", path=path, layer="below", line=dict(color=C_BLD_LINE, width=1.2), fillcolor=C_BLD_FILL))
    return out

def labels():
    items = [l for _, l in BUILDINGS if l] + FREE_LABELS
    return dict(x=[i[1] for i in items], y=[-i[2] for i in items], text=[i[0] for i in items],
                textposition=[i[3] for i in items])
