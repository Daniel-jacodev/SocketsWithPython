import socket
import os
import time

SERVER_IP = 'localhost'
SERVER_PORT = 8080

def send_file():
    raw_filename = input("Digite o caminho do arquivo: ").strip().replace("'", "").replace('"', "")
    
    if not os.path.exists(raw_filename):
        print("Erro: Arquivo não existe.")
        return

    filesize = os.path.getsize(raw_filename)
    name_only = os.path.basename(raw_filename)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        
       
        client.send(f"SEND|{name_only}|{filesize}".encode())

        response = client.recv(1024).decode()
        
        if response.startswith("CODE:"):
            code = response.split(":")[1]
            print(f"\n--- CÓDIGO ATIVO: {code} ---")
            print("O arquivo está disponível para múltiplos downloads.")
            print("Pressione Ctrl+C para encerrar o compartilhamento.\n")
            
            # === LOOP DE SEMEADURA (SEEDING) ===
            while True:
                print("Aguardando solicitações de download...")
                
                # Fica esperando o servidor dizer "UPLOAD_NOW"
                msg = client.recv(1024).decode()
                
                if msg == "UPLOAD_NOW":
                    print(f"--> Iniciando envio para um cliente...")
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
    code = input("Digite o código: ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        client.send(f"RECV|{code}".encode())

        server_msg = client.recv(1024).decode()
        
        if server_msg.startswith("FILENM|"):
            _, filename, filesize_str = server_msg.split("|")
            filesize = int(filesize_str)
            
            output_name = f"baixado_{filename}"
            print(f"Recebendo '{filename}' ({filesize} bytes)...")
            
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
    print("1. Compartilhar Arquivo (Fica online)")
    print("2. Baixar Arquivo")
    choice = input("Opção: ")
    if choice == '1': send_file()
    elif choice == '2': receive_file()

if __name__ == "__main__":
    main()