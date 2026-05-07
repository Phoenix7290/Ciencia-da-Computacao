#ifndef QUADTREE_H
#define QUADTREE_H

#include <stddef.h>


#define ESPACO           1000.0   
#define N_PARTICULAS     100000   
#define CAPACIDADE       50       
#define TASK_CUTOFF_PROF 4        


typedef struct {
    double x, y;
    int    id;
} Ponto;


typedef struct No {
    
    double x_min, x_max;
    double y_min, y_max;

    
    struct No *filhos[4];

    
    Ponto  *pontos;
    int     n_pontos;
    int     capacidade_alocada;

    
    int profundidade;

    
    omp_lock_t lock;
} No;




No   *qt_criar_raiz(void);


void  qt_inserir(No *raiz, Ponto p);


void  qt_construir_paralelo(No *raiz, Ponto *pts, int n, int n_threads);


int   qt_buscar_raio(No *raiz, double cx, double cy, double raio,
                     Ponto *resultado, int max_resultado);


int   qt_buscar_raio_paralelo(No *raiz, double cx, double cy, double raio,
                              Ponto *resultado, int max_resultado, int n_threads);


void  qt_estatisticas(No *raiz, int *n_nos, int *altura, int *n_folhas);


void  qt_liberar(No *raiz);

#endif 