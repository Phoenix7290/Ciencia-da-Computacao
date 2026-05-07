#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>   

#include "trie.h"




static inline int bit_em(const uint8_t *buf, int pos) {
    return (buf[pos / 8] >> (7 - (pos % 8))) & 1;
}


static void copiar_bits(uint8_t *dst, const uint8_t *src, int inicio, int len) {
    memset(dst, 0, 16);
    for (int i = 0; i < len; i++) {
        int b = bit_em(src, inicio + i);
        if (b) dst[i / 8] |= (uint8_t)(1 << (7 - (i % 8)));
    }
}




static void skip_para_bytes(const uint64_t *sb, uint8_t *out) {
    
    for (int i = 0; i < 8; i++)
        out[i]     = (uint8_t)((sb[0] >> (56 - 8*i)) & 0xFF);
    for (int i = 0; i < 8; i++)
        out[8 + i] = (uint8_t)((sb[1] >> (56 - 8*i)) & 0xFF);
}

static void bytes_para_skip(const uint8_t *in, int inicio, int len,
                              uint64_t *sb) {
    uint8_t tmp[16] = {0};
    copiar_bits(tmp, in, inicio, len);
    sb[0] = sb[1] = 0;
    for (int i = 0; i < 8; i++)
        sb[0] |= ((uint64_t)tmp[i])     << (56 - 8*i);
    for (int i = 0; i < 8; i++)
        sb[1] |= ((uint64_t)tmp[8 + i]) << (56 - 8*i);
}



typedef struct {
    uint8_t addr[16];   
    int     bits;       
    int     prefixo;    
    int     is_ipv6;
} EnderecoIP;


static int parsear_ip(const char *str, EnderecoIP *out) {
    char copia[128];
    strncpy(copia, str, sizeof(copia) - 1);
    copia[sizeof(copia) - 1] = '\0';

    
    char *barra = strchr(copia, '/');
    int   prefixo = -1;
    if (barra) {
        *barra  = '\0';
        prefixo = atoi(barra + 1);
    }

    memset(out->addr, 0, 16);

    
    if (strchr(copia, ':')) {
        if (inet_pton(AF_INET6, copia, out->addr) != 1) return -1;
        out->bits    = 128;
        out->is_ipv6 = 1;
        out->prefixo = (prefixo >= 0) ? prefixo : 128;
    } else {
        uint8_t tmp4[4];
        if (inet_pton(AF_INET, copia, tmp4) != 1) return -1;
        memcpy(out->addr, tmp4, 4);
        out->bits    = 32;
        out->is_ipv6 = 0;
        out->prefixo = (prefixo >= 0) ? prefixo : 32;
    }

    return 0;
}



static No *criar_no(int skip, const uint8_t *addr, int inicio,
                    int route_id, Trie *t) {
    No *n = (No *)calloc(1, sizeof(No));
    if (!n) { perror("calloc No"); exit(EXIT_FAILURE); }
    n->skip     = skip;
    n->route_id = route_id;
    n->filho[0] = n->filho[1] = NULL;
    if (skip > 0)
        bytes_para_skip(addr, inicio, skip, n->skip_bits);
    t->n_nos++;
    return n;
}



static void inserir_rec(No **ptr, const uint8_t *addr, int pos,
                         int prefixo, int route_id, Trie *t) {
    
    if (*ptr == NULL) {
        int skip = (pos < prefixo) ? (prefixo - pos - 1) : 0;
        No *novo = criar_no(skip, addr, pos, -1, t);
        
        if (pos + skip < prefixo) {
            int prox_bit = bit_em(addr, pos + skip);
            novo->filho[prox_bit] = criar_no(0, addr, 0, route_id, t);
            
        } else {
            novo->route_id = route_id;
        }
        *ptr = novo;
        return;
    }

    No *n = *ptr;

    
    uint8_t skip_bytes[16];
    skip_para_bytes(n->skip_bits, skip_bytes);

    int match = 0; 
    for (match = 0; match < n->skip; match++) {
        if (bit_em(addr, pos + match) != bit_em(skip_bytes, match)) break;
    }

    if (match < n->skip) {
        
        int bit_no   = bit_em(skip_bytes, match);
        int bit_addr = bit_em(addr, pos + match);

        
        No *inter = criar_no(match, addr, pos, -1, t);

        
        int novo_skip = n->skip - match - 1;
        if (novo_skip > 0) {
            uint8_t tmp[16];
            skip_para_bytes(n->skip_bits, tmp);
            bytes_para_skip(tmp, match + 1, novo_skip, n->skip_bits);
        } else {
            n->skip_bits[0] = n->skip_bits[1] = 0;
        }
        n->skip = novo_skip;

        inter->filho[bit_no] = n;

        
        int bits_restantes = prefixo - (pos + match + 1);
        if (bits_restantes > 0) {
            No *folha = criar_no(bits_restantes - 1, addr,
                                  pos + match + 1, -1, t);
            
            int ult_bit = bit_em(addr, pos + match + 1 + folha->skip);
            folha->filho[ult_bit] = criar_no(0, addr, 0, route_id, t);
            inter->filho[bit_addr] = folha;
        } else {
            
            inter->route_id = route_id;
            
            if (bits_restantes == 0 && bit_addr != bit_no) {
                
                (void)bit_addr;
            }
        }

        *ptr = inter;
        return;
    }

    
    pos += n->skip;

    if (pos == prefixo) {
        
        n->route_id = route_id;
        return;
    }

    
    int bit = bit_em(addr, pos);
    pos++;
    inserir_rec(&n->filho[bit], addr, pos, prefixo, route_id, t);
}


static int lookup_rec(No *n, const uint8_t *addr, int pos, int max_bits,
                       int melhor) {
    if (!n) return melhor;

    
    uint8_t skip_bytes[16];
    skip_para_bytes(n->skip_bits, skip_bytes);

    for (int i = 0; i < n->skip; i++) {
        if (pos + i >= max_bits) return melhor;
        if (bit_em(addr, pos + i) != bit_em(skip_bytes, i))
            return melhor; 
    }
    pos += n->skip;

    
    if (n->route_id != ROUTE_NONE)
        melhor = n->route_id;

    if (pos >= max_bits) return melhor;

    
    int bit = bit_em(addr, pos);
    return lookup_rec(n->filho[bit], addr, pos + 1, max_bits, melhor);
}



Trie *trie_criar(void) {
    Trie *t = (Trie *)calloc(1, sizeof(Trie));
    if (!t) { perror("calloc Trie"); exit(EXIT_FAILURE); }
    t->raiz    = NULL;
    t->n_nos   = 0;
    t->n_rotas = 0;
    return t;
}

int trie_inserir(Trie *t, const char *cidr, int route_id) {
    EnderecoIP ip;
    if (parsear_ip(cidr, &ip) != 0) {
        fprintf(stderr, "[ERRO] Prefixo inválido: %s\n", cidr);
        return -1;
    }
    inserir_rec(&t->raiz, ip.addr, 0, ip.prefixo, route_id, t);
    t->n_rotas++;
    return 0;
}

int trie_lookup(Trie *t, const char *ip_str) {
    EnderecoIP ip;
    if (parsear_ip(ip_str, &ip) != 0) {
        fprintf(stderr, "[ERRO] IP inválido: %s\n", ip_str);
        return ROUTE_NONE;
    }
    return lookup_rec(t->raiz, ip.addr, 0, ip.bits, ROUTE_NONE);
}



static void imprimir_rec(No *n, int prof, char *prefixo_str, int pos_str) {
    if (!n) return;

    
    uint8_t sb[16];
    skip_para_bytes(n->skip_bits, sb);
    char bits_skip[130] = "";
    for (int i = 0; i < n->skip && i < 128; i++) {
        bits_skip[i] = bit_em(sb, i) ? '1' : '0';
        bits_skip[i+1] = '\0';
    }

    for (int i = 0; i < prof; i++) printf("  ");
    printf("├─[skip=%d|%s]", n->skip, bits_skip);
    if (n->route_id != ROUTE_NONE)
        printf(" ★ route_id=%d", n->route_id);
    printf("\n");

    imprimir_rec(n->filho[0], prof + 1, prefixo_str, pos_str);
    imprimir_rec(n->filho[1], prof + 1, prefixo_str, pos_str);
}

void trie_imprimir(Trie *t) {
    printf("Trie (%d nós, %d rotas):\n", t->n_nos, t->n_rotas);
    imprimir_rec(t->raiz, 0, NULL, 0);
}



static void estat_rec(No *n, int prof, int *max_prof, int *n_folhas) {
    if (!n) return;
    if (!n->filho[0] && !n->filho[1]) {
        (*n_folhas)++;
        if (prof > *max_prof) *max_prof = prof;
        return;
    }
    estat_rec(n->filho[0], prof + 1, max_prof, n_folhas);
    estat_rec(n->filho[1], prof + 1, max_prof, n_folhas);
}

void trie_estatisticas(Trie *t) {
    int max_prof = 0, n_folhas = 0;
    estat_rec(t->raiz, 0, &max_prof, &n_folhas);
    printf("  Nós totais    : %d\n",   t->n_nos);
    printf("  Rotas         : %d\n",   t->n_rotas);
    printf("  Folhas        : %d\n",   n_folhas);
    printf("  Profund. max  : %d\n",   max_prof);
    printf("  Redução       : sem compressão seriam até %d nós (IPv6)\n",
           t->n_rotas * 128);
}



static void liberar_rec(No *n) {
    if (!n) return;
    liberar_rec(n->filho[0]);
    liberar_rec(n->filho[1]);
    free(n);
}

void trie_liberar(Trie *t) {
    liberar_rec(t->raiz);
    free(t);
}