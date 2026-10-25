from heapq import heappop, heappush


class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
        self.largest = 1 if n > 0 else 0

    def find(self, i):
        root = i
        while self.parent[root] != root:
            root = self.parent[root]
        curr = i
        while curr != root:
            nxt = self.parent[curr]
            self.parent[curr] = root
            curr = nxt
        return root

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)
        if root_u == root_v:
            return False
        if self.size[root_u] < self.size[root_v]:
            root_u, root_v = root_v, root_u
        self.parent[root_v] = root_u
        self.size[root_u] += self.size[root_v]
        self.components -= 1
        if self.size[root_u] > self.largest:
            self.largest = self.size[root_u]
        return True


def dsu(request):
    n = request["n"]
    ops = request["operations"]
    d = DSU(n)
    states = []
    for u, v in ops:
        d.union(u, v)
        states.append([d.components, d.largest])
    return {"states": states}


def kruskal(request):
    n = request["n"]
    edges = request["edges"]
    d = DSU(n)
    cost = 0
    edge_ids = []
    sorted_edges = sorted((w, idx, u, v) for idx, (u, v, w) in enumerate(edges))
    for w, idx, u, v in sorted_edges:
        if d.union(u, v):
            cost += w
            edge_ids.append(idx)
    return {"cost": cost, "edge_ids": edge_ids, "components": d.components}


def prim(request):
    n = request["n"]
    edges = request["edges"]
    adj = [[] for _ in range(n)]
    for idx, (u, v, w) in enumerate(edges):
        adj[u].append((w, idx, v))
        adj[v].append((w, idx, u))

    visited = [False] * n
    cost = 0
    edge_ids = []
    components = 0

    for i in range(n):
        if visited[i]:
            continue
        components += 1
        visited[i] = True
        heap = []
        for w, idx, to in adj[i]:
            heappush(heap, (w, idx, to))

        while heap:
            w, idx, u = heappop(heap)
            if visited[u]:
                continue
            visited[u] = True
            cost += w
            edge_ids.append(idx)
            for nw, nidx, to in adj[u]:
                if not visited[to]:
                    heappush(heap, (nw, nidx, to))

    return {"cost": cost, "edge_ids": edge_ids, "components": components}


def _dfs_topo(adj, detect_cycle=False):
    n = len(adj)
    color = [0] * n  # 0: white, 1: gray, 2: black
    order = []

    for start in range(n):
        if color[start] != 0:
            continue
        color[start] = 1
        stack = [[start, 0]]
        while stack:
            u, i = stack[-1]
            if i < len(adj[u]):
                v = adj[u][i]
                stack[-1][1] = i + 1
                if color[v] == 0:
                    color[v] = 1
                    stack.append([v, 0])
                elif detect_cycle and color[v] == 1:
                    return True, []
            else:
                color[u] = 2
                order.append(u)
                stack.pop()

    order.reverse()
    return False, order


def scc(request):
    n = request["n"]
    edges = request["edges"]
    adj = [[] for _ in range(n)]
    rev = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        rev[v].append(u)

    _, finish_order = _dfs_topo(adj, detect_cycle=False)

    component = [-1] * n
    label = 0
    for u in finish_order:
        if component[u] != -1:
            continue
        component[u] = label
        stack = [u]
        while stack:
            curr = stack.pop()
            for v in rev[curr]:
                if component[v] == -1:
                    component[v] = label
                    stack.append(v)
        label += 1

    cond = set()
    for u, v in edges:
        cu, cv = component[u], component[v]
        if cu != cv:
            cond.add((cu, cv))

    return {
        "component": component,
        "condensation": [list(p) for p in sorted(cond)]
    }


def topo(request):
    n = request["n"]
    adj = [[] for _ in range(n)]
    for u, v in request["edges"]:
        adj[u].append(v)

    has_cycle, order = _dfs_topo(adj, detect_cycle=True)
    if has_cycle:
        return {"acyclic": False, "order": []}
    return {"acyclic": True, "order": order}


def reconstruct_route(parent_edge, edges, source, target):
    if target == source:
        return [source]
    route = []
    curr = target
    seen = set()
    while curr != source:
        if curr in seen or not (0 <= curr < len(parent_edge)):
            return []
        seen.add(curr)
        e_idx = parent_edge[curr]
        if not (0 <= e_idx < len(edges)):
            return []
        u, v, _ = edges[e_idx]
        if v != curr:
            return []
        route.append(curr)
        curr = u
    route.append(source)
    route.reverse()
    return route


def dag(request):
    n = request["n"]
    source = request["source"]
    edges = request["edges"]

    adj = [[] for _ in range(n)]
    out_edges = [[] for _ in range(n)]
    for idx, (u, v, w) in enumerate(edges):
        adj[u].append(v)
        out_edges[u].append((v, w, idx))

    has_cycle, order = _dfs_topo(adj, detect_cycle=True)
    if has_cycle:
        return {"acyclic": False, "distance": [], "parent_edge": []}

    dist = [None] * n
    parent_edge = [-1] * n
    dist[source] = 0

    for u in order:
        if dist[u] is None:
            continue
        for v, w, idx in out_edges[u]:
            new_dist = dist[u] + w
            if dist[v] is None or new_dist < dist[v]:
                dist[v] = new_dist
                parent_edge[v] = idx

    return {
        "acyclic": True,
        "distance": dist,
        "parent_edge": parent_edge
    }
