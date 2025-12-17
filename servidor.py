import socket #Para utilizar sockets
import threading #Para permitir multiplas conexões através do socket
import random #Para gerar o código random
import string

MAX_FILE_SIZE = 500 * 1024 * 1024  
BLOCK_SIZE = 4096

transfers = {}

def handle_client(client_socket, address):
    print(f"Nova conexão de {address}")
    
    try:
        request = client_socket.recv(1024).decode().split('|')
        
        if len(request) < 2: return
        command = request[0]

        # === LÓGICA DO ENVIADOR (SENDER) ===
        if command == 'SEND':
            filename = request[1]
            filesize = int(request[2]) 
            file_hash = request[3]
            
            
            if filesize > MAX_FILE_SIZE:
                client_socket.send("ERROR:Arquivo muito grande".encode())
                client_socket.close()
                return

            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            transfers[code] = {
                'socket': client_socket,
                'filename': filename,
                'filesize': filesize,
                'hash': file_hash
            }   
            
            client_socket.send(f"CODE:{code}".encode())
            print(f"Sessão criada! Código: {code} | Arq: {filename} ({filesize} bytes)")
            print(f"Enviador {address} está aguardando downloads...")
          
            return 


        # === LÓGICA DO RECEPTOR (RECEIVER) ===
        elif command == 'RECV':
            code = request[1]
            
            if code in transfers:
                sender_data = transfers[code]
                sender_socket = sender_data['socket']
                filename = sender_data['filename']
                filesize = sender_data['filesize']
                
                print(f"Cliente {address} solicitou arquivo {code}")

                client_socket.send(f"FILENM|{filename}|{filesize}|{sender_data['hash']}".encode())

 
                # TRAVA DE SEGURANÇA: O servidor fica PARADO aqui esperando
                # o receptor dizer "OK, recebi o nome, pode mandar a foto".
                # Isso impede que a foto chegue grudada no nome.
                client_socket.recv(1024) 
  

                try:
                    sender_socket.send("UPLOAD_NOW".encode())
                except:
                    client_socket.send("ERROR:Enviador desconectou".encode())
                    del transfers[code]
                    return

                remaining = filesize
                while remaining > 0:

                
                    read_size = min(BLOCK_SIZE, remaining)
                    
                    data = sender_socket.recv(read_size)
                    if not data: break
                    
                    client_socket.send(data)
                    remaining -= len(data)
                
                print(f"Transferência concluída para {address}. Enviador continua online.")
                client_socket.close() 
               
                
            else:
                client_socket.send("ERROR:Código inválido ou expirado".encode())
                client_socket.close()

    except Exception as e:
        print(f"Erro: {e}")
     
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8080))
    server.listen(10) # Aceita até 10 conexões pendentes
    print(f"Servidor Multi-Client rodando na porta 8080...")
    print(f"Limite de arquivo: {MAX_FILE_SIZE/1024/1024} MB")

    while True:
        client_sock, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_sock, addr)).start()

if __name__ == "__main__":
    start_server()