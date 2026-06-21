import sys

from scapy.all import ARP, Ether, srp


def escanear_rede(faixa_cidr: str, timeout: int = 3) -> dict:

    pacote = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=faixa_cidr)

    respostas, _ = srp(pacote, timeout=timeout, verbose=False)

    tabela_ip_mac = {}
    for _, recebido in respostas:
        tabela_ip_mac[recebido.psrc] = recebido.hwsrc

    return tabela_ip_mac


def main():
    if len(sys.argv) < 2:
        print("Uso: sudo python3 network_scanner.py <faixa_cidr>")
        print("Exemplo: sudo python3 network_scanner.py 192.168.1.0/24")
        sys.exit(1)

    faixa = sys.argv[1]
    print(f"[*] Escaneando a rede {faixa} via ARP Request...")

    tabela = escanear_rede(faixa)

    print(f"\n[+] {len(tabela)} dispositivo(s) encontrado(s):")
    print(f"{'IP':<18}{'MAC':<20}")
    print("-" * 38)
    for ip, mac in sorted(tabela.items(), key=lambda item: tuple(int(o) for o in item[0].split("."))):
        print(f"{ip:<18}{mac:<20}")


if __name__ == "__main__":
    main()