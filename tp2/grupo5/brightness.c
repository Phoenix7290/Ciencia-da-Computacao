#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define ROWS 10000
#define COLS 10000
#define BRIGHTNESS 50
#define MAX_PIXEL 255

int main() {
    unsigned char **matrix = (unsigned char **)malloc(ROWS * sizeof(unsigned char *));
    if (!matrix) {
        fprintf(stderr, "Erro ao alocar linhas da matriz.\n");
        return 1;
    }
    for (int i = 0; i < ROWS; i++) {
        matrix[i] = (unsigned char *)malloc(COLS * sizeof(unsigned char));
        if (!matrix[i]) {
            fprintf(stderr, "Erro ao alocar coluna %d.\n", i);
            return 1;
        }
    }

    for (int i = 0; i < ROWS; i++)
        for (int j = 0; j < COLS; j++)
            matrix[i][j] = (unsigned char)(rand() % (MAX_PIXEL + 1));

    double start_seq = omp_get_wtime();

    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            int val = matrix[i][j] + BRIGHTNESS;
            matrix[i][j] = (unsigned char)(val > MAX_PIXEL ? MAX_PIXEL : val);
        }
    }

    double end_seq = omp_get_wtime();
    double time_seq = end_seq - start_seq;

    for (int i = 0; i < ROWS; i++)
        for (int j = 0; j < COLS; j++)
            matrix[i][j] = (unsigned char)(rand() % (MAX_PIXEL + 1));

    double start_par = omp_get_wtime();

    int i, j;
    #pragma omp parallel for shared(matrix) private(i, j) schedule(static)
    for (i = 0; i < ROWS; i++) {
        for (j = 0; j < COLS; j++) {
            int val = matrix[i][j] + BRIGHTNESS;
            matrix[i][j] = (unsigned char)(val > MAX_PIXEL ? MAX_PIXEL : val);
        }
    }

    double end_par = omp_get_wtime();
    double time_par = end_par - start_par;

    printf("=== Ajuste de Brilho em Matriz %dx%d (brilho = %d) ===\n\n",
           ROWS, COLS, BRIGHTNESS);
    printf("Threads disponíveis : %d\n", omp_get_max_threads());
    printf("Tempo sequencial    : %.4f segundos\n", time_seq);
    printf("Tempo paralelo      : %.4f segundos\n", time_par);
    printf("Speedup             : %.2fx\n", time_seq / time_par);

    for (int i = 0; i < ROWS; i++)
        free(matrix[i]);
    free(matrix);

    return 0;
}
