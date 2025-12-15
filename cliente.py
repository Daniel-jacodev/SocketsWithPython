import socket
import os
import time

SERVER_IP = 'localhost'
SERVER_PORT = 8080

def limpar_caminho(caminho_bruto):
    """
    Remove aspas, espaços e caracteres especiais do PowerShell (&)
    que atrapalham no Windows.
    """
    # 1. Remove espaços em branco nas pontas
    caminho = caminho_bruto.strip()
    
    # 2. Remove aspas simples e duplas (comum em ambos os sistemas)
    caminho = caminho.replace("'", "").replace('"', "")
    
    # 3. Correção específica para Windows PowerShell (Remove o '& ' do início)
    if caminho.startswith("& "):
        caminho = caminho[2:]
    elif caminho.startswith("&"):
        caminho = caminho[1:]
        
    # 4. Remove espaços extras que podem ter sobrado após tirar o '&'
    caminho = caminho.strip()

    # 5. Normaliza as barras (Converte / para \ no Windows automaticamente)
    return os.path.normpath(caminho)

def send_file():
    print("\n--- MODO ENVIAR ---")
    raw_filename = input("Digite o caminho do arquivo: ")
    
    # CHAMA A FUNÇÃO DE LIMPEZA AQUI
    filename = limpar_caminho(raw_filename)
    
    print(f"DEBUG: Tentando abrir -> [{filename}]")

    if not os.path.exists(filename):
        print("❌ Erro: Arquivo não existe.")
        print("Dica: Tente digitar o caminho manualmente se arrastar não funcionar.")
        return

    # Resto do código segue igual...
    filesize = os.path.getsize(filename)
    name_only = os.path.basename(filename)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        
        # Envia: SEND | NOME | TAMANHO
        client.send(f"SEND|{name_only}|{filesize}".encode())

        response = client.recv(1024).decode()
        
        if response.startswith("CODE:"):
            code = response.split(":")[1]
            print(f"\n✅ CÓDIGO ATIVO: {code}")
            print(f"Arquivo '{name_only}' ({filesize} bytes) pronto.")
            print("O arquivo está disponível para múltiplos downloads.")
            print("Pressione Ctrl+C para encerrar o compartilhamento.\n")
            
            # === LOOP DE SEMEADURA (SEEDING) ===
            while True:
                print("Aguardando solicitações de download...")
                
                msg = client.recv(1024).decode()
                
                if msg == "UPLOAD_NOW":
                    print(f"--> Iniciando envio para um cliente...")
                    with open(filename, 'rb') as f:
                        total_sent = 0
                        while total_sent < filesize:
                            data = f.read(4096)
                            if not data: break
                            client.send(data)
                            total_sent += len(data)
                    print(f"--> Envio concluído! Voltando a aguardar.\n")
                
                elif msg == "": 
                    print("⚠️ Servidor desconectado.")
                    break
        else:
            print(f"Erro do servidor: {response}")

    except KeyboardInterrupt:
        print("\nEncerrando compartilhamento...")
    except ConnectionRefusedError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
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
            parts = server_msg.split("|")
            filename = parts[1]
            filesize = int(parts[2])
            
            output_name = f"baixado_{filename}"
            print(f"\n📥 Recebendo '{filename}' ({filesize} bytes)...")
            
            received_total = 0
            with open(output_name, 'wb') as f:
                while received_total < filesize:
                    to_read = min(4096, filesize - received_total)
                    data = client.recv(to_read)
                    if not data: break
                    f.write(data)
                    received_total += len(data)
            
            print(f"✅ Sucesso! Salvo como '{output_name}'")
            
        elif server_msg.startswith("ERROR:"):
            print(f"Erro: {server_msg}")
            
    except ConnectionRefusedError:
         print("❌ Erro: Não foi possível conectar ao servidor.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

def main():
    print("=== MULTI-USER P2P (Windows/Linux Compatible) ===")
    print("1. Compartilhar Arquivo (Fica online)")
    print("2. Baixar Arquivo")
    choice = input("Opção: ")
    if choice == '1': send_file()
    elif choice == '2': receive_file()

if __name__ == "__main__":
    main()