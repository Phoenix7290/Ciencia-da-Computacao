import random
import sys

N  = 20
L  = 2

sys.setrecursionlimit(10_000)

random.seed()

a = [[random.randint(1, 20) for _ in range(N)] for _ in range(L)]
t = [[random.randint(1, 10) for _ in range(N)] for _ in range(L)]
e = [random.randint(1, 10) for _ in range(L)]
x = [random.randint(1, 10) for _ in range(L)]

def fastest(i: int, j: int) -> int:
    if j == 0:
        return e[i] + a[i][0]

    other = 1 - i

    stay     = fastest(i,     j - 1) + a[i][j]

    transfer = fastest(other, j - 1) + t[other][j - 1] + a[i][j]

    return min(stay, transfer)


def solve() -> tuple[int, int]:
    costs = [fastest(i, N - 1) + x[i] for i in range(L)]
    best  = min(range(L), key=lambda i: costs[i])
    return costs[best], best


def reconstruct(i: int, j: int) -> list[tuple[int, int]]:
    if j == 0:
        return [(0, i)]

    other    = 1 - i
    stay     = fastest(i,     j - 1)
    transfer = fastest(other, j - 1) + t[other][j - 1]

    prev_line = i if stay <= transfer else other
    return reconstruct(prev_line, j - 1) + [(j, i)]


def print_params() -> None:
    print(f"=== Linha de Montagem (2 linhas, {N} estações) ===\n")

    print(f"Tempos de entrada : e1={e[0]}  e2={e[1]}")
    print(f"Tempos de saída   : x1={x[0]}  x2={x[1]}\n")

    print("Tempos de montagem  a[linha][estação]:")
    for i in range(L):
        vals = "  ".join(f"{v:2d}" for v in a[i])
        print(f"  Linha {i+1}: {vals}")

    print("\nTempos de transferência  t[linha][estação]:")
    for i in range(L):
        vals = "  ".join(f"{v:2d}" for v in t[i][:N-1])
        print(f"  Linha {i+1}: {vals}   (-)")
    print()


if __name__ == "__main__":
    print_params()

    print("--- Calculando caminho ótimo (recursão pura)... ---\n")

    min_time, exit_line = solve()
    path = reconstruct(exit_line, N - 1)

    print("Caminho ótimo:")
    for station, line in path:
        print(f"  Estação {station+1:2d}  ->  Linha {line+1}")

    print(f"\nTempo mínimo total: {min_time}")
