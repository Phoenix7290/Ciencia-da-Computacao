#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <omp.h>

typedef long long ll;

typedef struct {
    ll    *dados;
    size_t tamanho;
} Lista;



static double tempo_agora(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int cmp_ll(const void *a, const void *b) {
    ll x = *(const ll *)a, y = *(const ll *)b;
    return (x > y) - (x < y);
}

static void gerar_dados(ll *arr, size_t n, unsigned int seed) {
    for (size_t i = 0; i < n; i++)
        arr[i] = (ll)(rand_r(&seed) % ((ll)n * 10));
}

static Lista merge_dois(const Lista *a, const Lista *b) {
    size_t total = a->tamanho + b->tamanho;
    ll *saida = NULL;
    posix_memalign((void **)&saida, 64, total * sizeof(ll));
    size_t i = 0, j = 0, o = 0;
    while (i < a->tamanho && j < b->tamanho)
        saida[o++] = (a->dados[i] <= b->dados[j]) ? a->dados[i++] : b->dados[j++];
    while (i < a->tamanho) saida[o++] = a->dados[i++];
    while (j < b->tamanho) saida[o++] = b->dados[j++];
    return (Lista){ saida, total };
}


static Lista *criar_runs(ll *arr, size_t n, int k) {
    Lista *runs = malloc((size_t)k * sizeof(Lista));
    size_t base = n / (size_t)k;
    for (int i = 0; i < k; i++) {
        size_t tam = base + (i == k - 1 ? n % (size_t)k : 0);
        ll *buf = malloc(tam * sizeof(ll));
        memcpy(buf, arr + (size_t)i * base, tam * sizeof(ll));
        qsort(buf, tam, sizeof(ll), cmp_ll);
        runs[i].dados   = buf;
        runs[i].tamanho = tam;
    }
    return runs;
}


static Lista merge_sequencial(Lista *runs, int k) {
    Lista *atual = malloc((size_t)k * sizeof(Lista));
    memcpy(atual, runs, (size_t)k * sizeof(Lista));
    int n = k;
    while (n > 1) {
        int pares = n / 2;
        Lista *prox = malloc(((size_t)pares + (size_t)(n % 2)) * sizeof(Lista));
        for (int i = 0; i < pares; i++) {
            prox[i] = merge_dois(&atual[i*2], &atual[i*2+1]);
            free(atual[i*2].dados);
            free(atual[i*2+1].dados);
        }
        if (n % 2) prox[pares] = atual[n-1];
        free(atual);
        atual = prox;
        n = pares + (n % 2);
    }
    Lista r = atual[0];
    free(atual);
    return r;
}


static Lista merge_paralelo(Lista *runs, int k, int threads) {
    Lista *atual = malloc((size_t)k * sizeof(Lista));
    memcpy(atual, runs, (size_t)k * sizeof(Lista));
    int n = k;

    #pragma omp parallel num_threads(threads)
    #pragma omp single
    {
        while (n > 1) {
            int pares = n / 2;
            Lista *prox = malloc(((size_t)pares + (size_t)(n%2)) * sizeof(Lista));
            for (int i = 0; i < pares; i++) {
                int idx = i;
                #pragma omp task firstprivate(idx) shared(atual, prox)
                {
                    Lista r = merge_dois(&atual[idx*2], &atual[idx*2+1]);
                    free(atual[idx*2].dados);
                    free(atual[idx*2+1].dados);
                    prox[idx] = r;
                }
            }
            if (n % 2) prox[pares] = atual[n-1];
            #pragma omp taskwait
            free(atual);
            atual = prox;
            n = pares + (n % 2);
        }
    }
    Lista r = atual[0];
    free(atual);
    return r;
}

static int validar(const Lista *r, size_t n) {
    if (r->tamanho != n) return 0;
    for (size_t i = 1; i < r->tamanho; i++)
        if (r->dados[i] < r->dados[i-1]) return 0;
    return 1;
}


int main(void) {
    const size_t N = 4000000;
    const int Ks[] = { 8, 16, 32 };
    const int Ts[] = { 2, 4, 8 };
    const int nK = 3, nT = 3;

    printf("\n");
    printf("           BENCHMARK  K-WAY MERGE  (N = %7zu)             \n", N);
    printf("\n");
    printf("   K   |  Seq(s)  |  T=%-2d(s) |  T=%-2d(s) |  T=%-2d(s)           \n",
           Ts[0], Ts[1], Ts[2]);
    printf("\n");

    ll *arr = malloc(N * sizeof(ll));
    gerar_dados(arr, N, 42);

    for (int ki = 0; ki < nK; ki++) {
        int K = Ks[ki];
        Lista *runs_base = criar_runs(arr, N, K);

        
        Lista *runs_seq = malloc((size_t)K * sizeof(Lista));
        for (int i = 0; i < K; i++) {
            runs_seq[i].dados   = malloc(runs_base[i].tamanho * sizeof(ll));
            runs_seq[i].tamanho = runs_base[i].tamanho;
            memcpy(runs_seq[i].dados, runs_base[i].dados,
                   runs_base[i].tamanho * sizeof(ll));
        }
        double t0 = tempo_agora();
        Lista rs = merge_sequencial(runs_seq, K);
        double t_seq = tempo_agora() - t0;
        int ok = validar(&rs, N);
        free(rs.dados);
        free(runs_seq);

        printf("  %3d  | %7.3f%c ", K, t_seq, ok ? ' ' : '!');

        
        for (int ti = 0; ti < nT; ti++) {
            int T = Ts[ti];
            Lista *runs_par = malloc((size_t)K * sizeof(Lista));
            for (int i = 0; i < K; i++) {
                runs_par[i].dados   = malloc(runs_base[i].tamanho * sizeof(ll));
                runs_par[i].tamanho = runs_base[i].tamanho;
                memcpy(runs_par[i].dados, runs_base[i].dados,
                       runs_base[i].tamanho * sizeof(ll));
            }
            t0 = tempo_agora();
            Lista rp = merge_paralelo(runs_par, K, T);
            double t_par = tempo_agora() - t0;
            ok = validar(&rp, N);
            free(rp.dados);
            free(runs_par);

            double speedup = t_seq / t_par;
            if (ti < nT - 1)
                printf(" %7.3f%c ", t_par, ok ? ' ' : '!');
            else
                printf(" %7.3f%c  Speedup=%.2fx \n", t_par, ok ? ' ' : '!', speedup);
        }

        
        for (int i = 0; i < K; i++) free(runs_base[i].dados);
        free(runs_base);
    }

    printf("\n");
    printf("Legenda: '!' = resultado incorreto\n");

    free(arr);
    return 0;
}