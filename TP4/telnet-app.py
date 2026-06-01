import socket
import threading
import time
import sys
import subprocess
import select

HOST_PADRAO  = "127.0.0.1"
PORTA_TELNET = 2323
BUFFER       = 1024
TIMEOUT      = 6


IAC   = 0xFF
DONT  = 0xFE
DO    = 0xFD
WONT  = 0xFC
WILL  = 0xFB
SB    = 0xFA
SE    = 0xF0

OPT_ECHO          = 0x01
OPT_SUPPRESS_GA   = 0x03
OPT_LINEMODE      = 0x22


def _filtrar_iac(dados: bytes) -> bytes:

    saida = bytearray()
    i = 0
    while i < len(dados):
        b = dados[i]
        if b == IAC and i + 2 < len(dados):
            i += 3
        else:
            saida.append(b)
            i += 1
    return bytes(saida)


def _negociar(conn: socket.socket) -> None:


    conn.sendall(bytes([IAC, WILL, OPT_ECHO,
                        IAC, WILL, OPT_SUPPRESS_GA,
                        IAC, DONT, OPT_LINEMODE]))




BANNER = (
    "\r\n"
    "\r\n"
    "    Servidor Telnet     \r\n"
    "\r\n"
    "\r\n"
    "  Comandos: eco <msg> | hora | ajuda | sair\r\n\r\n"
    "  > "
)

def _processar_comando(cmd: str) -> str:
    cmd = cmd.strip().lower()
    if not cmd:
        return "  > "
    if cmd.startswith("eco "):
        return f"  {cmd[4:]}\r\n  > "
    if cmd == "hora":
        return f"  {time.strftime('%Y-%m-%d %H:%M:%S')}\r\n  > "
    if cmd == "ajuda":
        return (
            "  Comandos disponíveis:\r\n"
            "    eco <texto>  — repete o texto\r\n"
            "    hora         — exibe data e hora\r\n"
            "    ajuda        — este menu\r\n"
            "    sair         — encerra a sessão\r\n"
            "  > "
        )
    if cmd == "sair":
        return "__SAIR__"
    return f"  Comando desconhecido: '{cmd}'\r\n  > "


def _tratar_cliente(conn: socket.socket, addr: tuple) -> None:
    print(f"  [TELNET-SRV] Conexão de {addr}")
    try:
        _negociar(conn)
        conn.sendall(BANNER.encode())
        buffer_linha = ""
        while True:
            try:
                dados = conn.recv(BUFFER)
            except (ConnectionResetError, OSError):
                break
            if not dados:
                break
            texto = _filtrar_iac(dados).decode(errors="replace")
            buffer_linha += texto

            while "\n" in buffer_linha or "\r" in buffer_linha:
                for delim in ("\r\n", "\r", "\n"):
                    if delim in buffer_linha:
                        linha, buffer_linha = buffer_linha.split(delim, 1)
                        resposta = _processar_comando(linha)
                        if resposta == "__SAIR__":
                            conn.sendall("  Até logo!\r\n".encode())
                            conn.close()
                            print(f"  [TELNET-SRV] {addr} encerrou a sessão.")
                            return
                        conn.sendall(resposta.encode())
                        break
    except Exception as exc:
        print(f"  [TELNET-SRV] Erro com {addr}: {exc}")
    finally:
        conn.close()
        print(f"  [TELNET-SRV] Conexão encerrada: {addr}")


def servidor_telnet(host: str = HOST_PADRAO, porta: int = PORTA_TELNET) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, porta))
        srv.listen(5)
        print(f"  [TELNET-SRV] Escutando em {host}:{porta} ...")
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=_tratar_cliente, args=(conn, addr), daemon=True)
            t.start()




def _sessao_telnet_automatica(host: str, porta: int, comandos: list[str]) -> list[str]:

    respostas = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
        cli.settimeout(TIMEOUT)
        cli.connect((host, porta))


        time.sleep(0.3)
        try:
            cli.recv(BUFFER)
        except Exception:
            pass

        for cmd in comandos:
            cli.sendall((cmd + "\r\n").encode())
            time.sleep(0.4)
            try:
                resposta = _filtrar_iac(cli.recv(BUFFER)).decode(errors="replace")
                respostas.append(resposta.strip())
            except Exception:
                respostas.append("<timeout>")
    return respostas


def cliente_telnet_interativo(host: str = HOST_PADRAO,
                              porta: int = PORTA_TELNET) -> None:

    print(f"  Conectando a {host}:{porta} ... (Ctrl+C para sair)")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
        cli.connect((host, porta))
        cli.settimeout(0.1)

        def _receber():
            while True:
                try:
                    dados = cli.recv(BUFFER)
                    if not dados:
                        break
                    texto = _filtrar_iac(dados).decode(errors="replace")
                    print(texto, end="", flush=True)
                except socket.timeout:
                    pass
                except Exception:
                    break

        t = threading.Thread(target=_receber, daemon=True)
        t.start()

        try:
            while True:
                linha = input()
                cli.sendall((linha + "\r\n").encode())
        except (KeyboardInterrupt, EOFError):
            print("\n  Encerrando cliente.")




def analise_curl(host: str = HOST_PADRAO, porta: int = PORTA_TELNET) -> None:

    print("=" * 62)
    print("  ANÁLISE COM CURL — Servidor Telnet")
    print(f"  Alvo: telnet://{host}:{porta}")
    print("=" * 62)

    testes_curl = [
        {
            "descricao": "Conexão simples (curl telnet://)",
            "cmd": ["curl", "--silent", "--max-time", "3",
                    f"telnet://{host}:{porta}"],
        },
        {
            "descricao": "Enviar comando 'hora' via stdin",
            "cmd": ["curl", "--silent", "--max-time", "3",
                    "--data-binary", "hora\r\n",
                    f"telnet://{host}:{porta}"],
        },
        {
            "descricao": "Enviar 'eco teste curl'",
            "cmd": ["curl", "--silent", "--max-time", "3",
                    "--data-binary", "eco teste curl\r\nsair\r\n",
                    f"telnet://{host}:{porta}"],
        },
        {
            "descricao": "Verbose — cabeçalhos de negociação TCP",
            "cmd": ["curl", "--verbose", "--max-time", "2",
                    f"telnet://{host}:{porta}"],
        },
    ]

    for teste in testes_curl:
        print(f"\n  [{teste['descricao']}]")
        print(f"  $ {' '.join(teste['cmd'])}")
        print(f"  {'─'*56}")
        try:
            resultado = subprocess.run(
                teste["cmd"],
                capture_output=True,
                text=True,
                timeout=6
            )
            saida = (resultado.stdout + resultado.stderr).strip()

            saida_limpa = "".join(c for c in saida if c.isprintable() or c in "\n\r")
            if saida_limpa:
                for linha in saida_limpa.splitlines()[:20]:
                    print(f"  {linha}")
            else:
                print("  (sem saída — servidor pode ter fechado imediatamente)")
        except FileNotFoundError:
            print("    curl não encontrado. Instale com: apt install curl")
        except subprocess.TimeoutExpired:
            print("    Timeout ao aguardar resposta do curl.")
        except Exception as exc:
            print(f"    Erro: {exc}")

    print("\n" + "=" * 62)
    print("""
  Observações sobre curl × Telnet
  ─────────────────────────────────────────────────────────
  ✦ curl suporta o esquema telnet:// desde a versão 7.x.
  ✦ Com telnet://, curl abre uma conexão TCP pura e passa
    stdin para o servidor sem interpretação de protocolo.
  ✦ A negociação IAC (bytes 0xFF) aparece como lixo no curl
    --verbose porque curl não implementa o protocolo Telnet
    completo — apenas a camada TCP subjacente.
  ✦ Para sessões interativas reais, o cliente Telnet deste
    arquivo trata as sequências IAC corretamente.
  ✦ curl é útil para testar a conectividade TCP e verificar
    se o servidor aceita conexões antes de usar o cliente
    dedicado.
""")




def executar_testes(host: str = HOST_PADRAO) -> None:
    print("=" * 62)
    print("  BATERIA DE TESTES — Cliente × Servidor Telnet")
    print(f"  Host: {host}:{PORTA_TELNET}")
    print("=" * 62)

    casos = [
        (["eco ola mundo"],         "ola mundo",            "Eco simples"),
        (["hora"],                  time.strftime("%Y"),     "Comando hora (ano presente)"),
        (["ajuda"],                 "Comandos",              "Comando ajuda"),
        (["comando_invalido"],      "desconhecido",          "Comando inválido"),
        (["eco a" * 50],            "a",                     "Eco mensagem longa"),
    ]

    aprovados = 0
    for comandos, esperado_sub, descricao in casos:
        try:
            respostas = _sessao_telnet_automatica(host, PORTA_TELNET, comandos)
            resposta_total = " ".join(respostas)
            ok = esperado_sub.lower() in resposta_total.lower()
            simbolo = "✓" if ok else "✗"
            status  = "PASSOU" if ok else "FALHOU"
            print(f"    {simbolo}  [{status}]  {descricao}")
            if ok:
                aprovados += 1
        except Exception as exc:
            print(f"      [ERRO]  {descricao}: {exc}")

    print(f"\n  Resultado: {aprovados}/{len(casos)} testes passaram")
    print("=" * 62)




def main() -> None:
    args = sys.argv[1:]
    host = HOST_PADRAO

    if "--host" in args:
        idx  = args.index("--host")
        host = args[idx + 1]

    modo = args[0] if args else "testes"

    if modo == "servidor":
        servidor_telnet(host, PORTA_TELNET)

    elif modo == "cliente":
        cliente_telnet_interativo(host, PORTA_TELNET)

    elif modo == "curl":
        analise_curl(host, PORTA_TELNET)

    elif modo == "testes":

        if host == HOST_PADRAO:
            print("  Iniciando servidor Telnet local ...")
            t = threading.Thread(
                target=servidor_telnet, args=(HOST_PADRAO, PORTA_TELNET), daemon=True
            )
            t.start()
            time.sleep(0.4)
        executar_testes(host)
        analise_curl(host, PORTA_TELNET)

    else:
        print("Uso: python telnet_app.py [testes|servidor|cliente|curl] [--host IP]")


if __name__ == "__main__":
    main()
