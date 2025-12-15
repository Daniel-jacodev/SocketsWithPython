import socket
import os

# Se for rodar localmente use 'localhost'. 
# Se for pela internet, coloque o IP Público do servidor.
SERVER_IP = 'localhost' 
SERVER_PORT = 8080

def send_file():
    # Recebe o caminho bruto
    raw_filename = input("Digite o caminho do arquivo para enviar: ")
    
    # 1. .strip() remove espaços vazios no começo e fim
    # 2. .replace() remove aspas simples (') e duplas (") que o terminal adiciona
    filename = raw_filename.strip().replace("'", "").replace('"', "")
    
    # Dica: Vamos imprimir para ver como ficou o caminho limpo
    print(f"Procurando por: {filename}") 

    if not os.path.exists(filename):
        print("Erro: Arquivo não encontrado. Verifique o caminho.")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    # Envia cabeçalho: SEND|nome_do_arquivo
    name_only = os.path.basename(filename)
    client.send(f"SEND|{name_only}".encode())

    # Recebe o código do servidor
    response = client.recv(1024).decode()
    if response.startswith("CODE:"):
        code = response.split(":")[1]
        print(f"\n--- CÓDIGO DE TRANSFERÊNCIA: {code} ---")
        print("Aguardando receptor conectar...")
        
        # Espera o servidor dizer "START"
        msg = client.recv(1024).decode()
        if msg == "START":
            print("Receptor conectado! Enviando arquivo...")
            with open(filename, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    client.send(data)
            print("Arquivo enviado com sucesso!")
            client.close()
def receive_file():
    code = input("Digite o código de transferência: ")
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    # Envia intenção: RECV|codigo
    client.send(f"RECV|{code}".encode())

    # Começa a receber os dados
    # (Num sistema real, deveríamos receber o nome do arquivo primeiro, 
    # mas vamos simplificar salvando como 'recebido_output')
    print("Baixando arquivo...")
    
    with open(f"recebido_{code}.dat", 'wb') as f:
        while True:
            data = client.recv(4096)
            if not data:
                break
            f.write(data)
    
    print(f"Arquivo recebido e salvo como 'recebido_{code}.dat'!")
    client.close()

def main():
    print("1. Enviar Arquivo")
    print("2. Receber Arquivo")
    choice = input("Escolha: ")

    if choice == '1':
        send_file()
    elif choice == '2':
        receive_file()

if __name__ == "__main__":
    main()