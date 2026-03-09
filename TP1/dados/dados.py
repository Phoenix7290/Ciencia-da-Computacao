import sys
import time
from collections import deque
import copy

def measure_memory(structure):
    return sys.getsizeof(structure)

def retrieve_positions_hashtable(hashtable, positions):
    results = {}
    start_time = time.perf_counter()
    for pos in positions:
        if pos in hashtable:
            results[pos] = hashtable[pos]
    elapsed = time.perf_counter() - start_time
    memory = measure_memory(hashtable)
    return results, elapsed, memory

def retrieve_positions_stack(stack_original, positions, total_items):
    stack = copy.deepcopy(stack_original)
    results = {}
    start_time = time.perf_counter()
    
    if total_items in positions:
        results[total_items] = stack[-1] if stack else None
    
    for pos in sorted(positions, reverse=True):
        if pos == total_items:
            continue
        pops_needed = total_items - pos
        for _ in range(pops_needed):
            if stack:
                stack.pop()
        if stack:
            results[pos] = stack.pop()
        stack = copy.deepcopy(stack_original)
    
    elapsed = time.perf_counter() - start_time
    memory = measure_memory(stack_original)
    return results, elapsed, memory

def retrieve_positions_queue(queue_original, positions):
    queue = copy.deepcopy(queue_original)
    results = {}
    start_time = time.perf_counter()
    
    if 1 in positions:
        results[1] = queue[0] if queue else None
    
    for pos in sorted(positions):
        if pos == 1:
            continue
        dequeues_needed = pos - 1
        for _ in range(dequeues_needed):
            if queue:
                queue.popleft()
        if queue:
            results[pos] = queue.popleft()
        queue = copy.deepcopy(queue_original)
    
    elapsed = time.perf_counter() - start_time
    memory = measure_memory(queue_original)
    return results, elapsed, memory

def add_remove_items(structure, structure_type, items_to_add, items_to_remove):
    start_time = time.perf_counter()
    memory_initial = measure_memory(structure)
    
    if structure_type == 'hashtable':
        max_key = max(structure.keys()) if structure else 0
        for i, item in enumerate(items_to_add, 1):
            structure[max_key + i] = item
    elif structure_type == 'stack':
        for item in items_to_add:
            structure.append(item) 
    elif structure_type == 'queue':
        for item in items_to_add:
            structure.append(item) 
    
    for _ in range(len(items_to_remove)):
        if structure_type == 'hashtable' and structure:
            structure.pop(max(structure.keys()))
        elif structure_type == 'stack' and structure:
            structure.pop()  
        elif structure_type == 'queue' and structure:
            structure.popleft() 
    
    elapsed = time.perf_counter() - start_time
    memory_final = measure_memory(structure)
    return elapsed, memory_initial, memory_final

input_file = 'filelist.txt'          
positions = [1, 100, 1000, 5000]        
items_to_add = ['new_file1.txt', 'new_file2.txt', 'new_file3.txt', 'new_file4.txt', 'new_file5.txt']
items_to_remove = items_to_add           

with open(input_file, 'r') as f:
    files = [line.strip() for line in f if line.strip()]

total_items = len(files)
positions.append(total_items)  

hashtable = {i+1: file for i, file in enumerate(files)}

stack = []
for file in files:
    stack.append(file)

queue = deque()
for file in files:
    queue.append(file)

results_hashtable, time_hash, mem_hash = retrieve_positions_hashtable(hashtable, positions)
results_stack, time_stack, mem_stack = retrieve_positions_stack(stack, positions, total_items)
results_queue, time_queue, mem_queue = retrieve_positions_queue(queue, positions)

time_addrem_hash, mem_init_hash, mem_final_hash = add_remove_items(hashtable, 'hashtable', items_to_add, items_to_remove)
time_addrem_stack, mem_init_stack, mem_final_stack = add_remove_items(stack, 'stack', items_to_add, items_to_remove)
time_addrem_queue, mem_init_queue, mem_final_queue = add_remove_items(queue, 'queue', items_to_add, items_to_remove)

with open('results.txt', 'w') as log:
    log.write("Resultados da Tabela Hash:\n")
    log.write(f"{results_hashtable}\nTempo: {time_hash:.6f}s | Memoria: {mem_hash} bytes\n")
    log.write(f"Adicionar/Remover: Tempo {time_addrem_hash:.6f}s | Memoria Inicial {mem_init_hash} -> Final {mem_final_hash}\n\n")
    
    log.write("Resultados da Pilha:\n")
    log.write(f"{results_stack}\nTempo: {time_stack:.6f}s | Memoria: {mem_stack} bytes\n")
    log.write(f"Adicionar/Remover: Tempo {time_addrem_stack:.6f}s | Memoria Inicial {mem_init_stack} -> Final {mem_final_stack}\n\n")
    
    log.write("Resultados da Fila:\n")
    log.write(f"{results_queue}\nTempo: {time_queue:.6f}s | Memoria: {mem_queue} bytes\n")
    log.write(f"Adicionar/Remover: Tempo {time_addrem_queue:.6f}s | Memoria Inicial {mem_init_queue} -> Final {mem_final_queue}\n")

print("Execucao concluida. Veja results.txt para detalhes.")