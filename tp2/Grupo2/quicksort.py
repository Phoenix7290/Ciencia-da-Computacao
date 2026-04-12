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
    pivot_index = median_of_three(arr, low, high)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]

    pivot = arr[high]
    store_index = low - 1

    for j in range(low, high):
        if arr[j] <= pivot:
            store_index += 1
            arr[store_index], arr[j] = arr[j], arr[store_index]
    arr[store_index + 1], arr[high] = arr[high], arr[store_index + 1]
    return store_index + 1

def quicksort(arr: list, low: int, high: int) -> None:
    if low < high:
        pivot_pos = partition(arr, low, high)
        quicksort(arr, low, pivot_pos - 1)
        quicksort(arr, pivot_pos + 1, high)

def sort(arr: list) -> list:
    result = arr[:]
    if len(result) > 1:
        quicksort(result, 0, len(result) - 1)
    return result

def verify_correctness() -> None:
    cases = [
        ([],                    []),
        ([1],                   [1]),
        ([2, 1],                [1, 2]),
        ([3, 1, 2],             [1, 2, 3]),
        ([5, 5, 5],             [5, 5, 5]),
        (list(range(20, 0, -1)), list(range(1, 21))),
        ([1, 2, 3, 4, 5],      [1, 2, 3, 4, 5]),
    ]
    for i, (input_arr, expected) in enumerate(cases):
        result = sort(input_arr)
        assert result == expected, (
            f"Test {i} failed: sort({input_arr}) = {result}, expected {expected}"
        )
    print("  Correção: todos os testes passaram.\n")

def benchmark() -> tuple[list[int], list[float]]:
    TRIALS      = 5
    START_SIZE  = 25
    END_SIZE    = 1000
    STEP        = 25

    sizes  = list(range(START_SIZE, END_SIZE + 1, STEP))
    times  = []

    print(f"  {'Tamanho':>7}  {'Tempo mediano (ms)':>18}  {'Testes':>6}")
    print(f"  {'-'*6}  {'-'*18}  {'-'*6}")

    for size in sizes:
        trial_times = []

        for _ in range(TRIALS):
            arr = random.sample(range(size * 10), size)

            start = time.perf_counter()
            sort(arr)
            end   = time.perf_counter()

            trial_times.append((end - start) * 1000)

        median_time = sorted(trial_times)[TRIALS // 2]
        times.append(median_time)

        print(f"  {size:>6}  {median_time:>17.4f}ms")

    return sizes, times

def plot_results(sizes: list[int], times: list[float]) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    n   = np.array(sizes)
    t   = np.array(times)
    ax.plot(n, t,
            color="#2563EB", linewidth=2, marker="o", markersize=4,
            label="Tempo medido (mediana de 5 testes)")

    theoretical = n * np.log2(n)
    scale       = t[-1] / theoretical[-1]
    ax.plot(n, theoretical * scale,
            color="#DC2626", linewidth=1.8, linestyle="--",
            label=r"Teórico $O(n \log n)$ (escalado)")

    ax.set_title("QuickSort — Benchmark vs. Complexidade Teórica",
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
                xytext=(sizes[max_idx] - 180, t[max_idx] + max(t) * 0.05),
                arrowprops=dict(arrowstyle="->", color="#2563EB"),
                fontsize=9, color="#2563EB")

    plt.tight_layout()
    output_path = "q3_quicksort_benchmark.png"
    plt.savefig(output_path, dpi=150)
    print(f"\n  Gráfico salvo em: {output_path}")
    plt.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  QuickSort — Implementação, Complexidade e Benchmark")
    print("=" * 60)

    print("\n[1] Verificação de correção")
    verify_correctness()

    print("[2] Benchmark (tamanhos 25 → 1000, passo 25)")
    sizes, times = benchmark()

    print("\n[3] Gerando gráfico...")
    plot_results(sizes, times)

    print("\nConcluído.")