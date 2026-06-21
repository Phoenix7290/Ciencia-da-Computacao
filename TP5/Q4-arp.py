import sys
from collections import defaultdict

from scapy.all import ARP, sniff

from Q4_network import escanear_rede

ips_por_mac = defaultdict(set)


def construir_tabela_verdade(faixa_cidr: str) -> dict:
    print(f"[*] Mapeando a rede {faixa_cidr} (Tabela da Verdade)...")
    tabela = escanear_rede(faixa_cidr)
    print(f"[+] {len(tabela)} dispositivo(s) mapeado(s) inicialmente.\n")
    return tabela


def analisar_pacote_arp(pacote, tabela_verdade: dict, ip_gateway: str):
    if not pacote.haslayer(ARP):
        return

    arp = pacote[ARP]

    if arp.op != 2:
        return

    ip_origem = arp.psrc
    mac_origem = arp.hwsrc

    if ip_origem == ip_gateway:
        mac_legitimo = tabela_verdade.get(ip_gateway)
        if mac_legitimo and mac_origem != mac_legitimo:
            print("=" * 60)
            print("[ALERTA] Possivel ARP SPOOFING do GATEWAY detectado!")
            print(f"  IP do Gateway: {ip_origem}")
            print(f"  MAC esperado (legitimo): {mac_legitimo}")
            print(f"  MAC recebido (suspeito): {mac_origem}")
            print("=" * 60)

    ips_por_mac[mac_origem].add(ip_origem)
    if len(ips_por_mac[mac_origem]) > 1:
        print("=" * 60)
        print("[ALERTA] Comportamento suspeito: um unico MAC respondendo "
              "por multiplos IPs!")
        print(f"  MAC: {mac_origem}")
        print(f"  IPs associados a esse MAC nesta sessao: {ips_por_mac[mac_origem]}")
        print("=" * 60)

    print(f"[ARP Reply] {ip_origem} -> {mac_origem}")


def main():
    if len(sys.argv) < 3:
        print("Uso: sudo python3 arp_detector.py <faixa_cidr> <ip_gateway>")
        print("Exemplo: sudo python3 arp_detector.py 192.168.1.0/24 192.168.1.1")
        sys.exit(1)

    faixa_cidr = sys.argv[1]
    ip_gateway = sys.argv[2]

    tabela_verdade = construir_tabela_verdade(faixa_cidr)

    if ip_gateway not in tabela_verdade:
        print(f"[!] Aviso: {ip_gateway} nao respondeu ao scan inicial. "
              "O alerta de spoofing do gateway so funcionara se ele "
              "aparecer na tabela.")
    else:
        print(f"[*] MAC legitimo do Gateway ({ip_gateway}): {tabela_verdade[ip_gateway]}")

    print("\n[*] Monitorando trafego ARP em tempo real... (Ctrl+C para sair)\n")

    sniff(
        filter="arp",
        prn=lambda pkt: analisar_pacote_arp(pkt, tabela_verdade, ip_gateway),
        store=False,
    )


if __name__ == "__main__":
    main()