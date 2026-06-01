#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "trie.h"


static long long tempo_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}


typedef struct {
    const char *ip;
    int         esperado;
    const char *explicacao;
} CasoTeste;


int main(void) {

    printf("\n");
    printf("         ROTEADOR LPM — Patricia Trie (IPv4 + IPv6)              \n");
    printf("\n\n");

    
    printf(" [1/4] Montando tabela de roteamento \n\n");

    Trie *t = trie_criar();

    typedef struct { const char *cidr; int id; const char *desc; } Rota;
    Rota rotas[] = {
        { "192.168.0.0/16",  10,  "Rota genérica para rede local"    },
        { "192.168.1.0/24",  20,  "Sub-rede específica 1"            },
        { "192.168.1.128/25",30,  "Sub-rede ainda mais específica"   },
        { "10.0.0.0/8",      40,  "Rede de grande porte"             },
        { "0.0.0.0/0",       50,  "Rota padrão (Default Gateway)"    },
        { "2001:db8::/32",  100,  "Prefixo IPv6 genérico"            },
        { "2001:db8:a::/48",200,  "Sub-rede IPv6 específica"         },
    };
    int n_rotas = (int)(sizeof(rotas) / sizeof(rotas[0]));

    for (int i = 0; i < n_rotas; i++) {
        trie_inserir(t, rotas[i].cidr, rotas[i].id);
        printf("  %-25s → ID %-4d  (%s)\n",
               rotas[i].cidr, rotas[i].id, rotas[i].desc);
    }
    printf("\n");

    
    printf(" [2/4] Estatísticas da Patricia Trie \n\n");
    trie_estatisticas(t);
    printf("\n");

    
    printf(" [3/4] Casos de Teste (LPM Lookup) \n\n");

    CasoTeste testes[] = {
        
        { "192.168.0.50",    10,
          "Coincide só com /16" },
        { "192.168.1.20",    20,
          "Coincide /16 e /24 → /24 vence" },
        { "192.168.1.150",   30,
          "Coincide /16, /24 e /25 → /25 vence" },
        { "10.255.0.1",      40,
          "Coincide com 10.0.0.0/8" },
        { "8.8.8.8",         50,
          "Nenhuma rota específica → default 0.0.0.0/0" },
        
        { "2001:db8:cafe::1",    100,
          "Coincide com prefixo /32" },
        { "2001:db8:a:b::1",     200,
          "Coincide com /48 (mais específico que /32)" },
    };
    int n_testes = (int)(sizeof(testes) / sizeof(testes[0]));

    int acertos = 0;
    printf("  %-26s %-10s %-10s %-8s  %s\n",
           "IP de Destino", "Esperado", "Obtido", "Status", "Explicação");
    printf("  %s\n", "");

    for (int i = 0; i < n_testes; i++) {
        int obtido = trie_lookup(t, testes[i].ip);
        int ok     = (obtido == testes[i].esperado);
        acertos   += ok;

        printf("  %-26s ID=%-6d ID=%-6d %s  %s\n",
               testes[i].ip,
               testes[i].esperado,
               obtido,
               ok ? " OK  " : " FAIL",
               testes[i].explicacao);
    }

    printf("\n  Resultado: %d/%d corretos %s\n\n",
           acertos, n_testes,
           acertos == n_testes ? "— TODOS PASSARAM " : "— HÁ FALHAS ");

    
    printf(" [4/4] Benchmark de Performance \n\n");

    
    const char *ips_bench[] = {
        "192.168.0.50", "192.168.1.20",  "192.168.1.150",
        "10.255.0.1",   "8.8.8.8",
        "2001:db8:cafe::1", "2001:db8:a:b::1"
    };
    int n_ips = (int)(sizeof(ips_bench) / sizeof(ips_bench[0]));

    int N = 1000000; 
    long long t0 = tempo_ns();

    volatile int sink = 0; 
    for (int i = 0; i < N; i++)
        sink += trie_lookup(t, ips_bench[i % n_ips]);

    long long t1 = tempo_ns();
    double elapsed_ms  = (double)(t1 - t0) / 1e6;
    double throughput  = (double)N / ((double)(t1 - t0) / 1e9);
    double ns_por_op   = (double)(t1 - t0) / N;

    printf("  Lookups realizados : %d\n",   N);
    printf("  Tempo total        : %.2f ms\n", elapsed_ms);
    printf("  Throughput         : %.0f lookups/s\n", throughput);
    printf("  Latência média     : %.1f ns/lookup\n\n", ns_por_op);

    
    printf("  Complexidade comparativa:\n");
    printf("  \n");
    printf("   Método               | Complexidade   | Para %d rotas      \n", n_rotas);
    printf("  \n");
    printf("   Varredura linear     | O(N × bits)   | %5d comparações   \n",
           n_rotas * 32);
    printf("   Patricia Trie (LPM)  | O(bits)       | %5d comparações   \n",
           32); 
    printf("  \n\n");

    
    printf("\n");
    printf("                        RESUMO FINAL                             \n");
    printf("\n");
    printf("  Rotas inseridas    : %-5d (IPv4 + IPv6)                       \n", n_rotas);
    printf("  Testes corretos    : %d/%d                                      \n",
           acertos, n_testes);
    printf("  Throughput         : %-10.0f lookups/s                    \n", throughput);
    printf("  Latência média     : %-6.1f ns/lookup                         \n", ns_por_op);
    printf("  Path Compression   : ativa (Patricia Trie)                     \n");
    printf("  IPv6 suportado     : sim (128 bits, comprimidos)               \n");
    printf("\n");

    trie_liberar(t);
    return (acertos == n_testes) ? 0 : 1;
}