import socket
import threading
import time
import sys
import struct

HOST_PADRAO = "127.0.0.1"
PORTA_TCP   = 9001
PORTA_UDP   = 9002
BUFFER      = 4096
TIMEOUT     = 5




def servidor_tcp(host: str = HOST_PADRAO, porta: int = PORTA_TCP) -> None:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, porta))
        srv.listen(5)
        print(f"  [TCP-SRV] Escutando em {host}:{porta} ...")

        while True:
            conn, addr = srv.accept()
            with conn:
                print(f"  [TCP-SRV] Conexão de {addr}")
                while True:
                    dados = conn.recv(BUFFER)
                    if not dados:
                        break
                    mensagem = dados.decode()
                    resposta = f"ECO-TCP: {mensagem.upper()}"
                    conn.sendall(resposta.encode())
                    print(f"  [TCP-SRV] Recebido: '{mensagem.strip()}' → Enviado: '{resposta.strip()}'")




def cliente_tcp(mensagem: str,
                host: str = HOST_PADRAO,
                porta: int = PORTA_TCP) -> str:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
        cli.settimeout(TIMEOUT)
        cli.connect((host, porta))
        cli.sendall(mensagem.encode())
        resposta = cli.recv(BUFFER).decode()
    return resposta




def servidor_udp(host: str = HOST_PADRAO, porta: int = PORTA_UDP) -> None:

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as srv:
        srv.bind((host, porta))
        print(f"  [UDP-SRV] Escutando em {host}:{porta} ...")

        while True:
            dados, addr = srv.recvfrom(BUFFER)
            mensagem = dados.decode()
            resposta = f"ECO-UDP: {mensagem.upper()}"
            srv.sendto(resposta.encode(), addr)
            print(f"  [UDP-SRV] De {addr}: '{mensagem.strip()}' → '{resposta.strip()}'")




def cliente_udp(mensagem: str,
                host: str = HOST_PADRAO,
                porta: int = PORTA_UDP) -> str:

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cli:
        cli.settimeout(TIMEOUT)
        cli.sendto(mensagem.encode(), (host, porta))
        resposta, _ = cli.recvfrom(BUFFER)
    return resposta.decode()




MENSAGENS_TESTE = [
    "ola mundo",
    "testando socket tcp e udp",
    "ciencia da computacao infnet",
    "12345 numeros e simbolos !@#",
    "WASD" * 250,
]

def _ok(condicao: bool, descricao: str) -> bool:
    simbolo = "✓" if condicao else "✗"
    status  = "PASSOU" if condicao else "FALHOU"
    print(f"    {simbolo}  [{status}]  {descricao}")
    return condicao


def _testar_protocolo(protocolo: str,
                      func_cliente,
                      mensagens: list[str]) -> tuple[int, int, float]:

    aprovados = 0
    latencias = []

    for msg in mensagens:
        try:
            t0 = time.perf_counter()
            resposta = func_cliente(msg)
            lat = (time.perf_counter() - t0) * 1000
            latencias.append(lat)

            esperado_prefixo = f"ECO-{protocolo}: {msg.upper()}"
            ok = resposta == esperado_prefixo
            aprovados += _ok(ok, f"'{msg[:30]}...' ({lat:.2f} ms)" if len(msg) > 30
                             else f"'{msg}' ({lat:.2f} ms)")
        except Exception as exc:
            _ok(False, f"ERRO ao enviar '{msg[:20]}': {exc}")

    media = sum(latencias) / len(latencias) if latencias else 0
    return aprovados, len(mensagens), media


def executar_testes(host: str = HOST_PADRAO) -> None:
    print("=" * 62)
    print("  BATERIA DE TESTES — TCP e UDP")
    print(f"  Host alvo : {host}")
    print("=" * 62)

    resultados = {}


    print("\n  [TCP] Iniciando testes ...")
    try:
        ap, tot, lat = _testar_protocolo(
            "TCP",
            lambda m: cliente_tcp(m, host),
            MENSAGENS_TESTE
        )
        resultados["TCP"] = (ap, tot, lat)
    except Exception as exc:
        print(f"      Servidor TCP inacessível: {exc}")
        resultados["TCP"] = (0, len(MENSAGENS_TESTE), 0)


    print("\n  [UDP] Iniciando testes ...")
    try:
        ap, tot, lat = _testar_protocolo(
            "UDP",
            lambda m: cliente_udp(m, host),
            MENSAGENS_TESTE
        )
        resultados["UDP"] = (ap, tot, lat)
    except Exception as exc:
        print(f"      Servidor UDP inacessível: {exc}")
        resultados["UDP"] = (0, len(MENSAGENS_TESTE), 0)


    print("\n" + "=" * 62)
    print("  RESUMO DE TESTES")
    print("=" * 62)
    print(f"  {'Protocolo':<12} {'Aprovados':>10} {'Total':>7} {'Latência média':>16}")
    print("  " + "─" * 50)
    for proto, (ap, tot, lat) in resultados.items():
        print(f"  {proto:<12} {ap:>10}/{tot:<6} {lat:>14.2f} ms")
    print("=" * 62)

    print("""
  Análise comparativa TCP × UDP
  ───────────────────────────────────────────────────────────
  TCP (SOCK_STREAM)
    + Orientado a conexão — exige handshake (SYN/SYN-ACK/ACK)
      antes de qualquer troca de dados.
    + Entrega garantida, ordenada e sem duplicatas.
    + Controle de congestionamento e retransmissão automáticos.
    + Latência ligeiramente maior devido ao overhead de controle.
    + Ideal para: transferência de arquivos, HTTP, SSH, e-mail.

  UDP (SOCK_DGRAM)
    + Sem conexão — datagramas enviados diretamente.
    + Sem garantia de entrega, ordem ou ausência de duplicatas.
    + Menor overhead → menor latência típica.
    + Ideal para: streaming, jogos em rede, DNS, VoIP.
""")




def _iniciar_servidores_locais() -> None:

    t_tcp = threading.Thread(
        target=servidor_tcp, args=(HOST_PADRAO, PORTA_TCP), daemon=True
    )
    t_udp = threading.Thread(
        target=servidor_udp, args=(HOST_PADRAO, PORTA_UDP), daemon=True
    )
    t_tcp.start()
    t_udp.start()
    time.sleep(0.3)


def main() -> None:
    args = sys.argv[1:]
    host = HOST_PADRAO


    if "--host" in args:
        idx = args.index("--host")
        host = args[idx + 1]

    if not args or args[0] == "testes":

        if host == HOST_PADRAO:
            print("  Iniciando servidores locais ...")
            _iniciar_servidores_locais()
        executar_testes(host)

    elif args[0] == "servidor-tcp":
        servidor_tcp(host, PORTA_TCP)

    elif args[0] == "servidor-udp":
        servidor_udp(host, PORTA_UDP)

    elif args[0] == "cliente-tcp":
        msg = " ".join(args[1:]) or "ola servidor tcp"
        print(cliente_tcp(msg, host))

    elif args[0] == "cliente-udp":
        msg = " ".join(args[1:]) or "ola servidor udp"
        print(cliente_udp(msg, host))

    else:
        print("Uso: python sockets.py [testes|servidor-tcp|servidor-udp|cliente-tcp|cliente-udp] [--host IP]")


if __name__ == "__main__":
    main()
