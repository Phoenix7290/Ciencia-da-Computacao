NUM_CIDADES = 30
CONEXOES = [
    (0, 1, 45, 3), (0, 2, 60, 8), (0, 3, 75, 12), (1, 2, 20, 2), (1, 4, 55, 6),
    (2, 3, 35, 4), (2, 5, 40, 5), (3, 6, 80, 10), (4, 5, 15, 1), (4, 7, 90, 14),
    (5, 6, 30, 3), (5, 8, 50, 7), (6, 9, 65, 9), (7, 8, 25, 2), (7, 10, 70, 11),
    (8, 9, 45, 5), (8, 11, 60, 8), (9, 12, 85, 13), (10, 11, 15, 1), (10, 13, 50, 6),
    (11, 12, 40, 4), (11, 14, 55, 7), (12, 15, 75, 10), (13, 14, 30, 3), (13, 16, 65, 9),
    (14, 15, 35, 4), (14, 17, 45, 6), (15, 18, 90, 15), (16, 17, 20, 2), (16, 19, 55, 8),
    (17, 18, 40, 5), (17, 20, 60, 9), (18, 21, 80, 12), (19, 20, 25, 3), (19, 22, 70, 11),
    (20, 21, 35, 4), (20, 23, 50, 7), (21, 24, 75, 10), (22, 23, 15, 1), (22, 25, 60, 8),
    (23, 24, 45, 6), (23, 26, 55, 7), (24, 27, 90, 14), (25, 26, 30, 3), (25, 28, 65, 9),
    (26, 27, 40, 5), (26, 29, 70, 11), (27, 29, 50, 6), (28, 29, 25, 2), (0, 4, 110, 18),
    (1, 5, 85, 11), (2, 6, 95, 14), (3, 9, 120, 22), (4, 8, 70, 9), (5, 9, 60, 8),
    (6, 12, 110, 16), (7, 11, 65, 9), (8, 12, 80, 11), (9, 15, 130, 24), (10, 14, 55, 7),
    (11, 15, 70, 9), (12, 18, 115, 19), (13, 17, 60, 8), (14, 18, 75, 10), (15, 21, 140, 25),
    (16, 20, 65, 9), (17, 21, 85, 12), (18, 24, 125, 20), (19, 23, 60, 8), (20, 24, 80, 11),
    (21, 27, 135, 23), (22, 26, 55, 7), (23, 27, 75, 10), (24, 29, 110, 17), (0, 7, 200, 35),
    (3, 12, 180, 28), (10, 19, 150, 22), (13, 22, 140, 21), (16, 25, 160, 26), (1, 8, 95, 13),
    (2, 9, 105, 15), (7, 13, 85, 12), (11, 17, 90, 13), (19, 25, 80, 12), (20, 26, 85, 13)
]


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False 
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal_mst(num_nodes, edges):
    edges_by_custo = sorted(edges, key=lambda e: e[2])

    uf = UnionFind(num_nodes)
    mst_edges = []
    custo_total = 0

    for origem, destino, custo, latencia in edges_by_custo:
        if uf.union(origem, destino):
            mst_edges.append((origem, destino, custo, latencia))
            custo_total += custo
            if len(mst_edges) == num_nodes - 1:
                break 

    return mst_edges, custo_total


def build_adjacency(num_nodes, edges):
    adj = [[] for _ in range(num_nodes)]
    for origem, destino, custo, latencia in edges:
        adj[origem].append((destino, latencia))
        adj[destino].append((origem, latencia))
    return adj


def dijkstra(num_nodes, adj, origem=0):
    INF = float('inf')
    dist = [INF] * num_nodes
    visitado = [False] * num_nodes
    dist[origem] = 0

    for _ in range(num_nodes):
        u, menor = -1, INF
        for v in range(num_nodes):
            if not visitado[v] and dist[v] < menor:
                u, menor = v, dist[v]

        if u == -1:
            break
        visitado[u] = True

        for vizinho, peso in adj[u]:
            if not visitado[vizinho] and dist[u] + peso < dist[vizinho]:
                dist[vizinho] = dist[u] + peso

    return dist


def main():
    print(" ETAPA 1 - INFRAESTRUTURA: ARVORE GERADORA MINIMA (Kruskal)")

    mst_edges, custo_total = kruskal_mst(NUM_CIDADES, CONEXOES)

    print(f"Total de conexoes escolhidas: {len(mst_edges)} "
          f"(esperado: {NUM_CIDADES - 1} para conectar {NUM_CIDADES} cidades sem ciclos)\n")
    print("Conexoes escolhidas (Origem -> Destino | Custo | Latencia):")
    for origem, destino, custo, latencia in mst_edges:
        print(f"  {origem:2d} -> {destino:2d} | Custo: {custo:4d} | Latencia: {latencia:2d} ms")

    print(f"\nCUSTO TOTAL DA REDE: {custo_total}")

    print("\n")
    print(" ETAPA 2 - OPERACAO: LATENCIA MINIMA A PARTIR DA CIDADE 0")
    print(" (usando a rede COMPLETA de conexoes disponiveis)")

    adjacencia_completa = build_adjacency(NUM_CIDADES, CONEXOES)
    latencias = dijkstra(NUM_CIDADES, adjacencia_completa, origem=0)

    for cidade in range(NUM_CIDADES):
        if cidade == 0:
            continue
        print(f"  Cidade 0 -> Cidade {cidade:2d} : {latencias[cidade]} ms")


if __name__ == "__main__":
    main()