# Relatório

## 1. Lógica dos dois programas

O primeiro programa segue este fluxo:
Lê o arquivo `filelist.txt` e converte os dados para lista para aplicar os algoritmos de ordenação (Bubble Sort, Selection Sort e Insertion Sort) e por fim mede o tempo de execução de cada algoritmo.

O segundo programa segue este fluxo:
Lê o arquivo `filelist.txt` e cria três estruturas (`dict`, `list` e `deque`) para recuperar itens em posições específicas, assim, mede tempo e memória e por fim executa operações de adicionar/remover itens.

## 2. Complexidade teórica

Algoritmo | Melhor caso | Caso médio | Pior caso | Espaço
--- | --- | --- | --- | ---
Bubble Sort | O(n) | O(n^2) | O(n^2) | O(1)
Selection Sort | O(n^2) | O(n^2) | O(n^2) | O(1)
Insertion Sort | O(n) | O(n^2) | O(n^2) | O(1)

Estruturas:

Hashtable (`dict`): acesso médio O(1), inserção/remoção O(1) amortizado.
Pilha (`list`): `push/pop` no final O(1), apesar do acesso por índice em listas seja O(1), no experimento foi utilizado um método que remove elementos até atingir a posição desejada, o que resulta em custo linear.
Fila (`deque`): `append/popleft` O(1), acesso por posição k exige operações lineares no método adotado.

## 3. Análise dos resultados (Hashtable, Pilha e Fila)

Com base no `results.txt` (16000 itens), os tempos medidos foram:

Hashtable (`dict`): 0.000003s para recuperar posições [1, 100, 1000, 5000, 16000].
Pilha (`list`): 0.009346s para recuperar as mesmas posições.
Fila (`deque`): 0.008915s para recuperar as mesmas posições.

Interpretação:

Hashtable foi muito mais rápida porque o acesso por chave é praticamente constante (O(1) médio), sem necessidade de percorrer elementos.
Pilha e fila ficaram mais lentas porque o método precisa remover elementos até chegar à posição desejada, o que torna o custo proporcional à distância da posição.
No experimento, pilha e fila tiveram desempenho parecido, pois ambas realizaram varias operacoes lineares para atender as consultas.

Sobre memória (medida com `sys.getsizeof` da estrutura principal):

Hashtable: 589912 bytes.
Pilha: 136632 bytes.
Fila: 132760 bytes.

A hashtable consumiu mais memória por armazenar chaves e valores com maior sobrecarga estrutural, enquanto pilha e fila armazenam apenas a sequência de elementos.

## 4. Resultado consolidado

Estrutura | Tempo de consulta | Memória (bytes) | Add/Remove (tempo)
--- | --- | --- | ---
Hashtable | 0.000003s | 589912 | 0.000714s
Pilha | 0.009346s | 136632 | 0.000003s
Fila | 0.008915s | 132760 | 0.000002s

Conclusão: para consultas por posição/chave, a hashtable é a melhor escolha em desempenho. Para operações de inserção/remoção nas extremidades, pilha e fila mantêm excelente desempenho e menor consumo de memória.
