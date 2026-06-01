from __future__ import annotations
import time




class NoTrie:


    def __init__(self):
        self.filhos    : dict[str, "NoTrie"] = {}
        self.fim       : bool                = False
        self.frequencia: int                 = 0




class Trie:


    def __init__(self):
        self._raiz      = NoTrie()
        self._tamanho   = 0



    def inserir(self, palavra: str) -> None:

        palavra = palavra.lower().strip()
        no = self._raiz
        for char in palavra:
            if char not in no.filhos:
                no.filhos[char] = NoTrie()
            no = no.filhos[char]

        if not no.fim:
            no.fim = True
            self._tamanho += 1
        no.frequencia += 1



    def buscar(self, palavra: str) -> bool:

        no = self._navegar(palavra.lower().strip())
        return no is not None and no.fim

    def _navegar(self, prefixo: str) -> NoTrie | None:

        no = self._raiz
        for char in prefixo:
            if char not in no.filhos:
                return None
            no = no.filhos[char]
        return no



    def remover(self, palavra: str) -> bool:

        palavra = palavra.lower().strip()
        removido, self._raiz = self._remover_rec(self._raiz, palavra, 0)
        if removido:
            self._tamanho -= 1
        return removido

    def _remover_rec(self, no: NoTrie, palavra: str, nivel: int) -> tuple[bool, NoTrie]:
        if no is None:
            return False, no

        if nivel == len(palavra):
            if not no.fim:
                return False, no
            no.fim = False
            no.frequencia = 0

            pode_podar = len(no.filhos) == 0
            return True, (None if pode_podar else no)

        char = palavra[nivel]
        if char not in no.filhos:
            return False, no

        removido, filho_atualizado = self._remover_rec(no.filhos[char], palavra, nivel + 1)
        if filho_atualizado is None:
            del no.filhos[char]
        else:
            no.filhos[char] = filho_atualizado


        pode_podar = (len(no.filhos) == 0 and not no.fim)
        return removido, (None if pode_podar else no)



    def listar(self) -> list[str]:

        resultado: list[str] = []
        self._listar_rec(self._raiz, [], resultado)
        return resultado

    def _listar_rec(self, no: NoTrie, prefixo: list[str], resultado: list[str]) -> None:
        if no.fim:
            resultado.append("".join(prefixo))
        for char in sorted(no.filhos):
            prefixo.append(char)
            self._listar_rec(no.filhos[char], prefixo, resultado)
            prefixo.pop()



    def autocompletar(self, prefixo: str, limite: int = 10) -> list[str]:

        prefixo = prefixo.lower().strip()
        no = self._navegar(prefixo)
        if no is None:
            return []

        candidatos: list[tuple[int, str]] = []
        self._completar_rec(no, list(prefixo), candidatos)

        candidatos.sort(key=lambda x: (-x[0], x[1]))
        return [palavra for _, palavra in candidatos[:limite]]

    def _completar_rec(
        self, no: NoTrie, prefixo: list[str], candidatos: list[tuple[int, str]]
    ) -> None:
        if no.fim:
            candidatos.append((no.frequencia, "".join(prefixo)))
        for char in sorted(no.filhos):
            prefixo.append(char)
            self._completar_rec(no.filhos[char], prefixo, candidatos)
            prefixo.pop()



    def autocorrigir(self, query: str, max_distancia: int = 2, limite: int = 5) -> list[str]:

        query = query.lower().strip()

        linha_atual = list(range(len(query) + 1))
        sugestoes: list[tuple[int, str]] = []

        for char in sorted(self._raiz.filhos):
            self._corrigir_rec(
                self._raiz.filhos[char], char, query,
                linha_atual, sugestoes, max_distancia
            )

        sugestoes.sort(key=lambda x: (x[0], x[1]))
        return [palavra for _, palavra in sugestoes[:limite]]

    def _corrigir_rec(
        self,
        no        : NoTrie,
        letra     : str,
        query     : str,
        linha_ant : list[int],
        sugestoes : list[tuple[int, str]],
        max_dist  : int,
        prefixo   : str = "",
    ) -> None:
        colunas    = len(query) + 1
        linha_nova = [linha_ant[0] + 1]
        prefixo    = prefixo + letra

        for col in range(1, colunas):
            substituicao = linha_ant[col - 1] + (0 if query[col - 1] == letra else 1)
            linha_nova.append(min(
                linha_nova[col - 1] + 1,
                linha_ant[col]     + 1,
                substituicao
            ))


        if no.fim and linha_nova[-1] <= max_dist:
            sugestoes.append((linha_nova[-1], prefixo))


        if min(linha_nova) <= max_dist:
            for char in sorted(no.filhos):
                self._corrigir_rec(
                    no.filhos[char], char, query,
                    linha_nova, sugestoes, max_dist, prefixo
                )



    def __len__(self) -> int:
        return self._tamanho

    def frequencia(self, palavra: str) -> int:

        no = self._navegar(palavra.lower().strip())
        return no.frequencia if (no and no.fim) else 0




PALAVRAS_PT = [

    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    "eu", "tu", "ele", "ela", "nos", "vos", "eles", "elas",
    "me", "te", "se", "lhe", "nos", "vos",

    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "por", "para", "com", "sem", "sob", "sobre", "entre",
    "e", "ou", "mas", "que", "se", "porque", "como", "quando",

    "ser", "estar", "ter", "haver", "fazer", "poder", "querer",
    "dizer", "ver", "dar", "saber", "vir", "ir", "vir",
    "falar", "passar", "ficar", "deixar", "levar", "trazer",
    "chegar", "partir", "começar", "terminar", "encontrar",
    "achar", "pensar", "saber", "entender", "conhecer",
    "trabalhar", "estudar", "aprender", "ensinar",

    "casa", "vida", "tempo", "dia", "ano", "homem", "mulher",
    "filho", "filha", "pai", "mae", "irmao", "irma",
    "cidade", "pais", "mundo", "brasil", "agua", "comida",
    "carro", "porta", "mesa", "livro", "escola", "trabalho",
    "dinheiro", "hora", "minuto", "semana", "mes",

    "grande", "pequeno", "novo", "velho", "bom", "ruim",
    "bonito", "feio", "rapido", "lento", "forte", "fraco",
    "alto", "baixo", "quente", "frio", "certo", "errado",

    "muito", "pouco", "mais", "menos", "bem", "mal",
    "aqui", "ali", "la", "agora", "depois", "antes",
    "sempre", "nunca", "ja", "ainda", "tambem", "so",

    "um", "dois", "tres", "quatro", "cinco",
    "seis", "sete", "oito", "nove", "dez",

    "algoritmo", "computador", "programa", "codigo", "dado",
    "arquivo", "sistema", "rede", "processo", "memoria",
    "pilha", "fila", "arvore", "grafo", "hash",
    "recursao", "iteracao", "funcao", "variavel", "classe",
    "objeto", "metodo", "atributo", "heranca", "interface",
]




def _ok(condicao: bool, descricao: str) -> bool:
    simbolo = "✓" if condicao else "✗"
    status  = "PASSOU" if condicao else "FALHOU"
    print(f"    {simbolo}  [{status}]  {descricao}")
    return condicao


def executar_testes(trie: Trie) -> None:
    falhas = 0
    testes = 0

    def checa(cond: bool, desc: str) -> None:
        nonlocal falhas, testes
        testes += 1
        if not _ok(cond, desc):
            falhas += 1


    print("\n  [T1] Inserção e tamanho")
    tamanho_base = len(trie)
    trie.inserir("python")
    trie.inserir("python")
    trie.inserir("pythonico")
    checa(len(trie) == tamanho_base + 2,
          f"Tamanho após 2 novas palavras: esperado {tamanho_base+2}, obtido {len(trie)}")
    checa(trie.frequencia("python") == 2,
          "Frequência de 'python' (inserida 2×) == 2")


    print("\n  [T2] Busca")
    checa(trie.buscar("casa"),     "'casa' deve existir")
    checa(trie.buscar("algoritmo"), "'algoritmo' deve existir")
    checa(not trie.buscar("xyzzy"), "'xyzzy' NÃO deve existir")
    checa(not trie.buscar("cas"),   "'cas' (prefixo apenas) NÃO deve existir como palavra")


    print("\n  [T3] Remoção")
    trie.inserir("remover_teste")
    checa(trie.buscar("remover_teste"), "'remover_teste' inserida com sucesso")
    trie.remover("remover_teste")
    checa(not trie.buscar("remover_teste"), "'remover_teste' removida com sucesso")
    checa(not trie.remover("inexistente"),  "Remover palavra inexistente retorna False")


    print("\n  [T4] Listagem")
    todas = trie.listar()
    checa("casa" in todas,      "'casa' aparece na listagem")
    checa("algoritmo" in todas, "'algoritmo' aparece na listagem")
    checa(todas == sorted(todas), "Listagem está em ordem alfabética")
    checa(len(todas) == len(trie), "len(listar()) == len(trie)")


    print("\n  [T5] Autocompletar")
    sug_al = trie.autocompletar("al")
    checa(len(sug_al) > 0,            "autocompletar('al') retorna resultados")
    checa(all(w.startswith("al") for w in sug_al),
          "Todas as sugestões de 'al' começam com 'al'")
    sug_xyz = trie.autocompletar("xyz")
    checa(len(sug_xyz) == 0,          "autocompletar('xyz') retorna lista vazia")
    sug_py = trie.autocompletar("py")
    checa("python" in sug_py and "pythonico" in sug_py,
          "autocompletar('py') encontra 'python' e 'pythonico'")


    print("\n  [T6] Autocorrigir")

    cor1 = trie.autocorrigir("cssa", max_distancia=2)
    checa("casa" in cor1, f"autocorrigir('cssa') sugere 'casa': {cor1}")

    cor2 = trie.autocorrigir("algortimo", max_distancia=2)
    checa("algoritmo" in cor2, f"autocorrigir('algortimo') sugere 'algoritmo': {cor2}")

    cor3 = trie.autocorrigir("zzzzzzzzzzz", max_distancia=2)
    checa(len(cor3) == 0, "autocorrigir('zzzzzzzzzzz') retorna lista vazia")


    print(f"\n  {'─'*50}")
    print(f"  Resultado: {testes - falhas}/{testes} testes passaram"
          + (" TODOS OK" if falhas == 0 else f" {falhas} FALHA(S)"))
    print(f"  {'─'*50}")




def demo_autocompletar(trie: Trie) -> None:
    print("\n")
    print("  DEMO — AUTOCOMPLETAR")
    print()
    prefixos = ["com", "pro", "ar", "tra", "es", "ca"]
    for pref in prefixos:
        sugestoes = trie.autocompletar(pref, limite=5)
        print(f"  '{pref}' → {sugestoes}")


def demo_autocorrigir(trie: Trie) -> None:
    print("\n")
    print("  DEMO — AUTOCORRIGIR  (distância de Levenshtein ≤ 2)")
    print()
    erros = [
        ("csa",       "casa"),
        ("tarabalho", "trabalho"),
        ("escolla",   "escola"),
        ("falar",     "falar (correto)"),
        ("tmepo",     "tempo"),
        ("sivstema",  "sistema"),
    ]
    for errado, esperado in erros:
        inicio = time.perf_counter()
        sugestoes = trie.autocorrigir(errado, max_distancia=2, limite=3)
        elapsed = (time.perf_counter() - inicio) * 1000
        print(f"  '{errado:<12}' → {str(sugestoes):<35}  ({elapsed:.2f} ms)")




def main() -> None:
    print()
    print("  TRIE — Português (100+ palavras)")
    print()

    trie = Trie()


    t0 = time.perf_counter()
    for palavra in PALAVRAS_PT:
        trie.inserir(palavra)
    t1 = time.perf_counter()

    print(f"\n  Palavras inseridas : {len(trie)}")
    print(f"  Tempo de inserção  : {(t1-t0)*1000:.2f} ms")


    todas = trie.listar()
    print(f"\n  Primeiras 15 palavras (ordem alfabética):")
    print(f"  {todas[:15]}")
    print(f"  Últimas  15 palavras:")
    print(f"  {todas[-15:]}")


    print("\n")
    print("  BUSCAS AVULSAS")
    print()
    exemplos = ["casa", "arvore", "python", "haskell", "algoritmo", "rec"]
    for palavra in exemplos:
        encontrado = trie.buscar(palavra)
        print(f"  buscar('{palavra}') → {' encontrada' if encontrado else ' não encontrada'}")

    demo_autocompletar(trie)
    demo_autocorrigir(trie)

    print("\n")
    print("  BATERIA DE TESTES AUTOMATIZADOS")
    print()
    executar_testes(trie)


if __name__ == "__main__":
    main()
