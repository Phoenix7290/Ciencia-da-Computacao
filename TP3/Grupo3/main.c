#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <omp.h>

#include "quadtree.h"


int *qt_contar_vizinhos_paralelo(No *raiz, Ponto *pts, int n,
                                  double raio, int n_threads);



static double tempo_agora(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void gerar_particulas(Ponto *pts, int n) {
    unsigned int seed = 2024;
    for (int i = 0; i < n; i++) {
        pts[i].x  = ((double)rand_r(&seed) / RAND_MAX) * ESPACO;
        pts[i].y  = ((double)rand_r(&seed) / RAND_MAX) * ESPACO;
        pts[i].id = i;
    }
}


static int busca_forca_bruta(Ponto *pts, int n,
                              double cx, double cy, double raio,
                              Ponto *resultado) {
    double r2 = raio * raio;
    int    cnt = 0;
    for (int i = 0; i < n; i++) {
        double dx = pts[i].x - cx, dy = pts[i].y - cy;
        if (dx*dx + dy*dy <= r2)
            resultado[cnt++] = pts[i];
    }
    return cnt;
}

static int cmp_id(const void *a, const void *b) {
    return ((Ponto *)a)->id - ((Ponto *)b)->id;
}



int main(int argc, char *argv[]) {

    int n_threads = 8;
    if (argc > 1) n_threads = atoi(argv[1]);
    if (n_threads < 1) n_threads = 1;

    printf("\n");
    printf("            QUADTREE 2D  —  SIMULAÇÃO DE PARTÍCULAS          \n");
    printf("\n");
    printf("  Espaço      : %.0f x %.0f                                   \n",
           ESPACO, ESPACO);
    printf("  Partículas  : %d                                         \n",
           N_PARTICULAS);
    printf("  Cap. nó     : %d pontos                                   \n",
           CAPACIDADE);
    printf("  Task cutoff : profundidade %d                               \n",
           TASK_CUTOFF_PROF);
    printf("  Threads     : %d                                            \n",
           n_threads);
    printf("\n\n");

    
    printf("[1/5] Gerando %d partículas...\n", N_PARTICULAS);
    Ponto *pts = (Ponto *)malloc((size_t)N_PARTICULAS * sizeof(Ponto));
    if (!pts) { perror("malloc pts"); return 1; }
    gerar_particulas(pts, N_PARTICULAS);
    printf("      OK\n\n");

    
    printf("[2/5] Construção SEQUENCIAL da QuadTree...\n");
    No    *raiz_seq = qt_criar_raiz();
    double t0       = tempo_agora();
    for (int i = 0; i < N_PARTICULAS; i++)
        qt_inserir(raiz_seq, pts[i]);
    double t_build_seq = tempo_agora() - t0;

    int n_nos, altura, n_folhas;
    qt_estatisticas(raiz_seq, &n_nos, &altura, &n_folhas);
    printf("      Tempo      : %.4f s\n", t_build_seq);
    printf("      Nós        : %d\n", n_nos);
    printf("      Folhas     : %d\n", n_folhas);
    printf("      Altura     : %d\n\n", altura);

    
    printf("[3/5] Construção PARALELA da QuadTree (%d threads)...\n", n_threads);
    No *raiz_par = qt_criar_raiz();
    t0 = tempo_agora();
    qt_construir_paralelo(raiz_par, pts, N_PARTICULAS, n_threads);
    double t_build_par = tempo_agora() - t0;

    qt_estatisticas(raiz_par, &n_nos, &altura, &n_folhas);
    printf("      Tempo      : %.4f s\n", t_build_par);
    printf("      Nós        : %d\n", n_nos);
    printf("      Folhas     : %d\n", n_folhas);
    printf("      Altura     : %d\n", altura);
    printf("      Speedup    : %.2fx\n\n", t_build_seq / t_build_par);

    
    double cx   = ESPACO / 2.0;   
    double cy   = ESPACO / 2.0;
    double raio = 50.0;           

    printf("[4/5] Busca de vizinhos em (%.1f, %.1f) raio=%.1f\n", cx, cy, raio);

    Ponto *res_qt = (Ponto *)malloc((size_t)N_PARTICULAS * sizeof(Ponto));
    Ponto *res_bf = (Ponto *)malloc((size_t)N_PARTICULAS * sizeof(Ponto));
    if (!res_qt || !res_bf) { perror("malloc res"); return 1; }

    
    t0 = tempo_agora();
    int cnt_bf = busca_forca_bruta(pts, N_PARTICULAS, cx, cy, raio, res_bf);
    double t_bf = tempo_agora() - t0;

    
    t0 = tempo_agora();
    int cnt_seq = qt_buscar_raio(raiz_par, cx, cy, raio, res_qt, N_PARTICULAS);
    double t_qt_seq = tempo_agora() - t0;

    
    qsort(res_qt, (size_t)cnt_seq, sizeof(Ponto), cmp_id);
    qsort(res_bf, (size_t)cnt_bf,  sizeof(Ponto), cmp_id);
    int valido = (cnt_seq == cnt_bf);
    if (valido)
        for (int i = 0; i < cnt_seq; i++)
            if (res_qt[i].id != res_bf[i].id) { valido = 0; break; }

    printf("      Força bruta : %d vizinhos em %.6f s\n", cnt_bf, t_bf);
    printf("      QuadTree    : %d vizinhos em %.6f s\n", cnt_seq, t_qt_seq);
    printf("      Speedup     : %.1fx\n", t_bf / t_qt_seq);
    printf("      Validação   : %s\n\n", valido ? " CORRETO" : " INCORRETO");

    
    printf("[5/5] Buscando vizinhos de TODAS as %d partículas (raio=%.1f)...\n",
           N_PARTICULAS, raio);

    
    t0 = tempo_agora();
    int *cont_seq = (int *)malloc((size_t)N_PARTICULAS * sizeof(int));
    {
        Ponto *tmp = (Ponto *)malloc((size_t)N_PARTICULAS * sizeof(Ponto));
        for (int i = 0; i < N_PARTICULAS; i++)
            cont_seq[i] = qt_buscar_raio(raiz_par, pts[i].x, pts[i].y,
                                          raio, tmp, N_PARTICULAS);
        free(tmp);
    }
    double t_all_seq = tempo_agora() - t0;

    
    t0 = tempo_agora();
    int *cont_par = qt_contar_vizinhos_paralelo(raiz_par, pts, N_PARTICULAS,
                                                raio, n_threads);
    double t_all_par = tempo_agora() - t0;

    
    int consistente = 1;
    long long total_viz = 0;
    for (int i = 0; i < N_PARTICULAS; i++) {
        total_viz += cont_par[i];
        if (cont_par[i] != cont_seq[i]) { consistente = 0; }
    }

    printf("      Seq  : %.3f s\n", t_all_seq);
    printf("      Par  : %.3f s  (%d threads)\n", t_all_par, n_threads);
    printf("      Speedup      : %.2fx\n", t_all_seq / t_all_par);
    printf("      Vizinhanças  : %lld pares encontrados\n", total_viz);
    printf("      Consistência : %s\n\n",
           consistente ? " CORRETO" : " INCORRETO");

    
    printf("\n");
    printf("                        RESUMO FINAL                         \n");
    printf("\n");
    printf("  Construção seq     : %7.4f s                             \n", t_build_seq);
    printf("  Construção par     : %7.4f s  (speedup %.2fx)           \n",
           t_build_par, t_build_seq / t_build_par);
    printf("  Busca única (QT)   : %7.6f s  (speedup vs BF: %.1fx)  \n",
           t_qt_seq, t_bf / t_qt_seq);
    printf("  Busca N partic seq : %7.3f s                             \n", t_all_seq);
    printf("  Busca N partic par : %7.3f s  (speedup %.2fx)           \n",
           t_all_par, t_all_seq / t_all_par);
    printf("\n");

    
    free(pts); free(res_qt); free(res_bf);
    free(cont_seq); free(cont_par);
    qt_liberar(raiz_seq);
    qt_liberar(raiz_par);

    return (valido && consistente) ? EXIT_SUCCESS : EXIT_FAILURE;
}