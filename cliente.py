
import socket
import os
import time

#local de onde o servidor está
SERVER_IP = 'localhost'
SERVER_PORT = 8080

def send_file():
    #Recebe os dados do arquivo
    raw_filename = input("Digite o caminho do arquivo: ").strip().replace("'", "").replace('"', "")
    
    if not os.path.exists(raw_filename):
        print("Erro: Arquivo não existe.")
        return
    #guarda o nome e tamanho do arquivo
    filesize = os.path.getsize(raw_filename)
    name_only = os.path.basename(raw_filename)

    #cliente se conecta ao servidor por TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
      
      #cliente envia o nome e tamanho
        client.send(f"SEND|{name_only}|{filesize}".encode())
        #espera a mensagem do codigo gerada pelo servidor
        response = client.recv(1024).decode()
        
        if response.startswith("CODE:"):
            code = response.split(":")[1]
            print(f"\n--- CÓDIGO ATIVO: {code} ---")
            print("O arquivo está disponível para múltiplos downloads.")
            print("Pressione Ctrl+C para encerrar o compartilhamento.\n")
            
         #send fica ligado permanentemente
            while True:
                print("Aguardando solicitações de download...")
                
                #espera a confirmação de conexão feita pelo servidor
                msg = client.recv(1024).decode()
                
                if msg == "UPLOAD_NOW":
                    print(f"--> Iniciando envio para um cliente...")
                    #inicia a escrita do arquivo por bytes 
                    with open(raw_filename, 'rb') as f:
                        total_sent = 0
                        while total_sent < filesize:
                            data = f.read(4096)
                            if not data: break
                            client.send(data)
                            total_sent += len(data)
                    print(f"--> Envio concluído! Voltando a aguardar.\n")
                
                elif msg == "": 
                    print("Servidor desconectado.")
                    break
        else:
            print(f"Erro do servidor: {response}")

    except KeyboardInterrupt:
        print("\nEncerrando compartilhamento...")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

def receive_file():
    #espera inserir o codigo por terminal
    code = input("Digite o código: ")
    #conecta por TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        #envia o codigo ao servidor
        client.send(f"RECV|{code}".encode())

        #espera a mensagem de sincronia
        server_msg = client.recv(1024).decode()
        
        if server_msg.startswith("FILENM|"):
            #guarda os tamanho e nome do arquivo
            _, filename, filesize_str = server_msg.split("|")
            filesize = int(filesize_str)
            #gera um arquivo com o mesmo nome e um acrescimo com baixado_
            output_name = f"baixado_{filename}"
            print(f"Recebendo '{filename}' ({filesize} bytes)...")
            
            #inicia a transferencia
            received_total = 0
            with open(output_name, 'wb') as f:
                while received_total < filesize:
                    to_read = min(4096, filesize - received_total)
                    data = client.recv(to_read)
                    if not data: break
                    f.write(data)
                    received_total += len(data)
            
            print(f"Sucesso! Salvo como '{output_name}'")
            
        elif server_msg.startswith("ERROR:"):
            print(f"Erro: {server_msg}")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

def main():
    print("=== MULTI-USER P2P ===")
    print("1. Compartilhar Arquivo")
    print("2. Baixar Arquivo")
    choice = input("Opção: ")
    if choice == '1': send_file()
    elif choice == '2': receive_file()


main()