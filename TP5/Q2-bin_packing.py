CAPACIDADE_SERVIDOR = 100

VMS_SOLICITADAS = [
    48, 12, 35, 22, 17, 65, 8, 42, 53, 29,
    14, 38, 47, 19, 25, 61, 33, 9, 55, 23,
    44, 16, 50, 31, 11, 28, 58, 41, 13, 37,
    62, 21, 45, 18, 26, 52, 34, 7, 49, 20,
    39, 15, 57, 32, 12, 27, 54, 43, 10, 36,
    60, 24, 46, 16, 22, 51, 30, 8, 40, 25
]

def next_fit(vms, capacidade):
    servidores = [[]]
    ocupacao = [0]

    for vm in vms:
        atual = len(servidores) - 1
        if ocupacao[atual] + vm <= capacidade:
            servidores[atual].append(vm)
            ocupacao[atual] += vm
        else:
            servidores.append([vm])
            ocupacao.append(vm)

    return servidores, ocupacao


def first_fit_decreasing(vms, capacidade):
    vms_ordenadas = sorted(vms, reverse=True)

    servidores = []
    ocupacao = []

    for vm in vms_ordenadas:
        colocado = False
        for i in range(len(servidores)):
            if ocupacao[i] + vm <= capacidade:
                servidores[i].append(vm)
                ocupacao[i] += vm
                colocado = True
                break

        if not colocado:
            servidores.append([vm])
            ocupacao.append(vm)

    return servidores, ocupacao

def imprimir_relatorio(nome, servidores, ocupacao, capacidade):
    print(f"[Heuristica {nome}]")
    print(f"- Servidores utilizados: {len(servidores)} servidores")
    for i, (servidor, ocup) in enumerate(zip(servidores, ocupacao), start=1):
        print(f"  Servidor {i}: {servidor} (Total: {ocup}/{capacidade} GB)")
    print()


def main():
    print("RESULTADO DA ALOCACAO (HEURISTICAS)\n")

    servidores_nf, ocup_nf = next_fit(VMS_SOLICITADAS, CAPACIDADE_SERVIDOR)
    imprimir_relatorio("Next-Fit", servidores_nf, ocup_nf, CAPACIDADE_SERVIDOR)

    servidores_ffd, ocup_ffd = first_fit_decreasing(VMS_SOLICITADAS, CAPACIDADE_SERVIDOR)
    imprimir_relatorio("First-Fit Decreasing", servidores_ffd, ocup_ffd, CAPACIDADE_SERVIDOR)

    diferenca = len(servidores_nf) - len(servidores_ffd)
    print(f"Conclusao: A heuristica First-Fit Decreasing economizou {diferenca} "
          f"servidor(es) em relacao a Next-Fit "
          f"({len(servidores_nf)} -> {len(servidores_ffd)}).")


if __name__ == "__main__":
    main()