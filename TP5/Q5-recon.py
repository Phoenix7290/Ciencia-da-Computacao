import subprocess
import nmap
import json
import re


DNS_TARGET = "zonetransfer.me"

NMAP_TARGET = "scanme.nmap.org"


def executar_dnsrecon(alvo):
    print("[*] Executando DNSRecon...")

    registros = {
        "MX": [],
        "NS": [],
        "A": [],
        "TXT": [],
        "subdominios": []
    }

    comando_std = [
        "dnsrecon",
        "-d", alvo,
        "-t", "std"
    ]

    resultado_std = subprocess.run(
        comando_std,
        capture_output=True,
        text=True
    )

    saida_std = resultado_std.stdout + resultado_std.stderr

    comando_brt = [
        "dnsrecon",
        "-d", alvo,
        "-t", "brt"
    ]

    resultado_brt = subprocess.run(
        comando_brt,
        capture_output=True,
        text=True
    )

    saida_brt = resultado_brt.stdout + resultado_brt.stderr

    for linha in saida_std.splitlines():
        linha_upper = linha.upper()

        if "MX" in linha_upper:
            registros["MX"].append(linha)

        if "NS" in linha_upper:
            registros["NS"].append(linha)

        if "TXT" in linha_upper:
            registros["TXT"].append(linha)

        if " A " in linha_upper or linha_upper.startswith("[*] A"):
            registros["A"].append(linha)

    for linha in saida_brt.splitlines():
        if "FOUND" in linha.upper() or "BRUTE" in linha.upper():
            registros["subdominios"].append(linha)

    return registros


def executar_nmap(alvo):
    print("[*] Executando Nmap...")

    scanner = nmap.PortScanner()

    scanner.scan(
        hosts=alvo,
        arguments='-Pn -sV --top-ports 100'
    )

    resultados = {}

    for host in scanner.all_hosts():
        resultados[host] = {
            "estado": scanner[host].state(),
            "protocolos": {}
        }

        for proto in scanner[host].all_protocols():
            portas = scanner[host][proto].keys()

            resultados[host]["protocolos"][proto] = []

            for porta in portas:
                info = scanner[host][proto][porta]

                resultados[host]["protocolos"][proto].append({
                    "porta": porta,
                    "estado": info["state"],
                    "servico": info["name"],
                    "versao": info.get("version", "desconhecida")
                })

    return resultados


def salvar_relatorio(dns_data, nmap_data):
    relatorio = {
        "dnsrecon": dns_data,
        "nmap": nmap_data
    }

    with open("relatorio_recon.json", "w") as arquivo:
        json.dump(relatorio, arquivo, indent=4)

    print("\n[+] Relatório salvo em relatorio_recon.json")


def mostrar_resumo(dns_data, nmap_data):
    print("\n" + "=" * 50)
    print(" RELATÓRIO AUTOMATIZADO DE SUPERFÍCIE DE ATAQUE")
    print("=" * 50)

    print("\n[1] RESULTADOS DNS")
    for tipo, valores in dns_data.items():
        print(f"\n{tipo}:")
        for v in valores:
            print("-", v)

    print("\n[2] RESULTADOS NMAP")
    for host, dados in nmap_data.items():
        print(f"\nHost: {host}")
        print("Estado:", dados["estado"])

        for proto, servicos in dados["protocolos"].items():
            for servico in servicos:
                print(
                    f"Porta: {servico['porta']}/{proto} "
                    f"| Serviço: {servico['servico']} "
                    f"| Versão: {servico['versao']}"
                )


def main():
    dns_data = executar_dnsrecon(DNS_TARGET)
    nmap_data = executar_nmap(NMAP_TARGET)

    mostrar_resumo(dns_data, nmap_data)
    salvar_relatorio(dns_data, nmap_data)


if __name__ == "__main__":
    main()