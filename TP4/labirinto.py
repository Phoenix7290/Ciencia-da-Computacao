from collections import deque



class Grafo:


    def __init__(self, n_vertices: int):
        self.n   = n_vertices
        self.adj : dict[int, list[int]] = {i: [] for i in range(n_vertices)}
        self.pos : dict[int, tuple[int,int]] = {}

    def adicionar_aresta(self, u: int, v: int) -> None:
        self.adj[u].append(v)
        self.adj[v].append(u)

    def definir_posicao(self, v: int, col: int, lin: int) -> None:
        self.pos[v] = (col, lin)

    def vizinhos(self, v: int) -> list[int]:
        return self.adj[v]

    def __len__(self) -> int:
        return self.n















def construir_labirinto() -> tuple["Grafo", int, int]:

    g = Grafo(36)


    posicoes = {

        0:  (2,  0),
        1:  (5,  0),
        2:  (10, 0),
        3:  (14, 0),
        4:  (17, 0),
        5:  (19, 0),

        6:  (0,  2),
        7:  (2,  2),
        8:  (5,  2),
        9:  (8,  2),
        10: (10, 2),
        11: (14, 2),
        12: (17, 2),
        13: (19, 2),
        14: (0,  4),

        15: (2,  4),
        16: (5,  4),
        17: (8,  4),
        18: (10, 4),
        19: (14, 4),
        20: (17, 4),
        21: (19, 4),
        22: (0,  6),

        23: (2,  6),
        24: (5,  6),
        25: (8,  6),
        26: (10, 6),
        27: (14, 6),
        28: (17, 6),
        29: (19, 6),

        30: (0,  8),
        31: (2,  8),
        32: (5,  8),
        33: (10, 8),
        34: (14, 8),
        35: (19, 10),
    }
    for v, (col, lin) in posicoes.items():
        g.definir_posicao(v, col, lin)


    arestas = [

        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5),

        (0, 7), (1, 8), (2, 10), (3, 11), (4, 12), (5, 13),

        (6, 7), (7, 8), (8, 9), (9, 10), (11, 12), (12, 13),

        (6, 14), (7, 15), (8, 16), (9, 17), (10, 18),
        (11, 19), (12, 20), (13, 21),

        (14, 15), (15, 16), (16, 17), (17, 18),
        (19, 20), (20, 21),

        (14, 22), (15, 23), (16, 24), (17, 25),
        (18, 26), (19, 27), (20, 28), (21, 29),

        (22, 23), (23, 24), (24, 25), (25, 26),
        (27, 28), (28, 29),

        (22, 30), (23, 31), (24, 32), (26, 33),
        (27, 34), (29, 35),

        (30, 31), (31, 32), (33, 34),

        (10, 11), (18, 19), (26, 27), (33, 35),
        (9, 16),  (17, 24), (25, 32),
        (5, 21),  (13, 20), (21, 28),
    ]
    for u, v in arestas:
        g.adicionar_aresta(u, v)

    return g, 0, 35




def dfs(grafo: Grafo, inicio: int, fim: int) -> list[int] | None:

    pilha      : list[int]       = [inicio]
    visitado   : set[int]        = set()
    predecessores: dict[int, int | None] = {inicio: None}

    while pilha:
        v = pilha.pop()

        if v in visitado:
            continue
        visitado.add(v)

        if v == fim:
            return _reconstruir(predecessores, inicio, fim)

        for vizinho in reversed(grafo.vizinhos(v)):
            if vizinho not in visitado:
                pilha.append(vizinho)
                if vizinho not in predecessores:
                    predecessores[vizinho] = v

    return None




def bfs(grafo: Grafo, inicio: int, fim: int) -> list[int] | None:

    fila         : deque[int]        = deque([inicio])
    visitado     : set[int]          = {inicio}
    predecessores: dict[int, int | None] = {inicio: None}

    while fila:
        v = fila.popleft()

        if v == fim:
            return _reconstruir(predecessores, inicio, fim)

        for vizinho in grafo.vizinhos(v):
            if vizinho not in visitado:
                visitado.add(vizinho)
                predecessores[vizinho] = v
                fila.append(vizinho)

    return None




def _reconstruir(pred: dict, inicio: int, fim: int) -> list[int]:

    caminho = []
    v = fim
    while v is not None:
        caminho.append(v)
        v = pred[v]
    caminho.reverse()
    return caminho


def imprimir_caminho(caminho: list[int], grafo: Grafo, rotulo: str) -> None:
    print(f"\n  {rotulo}")
    print(f"  {'─'*56}")
    print(f"  Comprimento (arestas) : {len(caminho) - 1}")
    print(f"  Vértices no caminho   : {len(caminho)}")
    print(f"  Sequência             : {' → '.join(str(v) for v in caminho)}")
    print(f"  Coordenadas (col,lin) :")
    for v in caminho:
        col, lin = grafo.pos[v]
        marcador = " ← ENTRADA" if v == caminho[0] else (" ← SAÍDA" if v == caminho[-1] else "")
        print(f"    V{v:02d}  ({col:2d}, {lin:2d}){marcador}")


def comparar(caminho_dfs: list[int], caminho_bfs: list[int]) -> None:
    print("\n" + "=" * 60)
    print("  COMPARAÇÃO DFS × BFS")
    print("=" * 60)
    headers = f"  {'Métrica':<30} {'DFS':>8} {'BFS':>8}"
    print(headers)
    print("  " + "─" * 50)

    d_arestas = len(caminho_dfs) - 1
    b_arestas = len(caminho_bfs) - 1
    d_vert    = len(caminho_dfs)
    b_vert    = len(caminho_bfs)

    print(f"  {'Arestas percorridas':<30} {d_arestas:>8} {b_arestas:>8}")
    print(f"  {'Vértices no caminho':<30} {d_vert:>8} {b_vert:>8}")
    print(f"  {'Caminho ótimo (menor)?':<30} {'Não':>8} {'Sim':>8}")
    print(f"  {'Estrutura auxiliar':<30} {'Pilha':>8} {'Fila':>8}")
    print(f"  {'Estratégia':<30} {'Profundo':>8} {'Largo':>8}")
    print("  " + "─" * 50)

    if b_arestas < d_arestas:
        ganho = d_arestas - b_arestas
        print(f"\n  BFS encontrou um caminho {ganho} aresta(s) mais curto que o DFS.")
    elif d_arestas < b_arestas:
        ganho = b_arestas - d_arestas
        print(f"\n  DFS encontrou um caminho {ganho} aresta(s) mais curto (incomum).")
    else:
        print(f"\n  Ambos encontraram caminhos de mesmo comprimento ({d_arestas} arestas).")

    print("""
  Análise:
  ─ DFS usa uma pilha (LIFO) e mergulha em profundidade antes de
    retroceder. Encontra um caminho rapidamente, mas não garante
    o caminho mais curto em grafos não ponderados.

  ─ BFS usa uma fila (FIFO) e explora camada por camada (nível a
    nível a partir da origem). Garante o caminho com o menor
    número de arestas — portanto ótimo em grafos não ponderados.

  ─ Em labirintos, BFS é preferível quando se quer o menor
    número de passos; DFS é mais simples e usa menos memória
    em grafos esparsos profundos.
""")




def main() -> None:
    print("=" * 60)
    print("  LABIRINTO — Busca por DFS e BFS")
    print("=" * 60)

    grafo, entrada, saida = construir_labirinto()
    print(f"\n  Vértices : {len(grafo)}")
    print(f"  Entrada  : vértice {entrada}  {grafo.pos[entrada]}")
    print(f"  Saída    : vértice {saida}  {grafo.pos[saida]}")


    caminho_dfs = dfs(grafo, entrada, saida)
    if caminho_dfs:
        imprimir_caminho(caminho_dfs, grafo, "DFS — Depth-First Search (Pilha)")
    else:
        print("\n  DFS: caminho não encontrado.")


    caminho_bfs = bfs(grafo, entrada, saida)
    if caminho_bfs:
        imprimir_caminho(caminho_bfs, grafo, "BFS — Breadth-First Search (Fila)")
    else:
        print("\n  BFS: caminho não encontrado.")


    if caminho_dfs and caminho_bfs:
        comparar(caminho_dfs, caminho_bfs)


if __name__ == "__main__":
    main()
