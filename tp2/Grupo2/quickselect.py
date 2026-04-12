import random
import time
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

sys.setrecursionlimit(10_000)

def median_of_three(arr: list, low: int, high: int) -> int:
    mid = (low + high) // 2

    if arr[low] > arr[mid]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[low] > arr[high]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[mid] > arr[high]:
        arr[mid], arr[high] = arr[high], arr[mid]

    return mid

def partition(arr: list, low: int, high: int) -> int:
    pivot_idx = median_of_three(arr, low, high)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]

    pivot = arr[high]
    store = low - 1

    for j in range(low, high):
        if arr[j] <= pivot:
            store += 1
            arr[store], arr[j] = arr[j], arr[store]

    arr[store + 1], arr[high] = arr[high], arr[store + 1]
    return store + 1

def quickselect(arr: list, low: int, high: int, k: int) -> int:
    if low == high:
        return arr[low]

    pivot_pos = partition(arr, low, high)

    if pivot_pos == k:
        return arr[pivot_pos]

    elif pivot_pos > k:
        return quickselect(arr, low, pivot_pos - 1, k)

    else:
        return quickselect(arr, pivot_pos + 1, high, k)

def find_kth_smallest(arr: list, k: int) -> int:
    if not arr:
        raise ValueError("Lista vazia.")
    if not (1 <= k <= len(arr)):
        raise ValueError(f"k={k} fora do intervalo [1, {len(arr)}].")

    working_copy = arr[:]
    return quickselect(working_copy, 0, len(working_copy) - 1, k - 1)

def verify_correctness() -> None:
    test_cases = [
        ([3, 1, 2],             1, 1),
        ([3, 1, 2],             3, 3),
        ([3, 1, 2],             2, 2),
        ([5, 5, 5, 5],          2, 5),
        ([7],                   1, 7),
        (list(range(10, 0, -1)), 5, 5),
        ([1, 2, 3, 4, 5],       3, 3),
    ]

    for i, (input_arr, k, expected) in enumerate(test_cases):
        result = find_kth_smallest(input_arr, k)
        assert result == expected, (
            f"Teste {i} falhou: find_kth_smallest({input_arr}, {k}) = {result}, "
            f"esperado {expected}"
        )

    print("  Corretude: todos os testes passaram.\n")

def benchmark() -> tuple[list[int], list[float]]:
    TRIALS     = 5
    START_SIZE = 25
    END_SIZE   = 1000
    STEP       = 25

    sizes = list(range(START_SIZE, END_SIZE + 1, STEP))
    times = []

    print(f"  {'Tamanho':>8}  {'Tempo mediano (ms)':>20}  {'k buscado':>10}")
    print(f"  {'-'*8}  {'-'*20}  {'-'*10}")

    for size in sizes:
        trial_times = []
        last_k = 0

        for _ in range(TRIALS):
            arr    = random.sample(range(size * 10), size)
            last_k = random.randint(1, size)

            start = time.perf_counter()
            find_kth_smallest(arr, last_k)
            end   = time.perf_counter()

            trial_times.append((end - start) * 1000)

        median_time = sorted(trial_times)[TRIALS // 2]
        times.append(median_time)

        print(f"  {size:>8}  {median_time:>19.4f}ms  {last_k:>10}")

    return sizes, times

def plot_results(sizes: list[int], times: list[float]) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    n = np.array(sizes)
    t = np.array(times)

    ax.plot(n, t,
            color="#16A34A", linewidth=2, marker="o", markersize=4,
            label="Tempo medido (mediana de 5 tentativas)")

    theoretical_linear = n.astype(float)
    scale_linear = t[-1] / theoretical_linear[-1]
    ax.plot(n, theoretical_linear * scale_linear,
            color="#DC2626", linewidth=1.8, linestyle="--",
            label=r"Teórico $O(n)$ (escalado)")

    theoretical_nlogn = n * np.log2(n)
    scale_nlogn = t[-1] / theoretical_nlogn[-1]
    ax.plot(n, theoretical_nlogn * scale_nlogn,
            color="#D97706", linewidth=1.4, linestyle=":",
            label=r"Referência $O(n \log n)$ QuickSort (escalado)")

    ax.set_title("QuickSelect — Benchmark vs. Complexidade Teórica",
                 fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Tamanho da entrada (n)", fontsize=12)
    ax.set_ylabel("Tempo de execução (ms)", fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(25))
    ax.set_xlim(0, 1025)
    ax.set_ylim(bottom=0)

    max_idx = int(np.argmax(t))
    ax.annotate(f"n={sizes[max_idx]}\n{t[max_idx]:.3f}ms",
                xy=(sizes[max_idx], t[max_idx]),
                xytext=(sizes[max_idx] - 200, t[max_idx] + max(t) * 0.06),
                arrowprops=dict(arrowstyle="->", color="#16A34A"),
                fontsize=9, color="#16A34A")

    plt.tight_layout()
    output_path = "q4_quickselect_benchmark.png"
    plt.savefig(output_path, dpi=150)
    print(f"\n  Gráfico salvo → {output_path}")
    plt.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  QuickSelect — Implementação, Complexidade e Benchmark")
    print("=" * 60)

    print("\n[1] Verificação de corretude")
    verify_correctness()

    print("[2] Benchmark (tamanhos 25 → 1000, passo 25)")
    sizes, times = benchmark()

    print("\n[3] Gerando gráfico...")
    plot_results(sizes, times)

    print("\nConcluído.")