"""Smart Campus Navigator — UIN Maulana Malik Ibrahim Malang
Created by Danu Seno Bhakti Utomo - 240601110022
Jalankan: python -m streamlit run app.py
"""
import base64
import pathlib
import plotly.graph_objects as go
import streamlit as st
import denah
from core import load_graph, dijkstra_trace, validate

st.set_page_config(page_title="Smart Campus Navigator", page_icon="📍", layout="wide")
AUTHOR = "Danu Seno Bhakti Utomo"
NIM = "240601110022"

# ---------- gaya: foto kampus sebagai latar header (transparan/overlay), kartu kaca ----------
_img = pathlib.Path("assets/header.jpg")
_b64 = base64.b64encode(_img.read_bytes()).decode() if _img.exists() else ""
CSS = """
<style>
:root{--photo:url(data:image/jpeg;base64,__IMG__);}
.stApp{background:linear-gradient(rgba(8,14,28,.90),rgba(8,14,28,.95)),var(--photo) center/cover fixed; color:#e6edf7;}
header[data-testid="stHeader"]{background:transparent;}
section[data-testid="stSidebar"]{background:rgba(12,21,38,.80); backdrop-filter:blur(10px); border-right:1px solid rgba(80,110,160,.25);}
.hero{position:relative; border-radius:20px; overflow:hidden; padding:38px 34px 30px 34px; margin-bottom:16px;
  border:1px solid rgba(120,160,220,.25);
  background:linear-gradient(95deg,rgba(6,12,26,.93) 0%,rgba(6,12,26,.70) 48%,rgba(6,12,26,.18) 100%),var(--photo) center 38%/cover;
  box-shadow:0 10px 40px rgba(0,0,0,.35);}
.hero .badge{display:inline-block; font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; color:#7dd3fc;
  background:rgba(56,189,248,.12); border:1px solid rgba(56,189,248,.35); padding:4px 12px; border-radius:999px;}
.hero h1{margin:12px 0 6px 0; font-size:2.3rem; color:#fff; text-shadow:0 2px 12px rgba(0,0,0,.5);}
.hero p{margin:0; max-width:560px; color:#c7d6ee; font-size:1rem;}
.hero .credit{margin-top:16px; font-size:.9rem; color:#e6edf7;}
.hero .credit b{color:#7dd3fc;}
.card{background:rgba(17,28,49,.62); backdrop-filter:blur(10px); border:1px solid rgba(90,125,185,.28);
  border-radius:16px; padding:14px 16px; margin-bottom:12px;}
.card h4{margin:0 0 4px 0; color:#38bdf8; font-size:1rem;}
.kpi{font-size:1.7rem; font-weight:700; color:#fff;}
.sub{color:#9fb3d1; font-size:.85rem;}
.ok{color:#34d399;} .warn{color:#fbbf24;}
.footer{text-align:center; color:#8fa3c4; font-size:.8rem; margin:18px 0 4px 0;}
</style>"""
st.markdown(CSS.replace("__IMG__", _b64), unsafe_allow_html=True)

G, META = load_graph()
LABEL = {n: d["label"] for n, d in G.nodes(data=True)}
ID_BY_LABEL = {v: k for k, v in LABEL.items()}
EDGE_BY_ID = {a["id"]: (u, v, a) for u, v, a in G.edges(data=True)}
EDGE_LABELS = {eid: f"{eid} · {LABEL[u]} ↔ {LABEL[v]} ({a['jarak']:.0f} m)" for eid, (u, v, a) in EDGE_BY_ID.items()}
NONE = "(tidak ada)"
TYPE_STYLE = {"gedung": ("#38bdf8", "square", "Gedung"), "gerbang": ("#a78bfa", "diamond", "Gerbang"),
              "simpang": ("#94a3b8", "circle", "Persimpangan")}
TYPE_IDS = {t: [n for n in G if G.nodes[n]["type"] == t] for t in TYPE_STYLE}
SPEEDS = {"Lambat": 1000, "Sedang": 650, "Cepat": 400, "Sangat cepat": 200}

# ---------- state & callback ----------
ss = st.session_state
ss.setdefault("src", "Gerbang Depan (Selatan)")
ss.setdefault("dst", "Ged. Saintek")
ss.setdefault("closed", NONE)

def preset_on_route():
    base = dijkstra_trace(G, ID_BY_LABEL[ss.src], ID_BY_LABEL[ss.dst], ss.weight)
    if base.path and len(base.path) > 1:
        m = len(base.path) // 2
        ss.closed = EDGE_LABELS[G[base.path[m - 1]][base.path[m]]["id"]]

def preset_off_route():
    base = dijkstra_trace(G, ID_BY_LABEL[ss.src], ID_BY_LABEL[ss.dst], ss.weight)
    on = {G[a][b]["id"] for a, b in zip(base.path, base.path[1:])} if base.path else set()
    for eid in EDGE_BY_ID:
        if eid not in on:
            ss.closed = EDGE_LABELS[eid]
            break

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### 📍 Campus Navigator")
    st.caption("Smart pathfinding · UIN Maulana Malik Ibrahim Malang")
    labels = sorted(LABEL.values())
    st.selectbox("Titik asal", labels, key="src")
    st.selectbox("Titik tujuan", labels, key="dst")
    st.radio("Bobot sisi", ["jarak", "waktu"], key="weight", horizontal=True,
             format_func=lambda x: "Jarak (m)" if x == "jarak" else "Waktu (dtk)")
    st.markdown("**Penutupan jalan**")
    st.selectbox("Jalan yang ditutup", [NONE] + list(EDGE_LABELS.values()), key="closed")
    c1, c2 = st.columns(2)
    c1.button("Uji 1: tutup di rute", on_click=preset_on_route, width="stretch")
    c2.button("Uji 2: tutup di luar rute", on_click=preset_off_route, width="stretch")
    view = st.radio("Tampilan graf", ["Denah kampus", "Peta OpenStreetMap"])
    show_scn = st.radio("Animasi untuk", ["Setelah penutupan", "Kondisi awal"], disabled=(ss.closed == NONE))
    speed_name = st.select_slider("Kecepatan animasi", options=list(SPEEDS), value="Sedang")
    st.markdown("---")
    st.caption(f"Created by **{AUTHOR}**  \n{NIM}")

src, dst, W = ID_BY_LABEL[ss.src], ID_BY_LABEL[ss.dst], ss.weight
unit = "m" if W == "jarak" else "dtk"
closed_id = None if ss.closed == NONE else ss.closed.split(" · ")[0]
closed = frozenset([closed_id]) if closed_id else frozenset()

# ---------- hero / judul ----------
st.markdown(f"""
<div class="hero">
  <span class="badge">📍 Campus Navigator</span>
  <h1>Smart Campus Navigator</h1>
  <p>Cari rute terpendek antargedung UIN Maulana Malik Ibrahim Malang dengan algoritma Dijkstra,
  lalu lihat apa yang terjadi ketika satu jalan ditutup.</p>
  <div class="credit">Created by <b>{AUTHOR}</b> &nbsp;·&nbsp; {NIM}</div>
</div>""", unsafe_allow_html=True)

if src == dst:
    st.warning("Titik asal dan tujuan sama — pilih tujuan yang berbeda.")
    st.stop()

base = dijkstra_trace(G, src, dst, W)
after = dijkstra_trace(G, src, dst, W, closed) if closed_id else base
use_after = bool(closed_id) and show_scn == "Setelah penutupan"
shown = after if use_after else base
shown_closed = closed if use_after else frozenset()
show_base = use_after and base.reachable and after.path != base.path

# ---------- figur beranimasi (frames Plotly: berjalan di browser, tanpa rerun) ----------
def build_fig(res, speed_ms):
    steps = res.steps
    osm = view == "Peta OpenStreetMap"
    X = (lambda n: G.nodes[n]["lon"]) if osm else (lambda n: G.nodes[n]["px"])
    Y = (lambda n: G.nodes[n]["lat"]) if osm else (lambda n: -G.nodes[n]["py"])
    T = go.Scattermap if osm else go.Scatter

    def co(edges):
        xs, ys = [], []
        for a, b in edges:
            xs += [X(a), X(b), None]
            ys += [Y(a), Y(b), None]
        return dict(lon=xs, lat=ys) if osm else dict(x=xs, y=ys)

    def pe(path, upto=None):
        p = path if upto is None else path[:upto + 1]
        return list(zip(p, p[1:]))

    def node_props(s, route_nodes):
        out = {}
        for typ, (color, _sym, _nm) in TYPE_STYLE.items():
            txt, cols, sizes, hov = [], [], [], []
            for n in TYPE_IDS[typ]:
                d = s["dist"].get(n)
                name = "" if typ == "simpang" else LABEL[n]
                txt.append(name + (f"<br>{d:.0f}" if d is not None and name else (f"{d:.0f}" if d is not None else "")))
                c = color
                if n in s["done"]: c = "#34d399"
                if n in route_nodes: c = "#22d3ee"
                if n == s["current"]: c = "#fbbf24"
                if n == src: c = "#3b82f6"
                if n == dst: c = "#ef4444"
                cols.append(c)
                sizes.append(26 if n == s["current"] else 16)
                hov.append(f"{LABEL[n]}<br>nilai sementara: " + ("∞" if d is None else f"{d:.1f} {unit}"))
            out[typ] = dict(text=txt, color=cols, size=sizes, hover=hov)
        return out

    def state(s, route_edges, route_nodes, final):
        tree = [] if final else [(p, c) for c, p in s["prev"].items()]
        rel = [] if (final or not s["relaxed"]) else [s["relaxed"]]
        bas = pe(base.path) if (final and show_base) else []
        return dict(tree=tree, rel=rel, bas=bas, route=route_edges, nodes=node_props(s, route_nodes))

    # --- urutan frame: langkah Dijkstra, lalu penelusuran rute (mundur lewat prev) ---
    plan = []  # (state, pesan)
    total = len(steps)
    for i, s in enumerate(steps):
        final = (i == total - 1) and not res.reachable
        plan.append((state(s, [], set(), final), f"<b>Langkah {i + 1}/{total}</b> · {s['msg']}"))
    if res.reachable:
        last = steps[-1]
        for k in range(1, len(res.path)):
            nodes_k = set(res.path[:k + 1])
            plan.append((state(last, pe(res.path, k), nodes_k, k == len(res.path) - 1),
                         f"<b>Menelusuri rute</b> · {' → '.join(LABEL[n] for n in res.path[:k + 1])}"
                         + (f"<br><b>Selesai: {res.total:.1f} {unit}</b>" if k == len(res.path) - 1 else "")))

    def ann(text):
        return [dict(text=text, xref="paper", yref="paper", x=0.5, y=-0.02, xanchor="center", yanchor="top",
                     showarrow=False, align="left", width=640, bgcolor="rgba(8,14,28,.82)", bordercolor="#2b3f63",
                     borderwidth=1, borderpad=7, font=dict(color="#e6edf7", size=12))]

    st0, msg0 = plan[0]
    fig = go.Figure()
    def L(edges, color, width, name, dash=None, legend=True):
        ln = dict(color=color, width=width)
        if dash and not osm: ln["dash"] = dash
        fig.add_trace(T(mode="lines", line=ln, name=name, hoverinfo="skip", showlegend=legend, **co(edges)))
    open_edges = [(u, v) for u, v, a in G.edges(data=True) if a["id"] not in shown_closed]
    L(open_edges, "#6f9bd6", 3, "Jalan terbuka")                       # 0
    L(st0["tree"], "#64748b", 5, "Jalur sementara")                    # 1
    L(st0["rel"], "#fbbf24", 7, "Sisi diperiksa")                      # 2
    L(st0["bas"], "#f97316", 4, "Rute awal (pembanding)", "dot", show_base)  # 3
    L(st0["route"], "#22d3ee", 8, "Rute terpendek")                    # 4
    ce = [(EDGE_BY_ID[e][0], EDGE_BY_ID[e][1]) for e in shown_closed]
    L(ce, "#ef4444", 5, "Jalan ditutup", "dash", bool(ce))             # 5
    mk = dict(lon=[(X(a) + X(b)) / 2 for a, b in ce], lat=[(Y(a) + Y(b)) / 2 for a, b in ce]) if osm else \
         dict(x=[(X(a) + X(b)) / 2 for a, b in ce], y=[(Y(a) + Y(b)) / 2 for a, b in ce])
    fig.add_trace(T(mode="markers+text", text=["✕"] * len(ce), textfont=dict(color="#fff", size=13),
                    marker=dict(size=20, color="#ef4444"), hoverinfo="skip", showlegend=False, **mk))  # 6
    for typ, (color, sym, name) in TYPE_STYLE.items():                 # 7..10
        ids, p = TYPE_IDS[typ], st0["nodes"][typ]
        kw = dict(lon=[X(n) for n in ids], lat=[Y(n) for n in ids]) if osm else dict(x=[X(n) for n in ids], y=[Y(n) for n in ids])
        fig.add_trace(T(mode="markers+text", text=p["text"], textposition="top center",
                        textfont=dict(color="#e6edf7", size=10), hovertext=p["hover"], hoverinfo="text",
                        marker=(dict(size=p["size"], color=p["color"]) if osm else
                                dict(size=p["size"], color=p["color"], symbol=sym, line=dict(color="#0b1220", width=2))),
                        name=name, **kw))

    if not osm:  # label gedung/area non-titik pada denah (statis, setelah trace dinamis)
        lb = denah.labels()
        fig.add_trace(go.Scatter(mode="text", x=lb["x"], y=lb["y"], text=lb["text"], textposition=lb["textposition"],
                                 textfont=dict(color="#aebbd3", size=9), hoverinfo="skip", showlegend=False))
    frames = []
    for i, (st_, msg) in enumerate(plan):
        data = [T(**co(st_["tree"])), T(**co(st_["rel"])), T(**co(st_["bas"])), T(**co(st_["route"]))]
        for typ in TYPE_STYLE:
            p = st_["nodes"][typ]
            data.append(T(text=p["text"], hovertext=p["hover"], marker=dict(color=p["color"], size=p["size"])))
        frames.append(go.Frame(name=f"f{i}", data=data, traces=[1, 2, 3, 4] + list(range(7, 7 + len(TYPE_STYLE))),
                               layout=dict(annotations=ann(msg))))
    fig.frames = frames

    anim = dict(frame=dict(duration=speed_ms, redraw=True), transition=dict(duration=int(speed_ms * 0.45), easing="cubic-in-out"),
                fromcurrent=True, mode="immediate")
    still = dict(frame=dict(duration=0, redraw=True), transition=dict(duration=0), mode="immediate")
    btn = dict(bgcolor="#16345c", bordercolor="#2b5c9a", font=dict(color="#e6edf7"))
    lay = dict(height=900, margin=dict(l=0, r=0, t=0, b=150), uirevision="keep",
               paper_bgcolor="rgba(17,28,49,0.55)", plot_bgcolor="rgba(17,28,49,0.0)",
               legend=dict(bgcolor="rgba(12,21,38,.80)", font=dict(color="#e6edf7"), x=0.01, y=0.01, yanchor="bottom"),
               annotations=ann(msg0),
               updatemenus=[dict(type="buttons", direction="right", x=0.0, y=-0.115, xanchor="left", yanchor="top",
                                 pad=dict(t=4, r=6), showactive=False, **btn,
                                 buttons=[dict(label="▶ Putar", method="animate", args=[None, anim]),
                                          dict(label="⏸ Jeda", method="animate",
                                               args=[[None], dict(frame=dict(duration=0, redraw=False), transition=dict(duration=0), mode="immediate")]),
                                          dict(label="↺ Ulang", method="animate", args=[["f0"], still])])],
               sliders=[dict(x=0.34, y=-0.115, xanchor="left", yanchor="top", len=0.66, pad=dict(t=0, b=0),
                             currentvalue=dict(prefix="Langkah ", font=dict(color="#e6edf7", size=12)),
                             font=dict(color="rgba(0,0,0,0)"), tickcolor="rgba(0,0,0,0)", bgcolor="#2b3f63",
                             steps=[dict(method="animate", label=str(i + 1), args=[[f"f{i}"], still]) for i in range(len(plan))])])
    if osm:
        lay["map"] = dict(style="open-street-map", zoom=16.3,
                          center=dict(lat=sum(G.nodes[n]["lat"] for n in G) / len(G), lon=sum(G.nodes[n]["lon"] for n in G) / len(G)))
    else:  # posisi titik tetap (stabil) mengikuti denah
        lay["shapes"] = denah.shapes()
        lay["xaxis"] = dict(visible=False, range=[40, 705], fixedrange=True)
        lay["yaxis"] = dict(visible=False, range=[-990, -95], scaleanchor="x", fixedrange=True)
    fig.update_layout(**lay)
    return fig, [m for _, m in plan]

# ---------- layout utama ----------
colA, colB = st.columns([3, 1.35])
fmt = lambda r: "tidak dapat dicapai" if not r.reachable else f"{r.total:.1f} {unit}"
with colB:
    st.markdown(f"<div class='card'><h4>Rute kondisi awal</h4><div class='kpi'>{fmt(base)}</div>"
                f"<div class='sub'>{' → '.join(LABEL[n] for n in base.path) if base.path else '—'}</div></div>", unsafe_allow_html=True)
    if closed_id:
        diff = ""
        if after.reachable and base.reachable:
            d = after.total - base.total
            diff = f"<span class='{'warn' if d > 0 else 'ok'}'>{'+' if d >= 0 else ''}{d:.1f} {unit} dari rute awal</span><br>"
        st.markdown(f"<div class='card'><h4>Setelah penutupan</h4><div class='kpi'>{fmt(after)}</div>"
                    f"<div class='sub'>{diff}{' → '.join(LABEL[n] for n in after.path) if after.path else '—'}</div></div>", unsafe_allow_html=True)
        if not after.reachable:
            st.error(f"⚠️ {LABEL[dst]} tidak dapat dicapai dari {LABEL[src]} setelah jalan ini ditutup.")
        elif after.path == base.path:
            st.info("Jalan yang ditutup **tidak berada di rute terpendek**, sehingga rute dan total bobot tidak berubah.")
        else:
            st.warning("Jalan yang ditutup **berada di rute terpendek**, sehingga algoritma mencari alternatif.")
    st.markdown("<div class='card'><h4>Cara membaca animasi</h4><div class='sub'>"
                "Tekan <b>▶ Putar</b> di bawah peta, atau geser slider untuk melangkah manual. "
                "Angka di titik = nilai jarak/waktu sementara. Hijau = sudah final, kuning = sedang diproses, "
                "garis biru muda = rute terpendek, garis merah putus-putus = jalan ditutup.</div></div>", unsafe_allow_html=True)

fig, messages = build_fig(shown, SPEEDS[speed_name])
with colA:
    st.plotly_chart(fig, config=dict(displayModeBar=False, scrollZoom=True),
                    key=f"fig-{src}-{dst}-{W}-{closed_id}-{view}-{speed_name}-{use_after}")
    with st.expander("Daftar semua langkah algoritma"):
        st.dataframe([dict(no=i + 1, keterangan=m.replace("<b>", "").replace("</b>", "").replace("<br>", " | "))
                      for i, m in enumerate(messages)], width="stretch", hide_index=True)

# ---------- tab: validasi, eksperimen, model ----------
t1, t2, t3 = st.tabs(["✅ Validasi", "🧪 Perbandingan skenario", "🗺️ Model graf"])
with t1:
    for name, r, cl in [("Kondisi awal", base, frozenset())] + ([("Setelah penutupan", after, closed)] if closed_id else []):
        v = validate(G, r, src, dst, W, cl)
        st.markdown(f"**{name}**")
        if not v["reachable"]:
            st.markdown(f"- Tujuan tak terjangkau. Pemeriksaan `nx.has_path` = tidak ada jalur → {'✅ cocok' if v['ok'] else '❌ tidak cocok'}")
            continue
        st.markdown(f"- Setiap pasangan titik berurutan bertetangga di graf aktif: {'✅' if v['adjacent'] else '❌'}")
        st.markdown(f"- Jumlah bobot manual **{v['manual']:.1f}** = keluaran algoritma **{v['algo']:.1f}** = NetworkX **{v['nx']:.1f}** {unit}: {'✅' if v['ok'] else '❌'}")
        st.dataframe([dict(dari=LABEL[a], ke=LABEL[b], jalan=n, bobot=f"{w:.1f} {unit}") for a, b, w, n in v["pairs"]],
                     width="stretch", hide_index=True)
    st.caption("Batas interpretasi: rute terbaik hanya berlaku untuk bobot dan kondisi jalan dalam data (jarak garis lurus "
               "antar titik, kecepatan jalan 1,2 m/s); tidak otomatis mewakili kondisi lalu lintas, kepadatan, atau jalur sebenarnya.")
with t2:
    if not closed_id:
        st.info("Pilih satu jalan untuk ditutup di sidebar (atau pakai tombol Uji 1 / Uji 2).")
    else:
        u, v, a = EDGE_BY_ID[closed_id]
        st.write(f"Jalan ditutup: **{a['nama']}** ({LABEL[u]} ↔ {LABEL[v]}).")
        st.dataframe([
            dict(skenario="Awal", status="terjangkau" if base.reachable else "tidak terjangkau",
                 total=f"{base.total:.1f} {unit}" if base.reachable else "—", jumlah_titik=len(base.path or []),
                 rute=" → ".join(LABEL[n] for n in base.path or [])),
            dict(skenario="Setelah penutupan", status="terjangkau" if after.reachable else "tidak terjangkau",
                 total=f"{after.total:.1f} {unit}" if after.reachable else "—", jumlah_titik=len(after.path or []),
                 rute=" → ".join(LABEL[n] for n in after.path or []))], width="stretch", hide_index=True)
        st.markdown("**Mengapa rute bisa berubah pada satu skenario tetapi tidak pada skenario lain?** "
                    "Dijkstra hanya terpengaruh bila sisi yang dihapus termasuk rute optimal. Jika sisi itu tidak dipakai, "
                    "rute optimal tetap valid. Jika dipakai, rute baru dicari dari sisi yang masih ada — "
                    "dan bila sisi itu satu-satunya penghubung (jembatan graf), tujuan menjadi tak terjangkau.")
with t3:
    st.write(f"**Jenis graf:** {META['jenis_graf']}  \n**Bobot:** {META['bobot']}  \n**Sumber:** {META['sumber']}")
    st.write(f"Titik = gedung, gerbang, dan persimpangan ({G.number_of_nodes()} titik); sisi = jalan yang dapat dilalui ({G.number_of_edges()} sisi).")
    st.dataframe([dict(id=a["id"], dari=LABEL[u], ke=LABEL[v], jalan=a["nama"], jarak_m=a["jarak"], waktu_dtk=a["waktu"])
                  for u, v, a in G.edges(data=True)], width="stretch", hide_index=True)

st.markdown(f"<div class='footer'>Smart Campus Navigator · Komputasi Graf 2026 · Created by {AUTHOR} - {NIM}</div>", unsafe_allow_html=True)
