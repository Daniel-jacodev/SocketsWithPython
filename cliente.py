import socket
import os
import sys
import platform
import subprocess # Vamos usar isso para chamar o Windows

# CONFIGURAÇÃO
SERVER_IP = 'localhost' 
SERVER_PORT = 8080

def selecionar_arquivo_universal():
    sistema = platform.system()
    
    # --- ESTRATÉGIA PARA WINDOWS (Janela Visual sem Biblioteca Extra) ---
    if sistema == "Windows":
        print("Abrindo janela de seleção de arquivo do Windows...")
        # Comando de PowerShell que cria uma janela de abrir arquivo
        comando_ps = """
        Add-Type -AssemblyName System.Windows.Forms;
        $f = New-Object System.Windows.Forms.OpenFileDialog;
        $f.Filter = "Todos os arquivos (*.*)|*.*";
        $f.Title = "Selecione o arquivo para enviar via P2P";
        $f.ShowHelp = $true;
        $f.ShowDialog() | Out-Null;
        $f.FileName
        """
        
        try:
            # Executa o comando e captura o resultado
            resultado = subprocess.check_output(["powershell", "-command", comando_ps], shell=True)
            caminho = resultado.decode().strip()
            
            if not caminho:
                print("❌ Nenhum arquivo foi selecionado na janela.")
                return None
            
            print(f"✅ O Windows retornou: {caminho}")
            return caminho
            
        except Exception as e:
            print(f"Erro ao abrir janela do Windows: {e}")
            print("Tentando método manual...")
            return input("Cole o caminho do arquivo aqui: ").strip().strip('"')

    # --- ESTRATÉGIA PARA LINUX / MAC (Drag & Drop funciona bem) ---
    else:
        # No Linux, apenas limpamos as aspas simples/duplas e espaços
        raw = input("Arrasta o arquivo para cá: ")
        return raw.strip().replace("'", "").replace('"', "")

def send_file():
    print("\n--- MODO ENVIAR ---")
    
    # Chama nossa função híbrida (Janela no Windows, Texto no Linux)
    filename = selecionar_arquivo_universal()
    
    if not filename or not os.path.exists(filename):
        print("❌ Erro: Arquivo inválido ou não encontrado.")
        return

    filesize = os.path.getsize(filename)
    name_only = os.path.basename(filename)

    print(f"DEBUG: Enviando '{name_only}' de {filesize} bytes")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        
        # Protocolo: SEND | NOME | TAMANHO
        client.send(f"SEND|{name_only}|{filesize}".encode())

        response = client.recv(1024).decode()
        
        if response.startswith("CODE:"):
            code = response.split(":")[1]
            print(f"\n✅ CÓDIGO GERADO: {code}")
            print("⏳ Aguardando receptor (Modo Seed)... Pressione Ctrl+C para sair.")
            
            while True:
                msg = client.recv(1024).decode()
                if msg == "UPLOAD_NOW":
                    print(f"\n--> Iniciando envio...")
                    with open(filename, 'rb') as f:
                        total_sent = 0
                        while total_sent < filesize:
                            data = f.read(4096)
                            if not data: break
                            client.send(data)
                            total_sent += len(data)
                    print(f"--> Envio concluído!")
                elif msg == "": 
                    print("Servidor desconectado.")
                    break
        else:
            print(f"❌ Erro do servidor: {response}")

    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
    except Exception as e:
        print(f"Erro de conexão: {e}")
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
            print(f"✅ Download completo: {output_name}")
            
        elif server_msg.startswith("ERROR:"):
            print(f"❌ Erro: {server_msg}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.close()

def main():
    print(f"=== P2P TRANSFER ({platform.system().upper()}) ===")
    print("1. Enviar Arquivo")
    print("2. Receber Arquivo")
    choice = input("Opção: ")
    if choice == '1': send_file()
    elif choice == '2': receive_file()

if __name__ == "__main__":
    main()