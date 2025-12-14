
import socket
import threading
import random
import string

#Limitação de tamanho por arquivo
MAX_FILE_SIZE = 500 * 1024 * 1024 
BLOCK_SIZE = 4096

transfers = {}

def handle_client(client_socket, address):
    print(f"Nova conexão de {address}")
    
    try:
        request = client_socket.recv(1024).decode().split('|') #recebo a mensagem contendo, tamanho e nome
        
        if len(request) < 2: return
        command = request[0]

        
        if command == 'SEND':
            filename = request[1]
            filesize = int(request[2]) 
            
           
            if filesize > MAX_FILE_SIZE:
                client_socket.send("ERROR:Arquivo muito grande".encode())
                client_socket.close()
                return

            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            transfers[code] = {
                'socket': client_socket,
                'filename': filename,
                'filesize': filesize
            }
            
            client_socket.send(f"CODE:{code}".encode())
            print(f"Sessão criada! Código: {code} | Arq: {filename} ({filesize} bytes)")
            print(f"Enviador {address} está aguardando downloads...")
            
        
            return 

     
        elif command == 'RECV':
            code = request[1]
            
            if code in transfers:
                #busca no banco de tranfers, o meio que cofre do meu servidor
                sender_data = transfers[code]
                sender_socket = sender_data['socket']
                filename = sender_data['filename']
                filesize = sender_data['filesize']
                
                print(f"Cliente {address} solicitou arquivo {code}")

             
                client_socket.send(f"FILENM|{filename}|{filesize}".encode()) #sincronia com o cliente que está recebendo

             
                try:
                    sender_socket.send("UPLOAD_NOW".encode()) #avisa ao send para começar a enviar e encerra a parte de "conversa"
                except:
                    client_socket.send("ERROR:Enviador desconectou".encode())
                    del transfers[code] 
                    return

              
                remaining = filesize #conferir para não faltar nenhum byte, ou a conexão não se manter aberta depois que acabar o arquivo
                while remaining > 0:
                  
                    read_size = min(BLOCK_SIZE, remaining)  #guarda em read_sive o tamanho do proximo pacote que será enviado
                    
                    data = sender_socket.recv(read_size) #guarda em data o próximo pacote
                    if not data: break 
                    
                    client_socket.send(data) #transferencia de arquivos acontecendo
                    remaining -= len(data) #diminui para contagem
                
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
  #  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8080))
    server.listen(10) # Aceita até 10 conexões pendentes
    print(f"Servidor Multi-Client rodando na porta 8080...")
    print(f"Limite de arquivo: {MAX_FILE_SIZE/1024/1024} MB")

    while True:
        client_sock, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_sock, addr)).start()


start_server()