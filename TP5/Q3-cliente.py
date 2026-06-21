import socket
import ssl

HOST = "127.0.0.1"
PORT = 8443
CERT_FILE = "server.crt"
MENSAGEM = "AUTH_TOKEN:XYZ123:CMD:REBOOT_SERVER"


def main():
    contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    contexto.load_verify_locations(cafile=CERT_FILE)
    contexto.check_hostname = True

    with socket.create_connection((HOST, PORT)) as sock_bruto:
        with contexto.wrap_socket(sock_bruto, server_hostname="localhost") as conexao_tls:
            print(f"[Cliente] Canal TLS estabelecido. Cifra: {conexao_tls.cipher()}")
            conexao_tls.sendall(MENSAGEM.encode("utf-8"))
            resposta = conexao_tls.recv(4096)
            print(f"[Cliente] Resposta do servidor: {resposta.decode('utf-8')}")


if __name__ == "__main__":
    main()