import socket
import os
import time
import tkinter as tk
from tkinter import filedialog

# CONFIGURAÇÃO
SERVER_IP = 'localhost' 
SERVER_PORT = 8080

def selecionar_arquivo_janela():
    """Abre uma janela nativa do SO para escolher o arquivo"""
    print("Abrindo janela de seleção...")
    
    # Cria uma janela raiz invisível (necessário para o tkinter não abrir uma tela em branco)
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True) # Força a janela a aparecer na frente
    
    # Abre o explorador de arquivos
    filename = filedialog.askopenfilename(title="Selecione o arquivo para enviar")
    
    root.destroy() # Fecha o processo da janela
    return filename

def send_file():
    print("\n--- MODO ENVIAR ---")
    print("Dica: Uma janela abrirá para você selecionar o arquivo.")
    
    # --- MUDANÇA AQUI: Usa a janela em vez do input ---
    filename = selecionar_arquivo_janela()
    # --------------------------------------------------

    if not filename: # Se o usuário cancelar a janela
        print("❌ Nenhum arquivo selecionado.")
        return

    # Garante que o caminho está normalizado para o sistema atual
    filename = os.path.normpath(filename)
    print(f"DEBUG: Arquivo selecionado: [{filename}]")

    if not os.path.exists(filename):
        print("❌ Erro bizarro: O sistema selecionou mas não achou. Verifique permissões.")
        return

    # Resto do código segue normal...
    filesize = os.path.getsize(filename)
    name_only = os.path.basename(filename)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        
        # Envia cabeçalho
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
                    print(f"\n--> Receptor conectado! Enviando...")
                    with open(filename, 'rb') as f:
                        total_sent = 0
                        while total_sent < filesize:
                            data = f.read(4096)
                            if not data: break
                            client.send(data)
                            total_sent += len(data)
                    print(f"--> Envio concluído!")
                
                elif msg == "": 
                    print("⚠️ Servidor desconectado.")
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
    code = input("Digite o código de transferência: ").strip()
    
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
            
    except ConnectionRefusedError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        client.close()

def main():
    print("=== P2P FILE TRANSFER (GUI Selector) ===")
    print("1. Enviar Arquivo")
    print("2. Receber Arquivo")
    choice = input("Escolha: ")

    if choice == '1':
        send_file()
    elif choice == '2':
        receive_file()

if __name__ == "__main__":
    main()