import socket
import ssl

HOST = "0.0.0.0"
PORT = 8443
CERT_FILE = "server.crt"
KEY_FILE = "server.key"


def main():
    contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    contexto.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_bruto:
        sock_bruto.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_bruto.bind((HOST, PORT))
        sock_bruto.listen(5)
        print(f"[Servidor] Escutando em {HOST}:{PORT} (TLS) ...")

        with contexto.wrap_socket(sock_bruto, server_side=True) as servidor_tls:
            while True:
                try:
                    conexao, endereco = servidor_tls.accept()
                except ssl.SSLError as e:
                    print(f"[Servidor] Falha no handshake TLS: {e}")
                    continue

                with conexao:
                    print(f"[Servidor] Conexao TLS estabelecida com {endereco}")
                    dados = conexao.recv(4096)
                    if dados:
                        mensagem = dados.decode("utf-8", errors="replace")
                        print(f"[Servidor] Comando Seguro Recebido: {mensagem}")
                        conexao.sendall(b"OK: comando processado")


if __name__ == "__main__":
    main()