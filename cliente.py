import socket
import os
import time

# CONFIGURAÇÃO
SERVER_IP = 'localhost' 
SERVER_PORT = 8080

def limpar_caminho_windows(caminho_bruto):
    """Limpeza cirúrgica para caminhos do Windows"""
    path = caminho_bruto.strip()
    
    # Remove artefatos do PowerShell
    if path.startswith("&"):
        path = path[1:].strip()
    
    # Remove aspas simples e duplas das pontas
    path = path.strip('"').strip("'").strip()
    
    return os.path.normpath(path)

def send_file():
    print("\n--- MODO ENVIAR ---")
    print("DICA DO WINDOWS: Segure SHIFT + Botão Direito no arquivo e escolha 'Copiar como caminho'.")
    print("Depois cole aqui.")
    
    raw_filename = input("Cole o caminho do arquivo: ")
    
    filename = limpar_caminho_windows(raw_filename)
    
    # --- ÁREA DE DEBUG (RAIO-X) ---
    print(f"\n[DEBUG] O Python entendeu: [{filename}]")
    if not os.path.exists(filename):
        print("❌ Erro: O arquivo não foi encontrado.")
        print("🔍 Raio-X da string (Códigos ASCII):")
        # Isso mostra caracteres invisíveis que podem estar atrapalhando
        print([ord(c) for c in filename])
        print("------------------------------------------------")
        return
    # ------------------------------

    filesize = os.path.getsize(filename)
    name_only = os.path.basename(filename)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        client.send(f"SEND|{name_only}|{filesize}".encode())

        response = client.recv(1024).decode()
        
        if response.startswith("CODE:"):
            code = response.split(":")[1]
            print(f"\n✅ CÓDIGO GERADO: {code}")
            print(f"Arquivo '{name_only}' ({filesize} bytes) pronto.")
            print("⏳ Modo Seed Ativo (Ctrl+C para sair)...")
            
            while True:
                msg = client.recv(1024).decode()
                if msg == "UPLOAD_NOW":
                    print(f"\n--> Enviando...")
                    with open(filename, 'rb') as f:
                        total_sent = 0
                        while total_sent < filesize:
                            data = f.read(4096)
                            if not data: break
                            client.send(data)
                            total_sent += len(data)
                    print(f"--> Concluído!")
                elif msg == "": 
                    break
        else:
            print(f"❌ Erro do servidor: {response}")

    except ConnectionRefusedError:
        print("❌ Erro: Servidor offline.")
    except KeyboardInterrupt:
        print("\n👋 Encerrado.")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        client.close()

def receive_file():
    print("\n--- MODO RECEBER ---")
    code = input("Digite o código: ").strip()
    
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
            print(f"\n📥 Recebendo: {filename} ({filesize} bytes)")
            
            received_total = 0
            with open(output_name, 'wb') as f:
                while received_total < filesize:
                    to_read = min(4096, filesize - received_total)
                    data = client.recv(to_read)
                    if not data: break
                    f.write(data)
                    received_total += len(data)
            print(f"✅ Download concluído: {output_name}")
            
        elif server_msg.startswith("ERROR:"):
            print(f"❌ Erro: {server_msg}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        client.close()

def main():
    print("=== P2P FILE TRANSFER (Texto Puro) ===")
    print("1. Enviar Arquivo")
    print("2. Receber Arquivo")
    choice = input("Escolha: ")
    if choice == '1': send_file()
    elif choice == '2': receive_file()

if __name__ == "__main__":
    main()