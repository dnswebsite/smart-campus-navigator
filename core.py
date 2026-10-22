"""Inti komputasi: pemuatan graf, Dijkstra (dengan jejak langkah), validasi."""
from __future__ import annotations
import heapq, json, math
from dataclasses import dataclass, field
import networkx as nx

SPEED = 1.2  # m/s, kecepatan jalan kaki
INF = math.inf

def load_graph(path="data/campus.json"):
    d = json.load(open(path, encoding="utf-8"))
    G = nx.Graph()
    for n in d["nodes"]:
        G.add_node(n["id"], **n)
    for e in d["edges"]:
        G.add_edge(e["u"], e["v"], id=e["id"], nama=e["nama"],
                   jarak=e["jarak"], waktu=round(e["jarak"] / SPEED, 1))
    return G, d["meta"]

def active_graph(G, closed=frozenset()):
    """Salinan graf tanpa sisi yang ditutup (closed = himpunan id sisi)."""
    H = G.copy()
    H.remove_edges_from([(u, v) for u, v, a in G.edges(data=True) if a["id"] in closed])
    return H

@dataclass
class Result:
    path: list | None
    total: float
    steps: list = field(default_factory=list)
    reachable: bool = True

def dijkstra_trace(G, src, dst, weight="jarak", closed=frozenset()):
    """Dijkstra implementasi sendiri; setiap langkah dicatat untuk animasi."""
    H = active_graph(G, closed)
    dist = {n: INF for n in H}
    prev, done = {}, []
    dist[src] = 0.0
    pq = [(0.0, src)]
    steps = []

    def snap(msg, current=None, relaxed=None, improved=False):
        steps.append(dict(msg=msg, current=current, relaxed=relaxed, improved=improved,
                          done=list(done), prev=dict(prev),
                          dist={k: v for k, v in dist.items() if v < INF}))

    snap(f"Mulai: jarak {G.nodes[src]['label']} = 0, titik lain = ∞.")
    found = False
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.append(u)
        snap(f"Pilih {G.nodes[u]['label']} (nilai terkecil = {d:.1f}); nilainya sudah final.", current=u)
        if u == dst:
            found = True
            snap(f"Tujuan {G.nodes[dst]['label']} final → selesai.", current=u)
            break
        for v in H[u]:
            if v in done:
                continue
            w = H[u][v][weight]
            nd = d + w
            if nd < dist[v]:
                old = dist[v]
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
                txt = "∞" if old == INF else f"{old:.1f}"
                snap(f"Relaksasi {G.nodes[u]['label']}→{G.nodes[v]['label']}: {d:.1f}+{w:.1f}={nd:.1f} < {txt}, diperbarui.",
                     current=u, relaxed=(u, v), improved=True)
            else:
                snap(f"Relaksasi {G.nodes[u]['label']}→{G.nodes[v]['label']}: {d:.1f}+{w:.1f}={nd:.1f} ≥ {dist[v]:.1f}, tidak berubah.",
                     current=u, relaxed=(u, v))
    if not found:
        snap(f"Antrean habis: {G.nodes[dst]['label']} tidak dapat dicapai.")
        return Result(None, INF, steps, False)
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    path.reverse()
    return Result(path, dist[dst], steps, True)

def validate(G, res, src, dst, weight="jarak", closed=frozenset()):
    """Tiga pemeriksaan mandiri: ketetanggaan, jumlah bobot manual, pembanding NetworkX."""
    H = active_graph(G, closed)
    if not res.reachable:
        ref_ok = not nx.has_path(H, src, dst)
        return dict(reachable=False, ok=ref_ok, adjacent=None, manual=None, algo=None, nx=None,
                    pairs=[])
    pairs = list(zip(res.path, res.path[1:]))
    adjacent = all(H.has_edge(a, b) for a, b in pairs)
    manual = sum(H[a][b][weight] for a, b in pairs) if adjacent else None
    ref = nx.dijkstra_path_length(H, src, dst, weight=weight)
    ok = adjacent and abs(manual - res.total) < 1e-6 and abs(ref - res.total) < 1e-6
    return dict(reachable=True, ok=ok, adjacent=adjacent, manual=manual, algo=res.total, nx=ref,
                pairs=[(a, b, H[a][b][weight], H[a][b]["nama"]) for a, b in pairs] if adjacent else [])
