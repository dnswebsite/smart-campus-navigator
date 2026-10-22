"""Uji otomatis: python tests.py"""
import itertools, networkx as nx
from core import load_graph, dijkstra_trace, validate, active_graph

G, _ = load_graph()
assert nx.is_connected(G), "graf awal harus terhubung"

# 1) Dijkstra == NetworkX untuk SEMUA pasangan titik, kedua bobot
for w in ("jarak", "waktu"):
    for s, t in itertools.permutations(G.nodes, 2):
        r = dijkstra_trace(G, s, t, w)
        assert abs(r.total - nx.dijkstra_path_length(G, s, t, weight=w)) < 1e-6, (s, t, w)
        assert validate(G, r, s, t, w)["ok"]

# 2) Dengan penutupan satu jalan, untuk semua pasangan & semua sisi
n = 0
for e in G.edges(data=True):
    closed = frozenset([e[2]["id"]])
    H = active_graph(G, closed)
    for s, t in itertools.permutations(G.nodes, 2):
        r = dijkstra_trace(G, s, t, "jarak", closed)
        assert r.reachable == nx.has_path(H, s, t)
        if r.reachable:
            assert abs(r.total - nx.dijkstra_path_length(H, s, t, weight="jarak")) < 1e-6
        n += 1
print("OK:", n, "kasus penutupan jalan lolos; graf awal terhubung; semua pasangan cocok dengan NetworkX")

# 3) Kasus tak terjangkau: tutup Sport Center-Khadijah (Khadijah hanya punya satu akses)
eid = G["SPORT"]["KHADIJAH"]["id"]
r = dijkstra_trace(G, "G_UTARA", "KHADIJAH", "jarak", frozenset([eid]))
assert not r.reachable and validate(G, r, "G_UTARA", "KHADIJAH", "jarak", frozenset([eid]))["ok"]
print("OK: kasus tujuan tak terjangkau terdeteksi (" + eid + ")")
