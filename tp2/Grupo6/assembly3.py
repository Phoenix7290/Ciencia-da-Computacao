import random
import sys
import time
from functools import lru_cache

N = 20
L = 3

sys.setrecursionlimit(50_000)

random.seed()

a = [[random.randint(1, 20) for _ in range(N)] for _ in range(L)]
e = [random.randint(1, 10) for _ in range(L)]
x = [random.randint(1, 10) for _ in range(L)]

t = [
    [
        [0 if frm == to else random.randint(1, 10) for _ in range(N)]
        for to in range(L)
    ]
    for frm in range(L)
]

def fastest_pure(i: int, j: int) -> int:
    if j == 0:
        return e[i] + a[i][0]

    return min(
        fastest_pure(k, j - 1) + t[k][i][j - 1] + a[i][j]
        for k in range(L)
    )


def solve_pure() -> tuple[int, int]:
    costs = [fastest_pure(i, N - 1) + x[i] for i in range(L)]
    best  = min(range(L), key=lambda i: costs[i])
    return costs[best], best


def best_prev_pure(i: int, j: int) -> int:
    return min(
        range(L),
        key=lambda k: fastest_pure(k, j - 1) + t[k][i][j - 1]
    )


def reconstruct_pure(i: int, j: int) -> list[tuple[int, int]]:
    if j == 0:
        return [(0, i)]
    return reconstruct_pure(best_prev_pure(i, j), j - 1) + [(j, i)]

@lru_cache(maxsize=None)
def fastest_memo(i: int, j: int) -> int:
    if j == 0:
        return e[i] + a[i][0]

    return min(
        fastest_memo(k, j - 1) + t[k][i][j - 1] + a[i][j]
        for k in range(L)
    )


def solve_memo() -> tuple[int, int]:
    costs = [fastest_memo(i, N - 1) + x[i] for i in range(L)]
    best  = min(range(L), key=lambda i: costs[i])
    return costs[best], best


def best_prev_memo(i: int, j: int) -> int:
    return min(
        range(L),
        key=lambda k: fastest_memo(k, j - 1) + t[k][i][j - 1]
    )


def reconstruct_memo(i: int, j: int) -> list[tuple[int, int]]:
    if j == 0:
        return [(0, i)]
    return reconstruct_memo(best_prev_memo(i, j), j - 1) + [(j, i)]

def print_params() -> None:
    print(f"=== Linha de Montagem (3 linhas, {N} estações) ===\n")

    entradas = "  ".join(f"e{i+1}={e[i]}" for i in range(L))
    saidas   = "  ".join(f"x{i+1}={x[i]}" for i in range(L))
    print(f"Tempos de entrada : {entradas}")
    print(f"Tempos de saída   : {saidas}\n")

    print("Tempos de montagem  a[linha][estação]:")
    for i in range(L):
        vals = "  ".join(f"{v:2d}" for v in a[i])
        print(f"  Linha {i+1}: {vals}")

    print("\nTempos de transferência  t[de][para][estação]:")
    for frm in range(L):
        for to in range(L):
            if frm == to:
                continue
            vals = "  ".join(f"{t[frm][to][j]:2d}" for j in range(N - 1))
            print(f"  L{frm+1}->L{to+1}: {vals}   (-)")
    print()

if __name__ == "__main__":
    print_params()

    print("--- [Versão com lru_cache] Calculando... ---\n")

    t0 = time.perf_counter()
    min_time_memo, exit_memo = solve_memo()
    path_memo = reconstruct_memo(exit_memo, N - 1)
    t1 = time.perf_counter()

    print("Caminho ótimo (memoização):")
    for station, line in path_memo:
        print(f"  Estação {station+1:2d}  ->  Linha {line+1}")

    cache_info = fastest_memo.cache_info()
    print(f"\nTempo mínimo total : {min_time_memo}")
    print(f"Tempo de execução  : {(t1 - t0)*1000:.3f} ms")
    print(f"Cache hits         : {cache_info.hits}  |  misses: {cache_info.misses}")

    print("\n" + "=" * 55)
    print("--- [Versão recursão pura] ---")
    print("  AVISO: O(3^20) ≈ 3.5 bi chamadas.")
    print("  Estimativa: 12 a 60 minutos dependendo da máquina.")
    print("  Pressione Ctrl+C para cancelar.\n")

    try:
        t2 = time.perf_counter()
        min_time_pure, exit_pure = solve_pure()
        path_pure = reconstruct_pure(exit_pure, N - 1)
        t3 = time.perf_counter()

        print("Caminho ótimo (recursão pura):")
        for station, line in path_pure:
            print(f"  Estação {station+1:2d}  ->  Linha {line+1}")

        print(f"\nTempo mínimo total : {min_time_pure}")
        print(f"Tempo de execução  : {(t3 - t2):.2f} s")

        match = "✓ iguais" if min_time_memo == min_time_pure else "✗ divergem"
        print(f"Conferência memo vs pura: {match}")

    except KeyboardInterrupt:
        print("\n  Execução pura cancelada pelo usuário.")
