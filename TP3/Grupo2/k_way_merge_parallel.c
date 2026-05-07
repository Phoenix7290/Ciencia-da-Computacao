#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <omp.h>


typedef long long ll;

typedef struct {
    ll   *dados;
    size_t tamanho;
} Lista;


static void   gerar_dados(ll *arr, size_t n);
static void   criar_runs(ll *arr, size_t n, int k, Lista *runs);
static Lista  merge_dois(const Lista *a, const Lista *b);
static Lista  merge_tree_paralelo(Lista *runs, int k, int threads);
static int    validar(const Lista *resultado, size_t n_esperado);
static double tempo_agora(void);




int main(int argc, char *argv[]) {

    size_t N = 4000000;
    int    K = 16;
    int    T = 8;

    if (argc > 1) N = (size_t)atoll(argv[1]);
    if (argc > 2) K = atoi(argv[2]);
    if (argc > 3) T = atoi(argv[3]);

    
    if (K < 2 || (K & (K - 1)) != 0) {
        fprintf(stderr, "[ERRO] K=%d deve ser uma potência de 2 (ex: 2,4,8,16,32).\n", K);
        return EXIT_FAILURE;
    }
    if (T < 1) T = 1;

    omp_set_num_threads(T);

    printf("\n");
    printf("         K-WAY MERGE PARALELO  (OpenMP Tasks)        \n");
    printf("\n");
    printf("  Elementos : %-10zu                            \n", N);
    printf("  Sublistas : %-10d                            \n", K);
    printf("  Threads   : %-10d                            \n", T);
    printf("  Níveis    : %-10d                            \n", (int)log2(K));
    printf("\n\n");

    
    printf("[1/4] Gerando %zu elementos aleatórios...\n", N);
    double t0 = tempo_agora();

    ll *arr = (ll *)malloc(N * sizeof(ll));
    if (!arr) { perror("malloc"); return EXIT_FAILURE; }
    gerar_dados(arr, N);

    printf("      Concluído em %.3f s\n\n", tempo_agora() - t0);

    
    printf("[2/4] Dividindo em %d sublistas e ordenando cada uma...\n", K);
    t0 = tempo_agora();

    Lista *runs = (Lista *)malloc(K * sizeof(Lista));
    if (!runs) { perror("malloc"); free(arr); return EXIT_FAILURE; }
    criar_runs(arr, N, K, runs);
    free(arr); 

    printf("      Concluído em %.3f s\n\n", tempo_agora() - t0);

    
    printf("[3/4] Executando Merge Tree paralelo...\n");
    t0 = tempo_agora();

    Lista resultado = merge_tree_paralelo(runs, K, T);
    free(runs);

    double t_merge = tempo_agora() - t0;
    printf("      Concluído em %.3f s\n\n", t_merge);

    
    printf("[4/4] Validando resultado...\n");
    int ok = validar(&resultado, N);
    printf("      %s\n\n", ok ? " Array ordenado corretamente" : "✗ ERRO: array NÃO está ordenado!");

    
    printf("\n");
    printf("                    RESULTADOS                       \n");
    printf("\n");
    printf("  Elementos ordenados : %-10zu                  \n", resultado.tamanho);
    printf("  Tempo de merge      : %-10.3f s               \n", t_merge);
    printf("  Throughput          : %-10.2f M elem/s         \n",
           (double)N / t_merge / 1e6);
    printf("  Resultado           : %-10s                  \n", ok ? "CORRETO" : "INCORRETO");
    printf("\n");

    free(resultado.dados);
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
}






static double tempo_agora(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}


static void gerar_dados(ll *arr, size_t n) {
    unsigned int seed = 42;
    for (size_t i = 0; i < n; i++)
        arr[i] = (ll)(rand_r(&seed) % (n * 10));
}


static int cmp_ll(const void *a, const void *b) {
    ll x = *(const ll *)a, y = *(const ll *)b;
    return (x > y) - (x < y);
}


static void criar_runs(ll *arr, size_t n, int k, Lista *runs) {
    size_t base = n / (size_t)k;
    size_t resto = n % (size_t)k;

    
    #pragma omp parallel for schedule(dynamic) num_threads(k < 8 ? k : 8)
    for (int i = 0; i < k; i++) {
        size_t tam = base + (i == k - 1 ? resto : 0);
        ll *buf = (ll *)malloc(tam * sizeof(ll));
        if (!buf) { perror("malloc run"); exit(EXIT_FAILURE); }


        
        size_t off_i = (size_t)i * base;
        memcpy(buf, arr + off_i, tam * sizeof(ll));
        qsort(buf, tam, sizeof(ll), cmp_ll);

        runs[i].dados   = buf;
        runs[i].tamanho = tam;
    }
}


static Lista merge_dois(const Lista *a, const Lista *b) {
    size_t total = a->tamanho + b->tamanho;

    
    ll *saida = NULL;
    if (posix_memalign((void **)&saida, 64, total * sizeof(ll)) != 0) {
        perror("posix_memalign"); exit(EXIT_FAILURE);
    }

    size_t i = 0, j = 0, o = 0;
    while (i < a->tamanho && j < b->tamanho) {
        if (a->dados[i] <= b->dados[j])
            saida[o++] = a->dados[i++];
        else
            saida[o++] = b->dados[j++];
    }
    while (i < a->tamanho) saida[o++] = a->dados[i++];
    while (j < b->tamanho) saida[o++] = b->dados[j++];

    return (Lista){ saida, total };
}


static Lista merge_tree_paralelo(Lista *runs, int k, int threads) {
    
    Lista *atual = (Lista *)malloc((size_t)k * sizeof(Lista));
    if (!atual) { perror("malloc"); exit(EXIT_FAILURE); }
    memcpy(atual, runs, (size_t)k * sizeof(Lista));

    int nivel = 1;
    int n_listas = k;

    #pragma omp parallel num_threads(threads)
    {
        #pragma omp single
        {
            while (n_listas > 1) {
                int pares = n_listas / 2;

                printf("      Nível %d: %2d thread(s) fundem %2d pares "
                       "(%2d → %2d listas)\n",
                       nivel, pares < threads ? pares : threads,
                       pares, n_listas, pares + (n_listas % 2));

                
                Lista *prox = (Lista *)malloc(
                    ((size_t)pares + (size_t)(n_listas % 2)) * sizeof(Lista));
                if (!prox) { perror("malloc"); exit(EXIT_FAILURE); }

                
                for (int i = 0; i < pares; i++) {
                    int idx = i; 
                    #pragma omp task firstprivate(idx) shared(atual, prox)
                    {
                        Lista r = merge_dois(&atual[idx * 2],
                                             &atual[idx * 2 + 1]);
                        
                        free(atual[idx * 2].dados);
                        free(atual[idx * 2 + 1].dados);
                        prox[idx] = r;
                    }
                }

                
                if (n_listas % 2 == 1) {
                    prox[pares] = atual[n_listas - 1];
                }

                
                #pragma omp taskwait

                free(atual);
                atual   = prox;
                n_listas = pares + (n_listas % 2);
                nivel++;
            }
        } 
    } 

    Lista resultado = atual[0];
    free(atual);
    return resultado;
}


static int validar(const Lista *resultado, size_t n_esperado) {
    if (resultado->tamanho != n_esperado) {
        fprintf(stderr, "[VALIDAÇÃO] Tamanho incorreto: esperado %zu, obtido %zu\n",
                n_esperado, resultado->tamanho);
        return 0;
    }
    for (size_t i = 1; i < resultado->tamanho; i++) {
        if (resultado->dados[i] < resultado->dados[i - 1]) {
            fprintf(stderr, "[VALIDAÇÃO] Fora de ordem na posição %zu: "
                    "%lld > %lld\n", i,
                    resultado->dados[i - 1], resultado->dados[i]);
            return 0;
        }
    }
    return 1;
}