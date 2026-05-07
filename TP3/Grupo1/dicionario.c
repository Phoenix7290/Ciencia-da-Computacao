#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PALAVRA   100
#define MAX_SIGNIFICADO 500


typedef struct No {
    char palavra[MAX_PALAVRA];
    char significado[MAX_SIGNIFICADO];
    int altura;
    struct No *esq, *dir;
} No;



static int altura(No *n) {
    return n ? n->altura : 0;
}

static int max2(int a, int b) {
    return a > b ? a : b;
}

static void atualizar_altura(No *n) {
    if (n)
        n->altura = 1 + max2(altura(n->esq), altura(n->dir));
}

static int fator_balanceamento(No *n) {
    return n ? altura(n->esq) - altura(n->dir) : 0;
}



static No *rotacao_direita(No *y) {
    No *x  = y->esq;
    No *T2 = x->dir;

    x->dir = y;
    y->esq = T2;

    atualizar_altura(y);
    atualizar_altura(x);
    return x;
}

static No *rotacao_esquerda(No *x) {
    No *y  = x->dir;
    No *T2 = y->esq;

    y->esq = x;
    x->dir = T2;

    atualizar_altura(x);
    atualizar_altura(y);
    return y;
}

static No *balancear(No *n) {
    atualizar_altura(n);
    int fb = fator_balanceamento(n);

    
    if (fb > 1 && fator_balanceamento(n->esq) >= 0)
        return rotacao_direita(n);

    
    if (fb > 1 && fator_balanceamento(n->esq) < 0) {
        n->esq = rotacao_esquerda(n->esq);
        return rotacao_direita(n);
    }

    
    if (fb < -1 && fator_balanceamento(n->dir) <= 0)
        return rotacao_esquerda(n);

    
    if (fb < -1 && fator_balanceamento(n->dir) > 0) {
        n->dir = rotacao_direita(n->dir);
        return rotacao_esquerda(n);
    }

    return n;
}



static No *criar_no(const char *palavra, const char *significado) {
    No *novo = (No *)malloc(sizeof(No));
    if (!novo) { perror("malloc"); exit(EXIT_FAILURE); }
    strncpy(novo->palavra,    palavra,    MAX_PALAVRA   - 1);
    strncpy(novo->significado, significado, MAX_SIGNIFICADO - 1);
    novo->palavra[MAX_PALAVRA - 1]       = '\0';
    novo->significado[MAX_SIGNIFICADO - 1] = '\0';
    novo->altura = 1;
    novo->esq = novo->dir = NULL;
    return novo;
}



No *inserir(No *raiz, const char *palavra, const char *significado) {
    if (!raiz)
        return criar_no(palavra, significado);

    int cmp = strcmp(palavra, raiz->palavra);

    if (cmp < 0)
        raiz->esq = inserir(raiz->esq, palavra, significado);
    else if (cmp > 0)
        raiz->dir = inserir(raiz->dir, palavra, significado);
    else {
        
        strncpy(raiz->significado, significado, MAX_SIGNIFICADO - 1);
        raiz->significado[MAX_SIGNIFICADO - 1] = '\0';
        printf("[INFO] Significado de \"%s\" atualizado.\n", palavra);
        return raiz;
    }

    return balancear(raiz);
}



No *buscar(No *raiz, const char *palavra) {
    if (!raiz) return NULL;

    int cmp = strcmp(palavra, raiz->palavra);
    if (cmp == 0) return raiz;
    if (cmp  < 0) return buscar(raiz->esq, palavra);
    return buscar(raiz->dir, palavra);
}



static int listar_rec(No *raiz, int idx) {
    if (!raiz) return idx;
    idx = listar_rec(raiz->esq, idx);
    printf("  %3d. %-20s : %s\n", ++idx, raiz->palavra, raiz->significado);
    idx = listar_rec(raiz->dir, idx);
    return idx;
}

void listar(No *raiz) {
    if (!raiz) { printf("  [Dicionário vazio]\n"); return; }
    listar_rec(raiz, 0);
}



static No *no_minimo(No *n) {
    while (n->esq) n = n->esq;
    return n;
}

No *remover(No *raiz, const char *palavra, int *removido) {
    if (!raiz) { *removido = 0; return NULL; }

    int cmp = strcmp(palavra, raiz->palavra);

    if (cmp < 0)
        raiz->esq = remover(raiz->esq, palavra, removido);
    else if (cmp > 0)
        raiz->dir = remover(raiz->dir, palavra, removido);
    else {
        *removido = 1;
        if (!raiz->esq || !raiz->dir) {
            No *tmp = raiz->esq ? raiz->esq : raiz->dir;
            free(raiz);
            return tmp;
        }
        
        No *suc = no_minimo(raiz->dir);
        snprintf(raiz->palavra,    MAX_PALAVRA,    "%s", suc->palavra);
        snprintf(raiz->significado, MAX_SIGNIFICADO, "%s", suc->significado);
        raiz->dir = remover(raiz->dir, suc->palavra, removido);
    }

    return balancear(raiz);
}



int altura_arvore(No *raiz) {
    return altura(raiz);
}



int contar(No *raiz) {
    if (!raiz) return 0;
    return 1 + contar(raiz->esq) + contar(raiz->dir);
}



void liberar(No *raiz) {
    if (!raiz) return;
    liberar(raiz->esq);
    liberar(raiz->dir);
    free(raiz);
}



static void ler_linha(const char *prompt, char *buf, int tam) {
    printf("%s", prompt);
    fflush(stdout);
    if (fgets(buf, tam, stdin)) {
        buf[strcspn(buf, "\n")] = '\0';
    }
}



int main(void) {
    No  *raiz = NULL;
    int  opcao;
    char palavra[MAX_PALAVRA];
    char significado[MAX_SIGNIFICADO];

    
    raiz = inserir(raiz, "algoritmo",   "Sequência finita de instruções para resolver um problema.");
    raiz = inserir(raiz, "compilador",  "Programa que traduz código-fonte para linguagem de máquina.");
    raiz = inserir(raiz, "arvore",      "Estrutura de dados hierárquica composta por nós.");
    raiz = inserir(raiz, "balanceamento","Processo de manter a árvore com alturas similares nos ramos.");
    raiz = inserir(raiz, "recursao",    "Técnica onde uma função chama a si mesma.");

    do {
        printf("\n");
        printf("         DICIONÁRIO AVL (BST)         \n");
        printf("\n");
        printf("  1. Inserir verbete                  \n");
        printf("  2. Buscar verbete                   \n");
        printf("  3. Listar dicionário                \n");
        printf("  4. Remover verbete                  \n");
        printf("  5. Altura da árvore                 \n");
        printf("  6. Número de itens                  \n");
        printf("  0. Sair                             \n");
        printf("\n");
        printf("Opção: ");
        if (scanf("%d", &opcao) != 1) break;
        getchar(); 

        switch (opcao) {

        case 1:
            ler_linha("Palavra   : ", palavra,    sizeof palavra);
            ler_linha("Significado: ", significado, sizeof significado);
            raiz = inserir(raiz, palavra, significado);
            printf("[OK] \"%s\" inserido.\n", palavra);
            break;

        case 2:
            ler_linha("Palavra a buscar: ", palavra, sizeof palavra);
            {
                No *res = buscar(raiz, palavra);
                if (res)
                    printf("  %s : %s\n", res->palavra, res->significado);
                else
                    printf("  [Não encontrado]\n");
            }
            break;

        case 3:
            printf("\n--- Dicionário (ordem alfabética) ---\n");
            listar(raiz);
            break;

        case 4:
            ler_linha("Palavra a remover: ", palavra, sizeof palavra);
            {
                int removido = 0;
                raiz = remover(raiz, palavra, &removido);
                printf(removido ? "  [OK] \"%s\" removido.\n"
                                : "  [Não encontrado] \"%s\".\n", palavra);
            }
            break;

        case 5:
            printf("  Altura da árvore: %d\n", altura_arvore(raiz));
            break;

        case 6:
            printf("  Itens armazenados: %d\n", contar(raiz));
            break;

        case 0:
            printf("Encerrando...\n");
            break;

        default:
            printf("Opção inválida.\n");
        }

    } while (opcao != 0);

    liberar(raiz);
    return 0;
}