import time
import random

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

# Main
with open("filelist.txt", "r") as f:
    files = [line.strip() for line in f if line.strip()]

print(f"Total de arquivos lidos: {len(files)}")

algoritmos = [
    ("Bubble Sort", bubble_sort),
    ("Selection Sort", selection_sort),
    ("Insertion Sort", insertion_sort),
]

with open("tempos_ordenacao.txt", "w") as log:
    for nome, func in algoritmos:
        lista = files[:]
        
        inicio = time.perf_counter()
        func(lista)
        fim = time.perf_counter()
        
        duracao = fim - inicio
        log.write(f"{nome}: {duracao:.4f} segundos\n")
        print(f"{nome}: {duracao:.4f} s")

print("Tempos salvos em tempos_ordenacao.txt")