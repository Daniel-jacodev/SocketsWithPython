import socket
import threading
import random
import string

# Configurações
MAX_FILE_SIZE = 500 * 1024 * 1024  
BLOCK_SIZE = 4096

PORTA_SERVIDOR = 8080

transfers = {}

def handle_client(client_socket, address):
    print(f"[NOVA CONEXÃO] {address} conectado.")
    
    try:
        # Tenta decodificar a mensagem inicial
        request = client_socket.recv(1024).decode().split('|')
        
        if len(request) < 1: 
            return
        command = request[0]

        # === LÓGICA DO ENVIADOR (SENDER) ===
        if command == 'SEND':
            if len(request) < 4: return 
            filename = request[1]
            filesize = int(request[2]) 
            file_hash = request[3]
            
            if filesize > MAX_FILE_SIZE:
                client_socket.send("ERROR:Arquivo muito grande".encode())
                client_socket.close()
                return

            # Gera código aleatório de 4 dígitos
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            # Salva o socket no dicionário para usar depois
            transfers[code] = {
                'socket': client_socket,
                'filename': filename,
                'filesize': filesize,
                'hash': file_hash
            }   
            
            client_socket.send(f"CODE:{code}".encode())
            print(f"[SESSÃO CRIADA] Código: {code} | Arq: {filename}")
            print(f"--> O socket do enviador {address} ficou salvo aguardando o receptor.")
            
            # NOTA: Não fechamos o socket aqui! Ele fica aberto esperando o Receiver.
            return 

        # === LÓGICA DO RECEPTOR (RECEIVER) ===
        elif command == 'RECV':
            if len(request) < 2: return
            code = request[1]
            
            if code in transfers:
                sender_data = transfers[code]
                sender_socket = sender_data['socket'] # Recupera o socket do enviador
                filename = sender_data['filename']
                filesize = sender_data['filesize']
                
                print(f"[REQUISIÇÃO] Cliente {address} pediu o arquivo {code}")

                # 1. Manda os dados do arquivo para o Receptor
                client_socket.send(f"FILENM|{filename}|{filesize}|{sender_data['hash']}".encode())

                # 2. Espera o Receptor confirmar com "OK" (Trava de segurança)
                client_socket.recv(1024) 
  
                # 3. Avisa o Enviador para começar a mandar os bytes
                try:
                    sender_socket.send("UPLOAD_NOW".encode())
                except:
                    client_socket.send("ERROR:Enviador desconectou".encode())
                    del transfers[code]
                    client_socket.close()
                    return

                # 4. Loop de transferência (Relay: Enviador -> Servidor -> Receptor)
                print(f"--> Iniciando transferência de {filesize} bytes...")
                remaining = filesize
                while remaining > 0:
                    read_size = min(BLOCK_SIZE, remaining)
                    
                    # Lê do Enviador
                    data = sender_socket.recv(read_size)
                    if not data: break
                    
                    # Repassa para o Receptor
                    client_socket.send(data)
                    remaining -= len(data)
                
                print(f"✅ Transferência concluída! Código {code} finalizado.")
                
                
                client_socket.close()       # Fecha receptor
               
                
            else:
                client_socket.send("ERROR:Código inválido ou expirado".encode())
                client_socket.close()

    except Exception as e:
        print(f"❌ Erro na conexão com {address}: {e}")
        client_socket.close()


def iniciar_servidor():
    HOST = '0.0.0.0'
    
    # Cria o socket principal do servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORTA_SERVIDOR))
    server.listen()
    
    print(f"--- SERVIDOR RODANDO ---")
    print(f"Escutando em: {HOST}:{PORTA_SERVIDOR}")
    print(f"Configure o Ngrok com: ngrok tcp {PORTA_SERVIDOR}")
    print("------------------------")

    # Loop infinito para aceitar conexões
    while True:
        try:
            conn, addr = server.accept()
            
            # AQUI ESTÁ A MÁGICA:
            # Para cada nova conexão, criamos uma linha de execução separada (Thread)
            # que vai rodar a função 'handle_client'.
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            
            print(f"[THREAD] Total ativas: {threading.active_count() - 1}")
            
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

if __name__ == "__main__":
    iniciar_servidor()