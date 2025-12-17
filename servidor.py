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
        request = client_socket.recv(1024).decode().split('|')
        
        if len(request) < 1: 
            return
        command = request[0]

        # LÓGICA DO ENVIADOR - SEND
        if command == 'SEND':
            if len(request) < 4: return 
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
            print(f"[SESSÃO CRIADA] Código: {code} | Arq: {filename}")
            print(f"--> O socket do enviador {address} ficou salvo aguardando o receptor.")
 
            return 

        # LÓGICA DO RECEPTOR 
        elif command == 'RECV':
            if len(request) < 2: return
            code = request[1]
            
            if code in transfers:
                sender_data = transfers[code]
                sender_socket = sender_data['socket']
                filename = sender_data['filename']
                filesize = sender_data['filesize']
                
                print(f"O cliente {address} pediu o arquivo {code}")

                client_socket.send(f"FILENM|{filename}|{filesize}|{sender_data['hash']}".encode())

      
                client_socket.recv(1024) 
  
                try:
                    sender_socket.send("UPLOAD_NOW".encode())
                except:
                    client_socket.send("ERROR:Enviador desconectou".encode())
                    del transfers[code]
                    client_socket.close()
                    return
                
                print(f"--> Iniciando transferência de {filesize} bytes...")
                remaining = filesize
                while remaining > 0:
                    read_size = min(BLOCK_SIZE, remaining)
                    
        
                    data = sender_socket.recv(read_size)
                    if not data: break
                    
           
                    client_socket.send(data)
                    remaining -= len(data)
                
                print(f"✅ Transferência concluída! Código {code} finalizado.")
                
                
                client_socket.close()
               
                
            else:
                client_socket.send("ERROR:Código inválido ou expirado".encode())
                client_socket.close()

    except Exception as e:
        print(f"❌ Erro na conexão com {address}: {e}")
        client_socket.close()


def iniciar_servidor():
    HOST = '0.0.0.0'
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORTA_SERVIDOR))
    server.listen()
    
    print(f"--- SERVIDOR RODANDO ---")


    while True:
        try:
            conn, addr = server.accept()
            
  
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            
            print(f"[THREAD] Total ativas: {threading.active_count() - 1}")
            
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

if __name__ == "__main__":
    iniciar_servidor()