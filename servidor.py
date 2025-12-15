import socket
import threading
import random
import string

# Dicionário para guardar as transferências pendentes
# Formato: { 'CODIGO': socket_do_enviador }
transfers = {}

def handle_client(client_socket, address):
    print(f"Nova conexão de {address}")
    
    try:
        # O cliente envia primeiro a intenção: SEND ou RECV
        # Exemplo de mensagem: "SEND|nome_arquivo.txt" ou "RECV|1234"
        request = client_socket.recv(1024).decode().split('|')
        command = request[0]

        if command == 'SEND':
            filename = request[1]
            # Gera um código curto de 4 dígitos
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            # Guarda o socket do enviador no dicionário
            transfers[code] = client_socket
            
            # Avisa o código ao enviador
            client_socket.send(f"CODE:{code}".encode())
            print(f"Usuário {address} esperando receptor com código {code}")
            
            # Nota: A thread termina aqui? Não, mantemos o socket aberto no dicionário
            # O socket será usado quando o Receptor chegar.
            return 

        elif command == 'RECV':
            code = request[1]
            
            if code in transfers:
                sender_socket = transfers[code]
                print(f"Conectando receptor {address} ao enviador do código {code}")
                
                # Avisa ao enviador para começar a mandar
                sender_socket.send("START".encode())
                
                # LOOP DE TRANSFERÊNCIA (A PONTE)
                # O servidor lê do Sender e escreve no Receiver
                while True:
                    data = sender_socket.recv(4096)
                    if not data:
                        break
                    client_socket.send(data)
                
                # Limpeza
                sender_socket.close()
                client_socket.close()
                del transfers[code]
                print(f"Transferência {code} concluída.")
            else:
                client_socket.send("ERROR:Código não encontrado".encode())
                client_socket.close()

    except Exception as e:
        print(f"Erro na conexão: {e}")
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 0.0.0.0 permite conexões de qualquer IP (local ou externo se tiver port forwarding)
    server.bind(('0.0.0.0', 8080))
    server.listen(5)
    print("Servidor P2P Relay rodando na porta 8080...")

    while True:
        client_sock, addr = server.accept()
        # Cria uma nova thread para cada conexão
        thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        thread.start()

if __name__ == "__main__":
    start_server()