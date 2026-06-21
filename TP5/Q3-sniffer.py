import struct
import sys

import pcapy

INTERFACE = "lo"
FILTRO_BPF = "tcp port 8443"
TAMANHO_CABECALHO_ETHERNET = 14


def extrair_texto_legivel(payload: bytes) -> str:
    caracteres = []
    for byte in payload:
        if 32 <= byte <= 126:
            caracteres.append(chr(byte))
        else:
            caracteres.append(".")
    return "".join(caracteres)


def decodificar_pacote(dados: bytes):
    if len(dados) < TAMANHO_CABECALHO_ETHERNET:
        return None

    eth_tipo = struct.unpack("!H", dados[12:14])[0]
    if eth_tipo != 0x0800:
        return None

    ip_inicio = TAMANHO_CABECALHO_ETHERNET
    ip_header = dados[ip_inicio:ip_inicio + 20]
    if len(ip_header) < 20:
        return None

    versao_ihl = ip_header[0]
    tamanho_cabecalho_ip = (versao_ihl & 0x0F) * 4
    protocolo = ip_header[9]
    if protocolo != 6:
        return None

    tcp_inicio = ip_inicio + tamanho_cabecalho_ip
    tcp_header_base = dados[tcp_inicio:tcp_inicio + 20]
    if len(tcp_header_base) < 20:
        return None

    porta_origem, porta_destino = struct.unpack("!HH", tcp_header_base[0:4])
    offset_dados = (tcp_header_base[12] >> 4) * 4

    payload_inicio = tcp_inicio + offset_dados
    payload = dados[payload_inicio:]

    return {
        "porta_origem": porta_origem,
        "porta_destino": porta_destino,
        "payload": payload,
    }


def main():
    print(f"[*] Iniciando captura na interface {INTERFACE} (Porta 8443)...")

    try:
        capturador = pcapy.open_live(INTERFACE, 65536, True, 100)
    except Exception as e:
        print(f"[!] Erro ao abrir a interface '{INTERFACE}': {e}")
        print("    Rode este script com sudo/root.")
        sys.exit(1)

    capturador.setfilter(FILTRO_BPF)

    try:
        while True:
            cabecalho, dados_brutos = capturador.next()
            if cabecalho is None or len(dados_brutos) == 0:
                continue

            info = decodificar_pacote(dados_brutos)
            if info is None:
                continue

            texto = extrair_texto_legivel(info["payload"])

            print(f"\n[+] Pacote TCP Capturado! Tamanho: {len(dados_brutos)} bytes.")
            print(f"    Porta origem: {info['porta_origem']} -> Porta destino: {info['porta_destino']}")
            print(f"[Dados Brutos do Payload]: {info['payload'][:60]!r}")
            print(f"[Texto Convertido]: {texto[:120]}")

            if "AUTH_TOKEN" in texto or "REBOOT_SERVER" in texto:
                print("[!] ALERTA: Padrao sensivel encontrado em TEXTO CLARO! "
                      "A criptografia FALHOU.")
            else:
                print("[-] Alerta: Padrao 'AUTH_TOKEN' NAO encontrado. "
                      "Os dados estao devidamente cifrados via TLS.")

    except KeyboardInterrupt:
        print("\n[*] Captura interrompida pelo usuario.")


if __name__ == "__main__":
    main()