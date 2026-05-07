#ifndef TRIE_H
#define TRIE_H

#include <stdint.h>


#define MAX_BITS_IPV4   32
#define MAX_BITS_IPV6  128
#define ROUTE_NONE      -1   


typedef struct No {
    
    int      skip;
    uint64_t skip_bits[2];   

    
    struct No *filho[2];

    
    int route_id;
} No;


typedef struct {
    No  *raiz;
    int  n_nos;       
    int  n_rotas;     
} Trie;




Trie *trie_criar(void);


int trie_inserir(Trie *t, const char *cidr, int route_id);


int trie_lookup(Trie *t, const char *ip);


void trie_imprimir(Trie *t);


void trie_estatisticas(Trie *t);


void trie_liberar(Trie *t);

#endif 
