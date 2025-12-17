import socket 
import os 
import platform 
import hashlib 



NGROK_HOST = '0.tcp.sa.ngrok.io'
NGROK_PORT = 19034       


SERVER_IP = ""     
SERVER_PORT = NGROK_PORT

def calcular_hash(caminho):
    sha256 = hashlib.sha256()
    with open(caminho, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def corrigir_caminho(caminho_original):
    caminho = caminho_original.strip().strip('"').strip("'")
    
    # if platform.system() == "Windows" and caminho.startswith("&"):
    #     caminho = caminho[1:].strip()

    if os.path.exists(caminho):
        return caminho

    # pastas_comuns = ["Desktop", "Documents", "Pictures", "Imagens", "Documentos", "Área de Trabalho"]
    
    # for pasta in pastas_comuns:
    #     if pasta in caminho:
    #         caminho_onedrive = caminho.replace(pasta, f"OneDrive{os.sep}{pasta}")
    #         if os.path.exists(caminho_onedrive):
    #             print(f"✅ ACHEI! O arquivo está em: {caminho_onedrive}")
    #             return caminho_onedrive

    # return None

def send_file():
    print("\n--- MODO ENVIAR ---")
    print("Pode arrastar o arquivo para cá, eu resolvo o caminho.")
    
    raw_input = input("Caminho: ")
    filename = corrigir_caminho(raw_input)
    
    if not filename:
        print("\n❌ ERRO FATAL: Arquivo não encontrado.")
        return

    print("⏳ Calculando Hash e lendo arquivo...")
    file_hash = calcular_hash(filename)
    filesize = os.path.getsize(filename)
    name_only = os.path.basename(filename)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Usa o IP que descobrimos no início
        print(f"📡 Conectando em {SERVER_IP}:{SERVER_PORT}...")
        client.connect((SERVER_IP, SERVER_PORT))
        
        # Protocolo de envio
        client.send(f"SEND|{name_only}|{filesize}|{file_hash}".encode())

        response = client.recv(1024).decode()
        
        if response.startswith("CODE:"):
            code = response.split(":")[1]
            print(f"\n✅ CÓDIGO GERADO: {code}")
            print("⚠️  Passe este código para quem vai receber o arquivo.")
            print("⏳ Aguardando o receptor conectar... (Não feche esta janela)")
            
            while True:
                msg = client.recv(1024).decode()
                if msg == "UPLOAD_NOW":
                    print(f"--> Iniciando transferência...")
                    with open(filename, 'rb') as f:
                        total_sent = 0
                        while total_sent < filesize:
                            data = f.read(4096)
                            if not data: break
                            client.send(data)
                            total_sent += len(data)
                            # Opcional: Mostrar progresso
                            # print(f"Enviado: {total_sent}/{filesize}", end='\r')
                    print(f"\n--> Sucesso! Transferência concluída.")
                    print("Conexão aberta, para mais transferências, caso deseje fechar, aperte Ctrl + C")
                elif msg == "": 
                    print("Conexão perdida.")
                    break
        else:
            print(f"Erro no servidor: {response}")

    except KeyboardInterrupt:
        print("\nCancelado pelo usuário.")
    except Exception as e:
        print(f"Erro de conexão: {e}")
    finally:
        client.close()

def receive_file():
    print("\n--- MODO RECEBER ---")
    code = input("Digite o código fornecido por quem envia: ").strip()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"📡 Conectando em {SERVER_IP}:{SERVER_PORT}...")
        client.connect((SERVER_IP, SERVER_PORT))
        client.send(f"RECV|{code}".encode())

        server_msg = client.recv(1024).decode()
        
        if server_msg.startswith("FILENM|"):
            parts = server_msg.split("|")
            filename = parts[1]
            filesize = int(parts[2])
            hash_recebido = parts[3]
            
            output_name = f"baixado_{filename}"
            print(f"\n📥 Recebendo arquivo: {filename}")
            print(f"📦 Tamanho: {filesize} bytes")

            # Confirma recebimento dos metadados
            client.send("OK".encode())
            
            received_total = 0
            with open(output_name, 'wb') as f:
                while received_total < filesize:
                    to_read = min(4096, filesize - received_total)
                    data = client.recv(to_read)
                    if not data: break
                    f.write(data)
                    received_total += len(data)
            
            print(f"✅ Download concluído: {output_name}")
            print("⏳ Verificando integridade (Hash)...")
            
            hash_calculado = calcular_hash(output_name)

            if hash_calculado == hash_recebido:
                 print("✅ SUCESSO! O arquivo é idêntico ao original.")
            else:
                print("❌ PERIGO: O hash não bate! O arquivo pode estar corrompido.")
            
        elif server_msg.startswith("ERROR:"):
            print(f"Erro do servidor: {server_msg}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

def main():
    global SERVER_IP
    
    print("=== P2P FILE TRANSFER (CLIENTE) ===")
    print(f"Resolvendo DNS para: {NGROK_HOST}...")
    
    # --- O TRUQUE PARA O PROFESSOR ---
    try:
        SERVER_IP = socket.gethostbyname(NGROK_HOST)
        print(f"✅ Endereço resolvido!")
        print(f"   URL: {NGROK_HOST}")
        print(f"   IP Real: {SERVER_IP}  <-- Conectando via IP")
    except socket.gaierror:
        print("❌ ERRO: Não foi possível encontrar o IP do Ngrok.")
        print("Verifique se digitou o endereço correto no código.")
        return

    print("-----------------------------------")
    print("1. Enviar Arquivo")
    print("2. Receber Arquivo")
    opcao = input("Opção: ")
    
    if opcao == '1': 
        send_file()
    elif opcao == '2': 
        receive_file()
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()