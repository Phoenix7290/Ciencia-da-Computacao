#include <stdio.h>
#include <math.h>
#include <omp.h>

#define NUM_PASSOS 100000000L

int main(void)
{
    long   i;
    double x;
    double sum   = 0.0;
    double passo;
    double pi;
    double t_inicio, t_fim, tempo_total;

    passo = 1.0 / (double)NUM_PASSOS;

    printf("============================================================\n");
    printf("  Cálculo de π via integração numérica com OpenMP\n");
    printf("============================================================\n");
    printf("  Número de passos : %ld\n", NUM_PASSOS);
    printf("  Threads ativas   : %d\n", omp_get_max_threads());
    printf("------------------------------------------------------------\n");

    t_inicio = omp_get_wtime();

    #pragma omp parallel for private(x) reduction(+:sum)
    for (i = 0; i < NUM_PASSOS; i++) {
        x = (i + 0.5) * passo;
        sum += 4.0 / (1.0 + x * x);
    }

    pi = passo * sum;

    t_fim      = omp_get_wtime();
    tempo_total = t_fim - t_inicio;

    printf("  π calculado      : %.15f\n", pi);
    printf("  π real (math.h)  : %.15f\n", M_PI);
    printf("  Erro absoluto    : %.2e\n",  fabs(pi - M_PI));
    printf("  Tempo de execução: %.4f segundos\n", tempo_total);
    printf("============================================================\n\n");

    printf("Para comparar speedup:\n");
    printf("  export OMP_NUM_THREADS=1 ; ./q1_pi_openmp\n");
    printf("  export OMP_NUM_THREADS=2 ; ./q1_pi_openmp\n");
    printf("  export OMP_NUM_THREADS=4 ; ./q1_pi_openmp\n");
    printf("  export OMP_NUM_THREADS=8 ; ./q1_pi_openmp\n\n");

    return 0;
}