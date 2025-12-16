import socket
import os
import platform

# CONFIGURAÇÃO
SERVER_IP = 'localhost'
SERVER_PORT = 8080

def corrigir_caminho_onedrive(caminho_original):
    """
    Tenta consertar o caminho 'mentiroso' que o Windows entrega
    quando os arquivos estão no OneDrive.
    """
    # 1. Limpeza básica (aspas e espaços)
    caminho = caminho_original.strip().strip('"').strip("'")
    
    # Se for Windows, remove o '& ' do PowerShell se houver
    if platform.system() == "Windows" and caminho.startswith("&"):
        caminho = caminho[1:].strip()

    # Se o arquivo existe do jeito que veio, ótimo!
    if os.path.exists(caminho):
        return caminho

    # --- A MÁGICA DO ONEDRIVE AQUI ---
    print(f"❌ Caminho padrão falhou: {caminho}")
    print("🔍 Tentando procurar dentro do OneDrive...")

    # Lista de pastas que o OneDrive costuma "sequestrar"
    pastas_comuns = ["Desktop", "Documents", "Pictures", "Imagens", "Documentos", "Área de Trabalho"]
    
    path_parts = caminho.split(os.sep) # Separa as pastas (C:, Users, Weslem...)
    
    # Tenta injetar 'OneDrive' antes das pastas comuns
    for pasta in pastas_comuns:
        if pasta in caminho:
            # Substitui 'Pictures' por 'OneDrive\Pictures'
            caminho_onedrive = caminho.replace(pasta, f"OneDrive{os.sep}{pasta}")
            
            if os.path.exists(caminho_onedrive):
                print(f"✅ ACHEI! O arquivo real está em: {caminho_onedrive}")
                return caminho_onedrive

    # Se chegou aqui, não achou nem no OneDrive
    return None

def send_file():
    print("\n--- MODO ENVIAR (Correção OneDrive Ativa) ---")
    print("Pode arrastar o arquivo para cá, eu resolvo o caminho.")
    
    raw_input = input("Caminho: ")
    
    filename = corrigir_caminho_onedrive(raw_input)

    if not filename:
        print("\n❌ ERRO FATAL: Arquivo não encontrado nem no local original, nem no OneDrive.")
        print("DICA DE OURO: Copie o arquivo para a mesma pasta deste script (cliente.py) e digite apenas o nome dele.")
        return

    filesize = os.path.getsize(filename)
    name_only = os.path.basename(filename)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        client.send(f"SEND|{name_only}|{filesize}".encode())

        response = client.recv(1024).decode()
        
        if response.startswith("CODE:"):
            code = response.split(":")[1]
            print(f"\n✅ CÓDIGO ATIVO: {code}")
            print("⏳ Semeando arquivo... (Ctrl+C para parar)")
            
            while True:
                msg = client.recv(1024).decode()
                if msg == "UPLOAD_NOW":
                    print(f"--> Enviando dados...")
                    with open(filename, 'rb') as f:
                        total_sent = 0
                        while total_sent < filesize:
                            data = f.read(4096)
                            if not data: break
                            client.send(data)
                            total_sent += len(data)
                    print(f"--> Sucesso! Aguardando próximo...")
                elif msg == "": 
                    print("Servidor caiu.")
                    break
        else:
            print(f"Erro no servidor: {response}")

    except KeyboardInterrupt:
        print("\nEncerrado.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

def receive_file():
    print("\n--- MODO RECEBER ---")
    code = input("Digite o código: ").strip()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        client.send(f"RECV|{code}".encode())

        # Recebe os metadados (agora vem limpo, sem pedaço de foto junto)
        server_msg = client.recv(1024).decode()
        
        if server_msg.startswith("FILENM|"):
            parts = server_msg.split("|")
            filename = parts[1]
            filesize = int(parts[2])
            
            output_name = f"baixado_{filename}"
            print(f"\n📥 Recebendo: {filename} ({filesize} bytes)")

            # === [CORREÇÃO AQUI] ===
            # Avisa o servidor: "Já li o nome do arquivo. Pode mandar os dados!"
            client.send("OK".encode())
            # =======================
            
            received_total = 0
            with open(output_name, 'wb') as f:
            # ... (resto do código continua igual)
                while received_total < filesize:
                    to_read = min(4096, filesize - received_total)
                    data = client.recv(to_read)
                    if not data: break
                    f.write(data)
                    received_total += len(data)
            print(f"✅ Salvo como: {output_name}")
            
        elif server_msg.startswith("ERROR:"):
            print(f"Erro: {server_msg}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

def main():
    print("=== P2P FILE TRANSFER ===")
    print("1. Enviar")
    print("2. Receber")
    if input("Opção: ") == '1': send_file()
    else: receive_file()

if __name__ == "__main__":
    main()