#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#include "quadtree.h"



#define NW 0
#define NE 1
#define SW 2
#define SE 3




static No *criar_no(double x_min, double x_max,
                    double y_min, double y_max, int prof) {
    No *n = (No *)malloc(sizeof(No));
    if (!n) { perror("malloc No"); exit(EXIT_FAILURE); }

    n->x_min = x_min; n->x_max = x_max;
    n->y_min = y_min; n->y_max = y_max;
    n->profundidade = prof;
    n->n_pontos = 0;
    n->capacidade_alocada = CAPACIDADE;

    
    if (posix_memalign((void **)&n->pontos, 64,
                       (size_t)CAPACIDADE * sizeof(Ponto)) != 0) {
        perror("posix_memalign"); exit(EXIT_FAILURE);
    }

    for (int i = 0; i < 4; i++) n->filhos[i] = NULL;
    omp_init_lock(&n->lock);
    return n;
}


static inline int quadrante(No *n, double x, double y) {
    double mx = (n->x_min + n->x_max) * 0.5;
    double my = (n->y_min + n->y_max) * 0.5;
    int leste = (x >= mx) ? 1 : 0;
    int sul   = (y <  my) ? 2 : 0;   
    return sul | leste;               
}


static void subdividir(No *n) {
    double mx = (n->x_min + n->x_max) * 0.5;
    double my = (n->y_min + n->y_max) * 0.5;
    int    p  = n->profundidade + 1;

    n->filhos[NW] = criar_no(n->x_min, mx,     my, n->y_max, p);
    n->filhos[NE] = criar_no(mx,     n->x_max, my, n->y_max, p);
    n->filhos[SW] = criar_no(n->x_min, mx,     n->y_min, my, p);
    n->filhos[SE] = criar_no(mx,     n->x_max, n->y_min, my, p);
}


static void inserir_seq(No *n, Ponto p) {
    omp_set_lock(&n->lock);

    
    if (n->filhos[0] == NULL && n->n_pontos < CAPACIDADE) {
        n->pontos[n->n_pontos++] = p;
        omp_unset_lock(&n->lock);
        return;
    }

    
    if (n->filhos[0] == NULL) {
        subdividir(n);
        
        for (int i = 0; i < n->n_pontos; i++) {
            int q = quadrante(n, n->pontos[i].x, n->pontos[i].y);
            No *filho = n->filhos[q];
            filho->pontos[filho->n_pontos++] = n->pontos[i];
        }
        n->n_pontos = 0;
        free(n->pontos);
        n->pontos = NULL;
    }

    int q = quadrante(n, p.x, p.y);
    No *destino = n->filhos[q];
    omp_unset_lock(&n->lock);

    
    inserir_seq(destino, p);
}



No *qt_criar_raiz(void) {
    return criar_no(0.0, ESPACO, 0.0, ESPACO, 0);
}

void qt_inserir(No *raiz, Ponto p) {
    inserir_seq(raiz, p);
}


static void construir_task(No *no, Ponto *pts, int n_pts, int prof_task) {

    
    if (n_pts <= CAPACIDADE || prof_task <= 0) {
        for (int i = 0; i < n_pts; i++)
            inserir_seq(no, pts[i]);
        return;
    }

    
    omp_set_lock(&no->lock);
    if (no->filhos[0] == NULL)
        subdividir(no);
    omp_unset_lock(&no->lock);

    
    
    int cnt[4] = {0, 0, 0, 0};
    for (int i = 0; i < n_pts; i++)
        cnt[quadrante(no, pts[i].x, pts[i].y)]++;

    
    Ponto *bufs[4];
    for (int q = 0; q < 4; q++) {
        bufs[q] = (Ponto *)malloc((size_t)(cnt[q] ? cnt[q] : 1) * sizeof(Ponto));
        if (!bufs[q]) { perror("malloc buf"); exit(EXIT_FAILURE); }
        cnt[q] = 0; 
    }
    for (int i = 0; i < n_pts; i++) {
        int q = quadrante(no, pts[i].x, pts[i].y);
        bufs[q][cnt[q]++] = pts[i];
    }

    
    Ponto *b0=bufs[NW]; int c0=cnt[NW]; No *f0=no->filhos[NW];
    Ponto *b1=bufs[NE]; int c1=cnt[NE]; No *f1=no->filhos[NE];
    Ponto *b2=bufs[SW]; int c2=cnt[SW]; No *f2=no->filhos[SW];
    Ponto *b3=bufs[SE]; int c3=cnt[SE]; No *f3=no->filhos[SE];
    int pd = prof_task - 1;

    #pragma omp task firstprivate(b0,c0,f0,pd)
    { construir_task(f0, b0, c0, pd); free(b0); }

    #pragma omp task firstprivate(b1,c1,f1,pd)
    { construir_task(f1, b1, c1, pd); free(b1); }

    #pragma omp task firstprivate(b2,c2,f2,pd)
    { construir_task(f2, b2, c2, pd); free(b2); }

    #pragma omp task firstprivate(b3,c3,f3,pd)
    { construir_task(f3, b3, c3, pd); free(b3); }

    #pragma omp taskwait
}

void qt_construir_paralelo(No *raiz, Ponto *pts, int n, int n_threads) {
    omp_set_num_threads(n_threads);

    #pragma omp parallel
    {
        #pragma omp single nowait
        {
            construir_task(raiz, pts, n, TASK_CUTOFF_PROF);
        }
    }
}




static inline int intersecta(No *n, double cx, double cy, double r) {
    
    double nx = cx < n->x_min ? n->x_min : (cx > n->x_max ? n->x_max : cx);
    double ny = cy < n->y_min ? n->y_min : (cy > n->y_max ? n->y_max : cy);
    double dx = cx - nx, dy = cy - ny;
    return (dx*dx + dy*dy) <= r*r;
}



static int buscar_rec(No *n, double cx, double cy, double r,
                      Ponto *res, int max_res, int encontrados) {
    if (!intersecta(n, cx, cy, r)) return encontrados;

    if (n->filhos[0] == NULL) {
        
        double r2 = r * r;
        for (int i = 0; i < n->n_pontos && encontrados < max_res; i++) {
            double dx = n->pontos[i].x - cx;
            double dy = n->pontos[i].y - cy;
            if (dx*dx + dy*dy <= r2)
                res[encontrados++] = n->pontos[i];
        }
        return encontrados;
    }

    
    for (int q = 0; q < 4; q++) {
        if (n->filhos[q])
            encontrados = buscar_rec(n->filhos[q], cx, cy, r,
                                     res, max_res, encontrados);
    }
    return encontrados;
}

int qt_buscar_raio(No *raiz, double cx, double cy, double raio,
                   Ponto *resultado, int max_resultado) {
    return buscar_rec(raiz, cx, cy, raio, resultado, max_resultado, 0);
}


int qt_buscar_raio_paralelo(No *raiz, double cx, double cy, double raio,
                             Ponto *resultado, int max_resultado, int n_threads) {
    

    
    int *contagens = (int *)calloc((size_t)max_resultado, sizeof(int));
    if (!contagens) { perror("calloc"); exit(EXIT_FAILURE); }

    
    int total = buscar_rec(raiz, cx, cy, raio, resultado, max_resultado, 0);

    free(contagens);
    return total;
}


int *qt_contar_vizinhos_paralelo(No *raiz, Ponto *pts, int n,
                                  double raio, int n_threads) {
    int *contagens = (int *)calloc((size_t)n, sizeof(int));
    if (!contagens) { perror("calloc"); exit(EXIT_FAILURE); }

    
    int max_viz = n; 

    #pragma omp parallel num_threads(n_threads)
    {
        
        Ponto *buf_local = (Ponto *)malloc((size_t)max_viz * sizeof(Ponto));
        if (!buf_local) { perror("malloc buf_local"); exit(EXIT_FAILURE); }

        #pragma omp for schedule(dynamic, 256)
        for (int i = 0; i < n; i++) {
            contagens[i] = buscar_rec(raiz, pts[i].x, pts[i].y,
                                      raio, buf_local, max_viz, 0);
        }

        free(buf_local);
    }

    return contagens;
}



static void estat_rec(No *n, int *nos, int *alt, int *folhas) {
    if (!n) return;
    (*nos)++;
    if (n->filhos[0] == NULL) {
        (*folhas)++;
        if (n->profundidade > *alt) *alt = n->profundidade;
        return;
    }
    for (int q = 0; q < 4; q++)
        estat_rec(n->filhos[q], nos, alt, folhas);
}

void qt_estatisticas(No *raiz, int *n_nos, int *altura, int *n_folhas) {
    *n_nos = *altura = *n_folhas = 0;
    estat_rec(raiz, n_nos, altura, n_folhas);
}



void qt_liberar(No *raiz) {
    if (!raiz) return;
    for (int q = 0; q < 4; q++)
        qt_liberar(raiz->filhos[q]);
    omp_destroy_lock(&raiz->lock);
    if (raiz->pontos) free(raiz->pontos);
    free(raiz);
}