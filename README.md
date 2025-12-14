# SocketsWithPython

# 📂 Sistema de Transferência de Arquivos P2P

Este é um projeto de transferência de arquivos desenvolvido em **Python** utilizando **Sockets**. O sistema funciona através de um servidor intermediário que conecta dois clientes (um Enviador e um Receptor) através de um **código curto**, eliminando a necessidade de digitar endereços IP manualmente.

O sistema suporta **Multi-Threading** e **Sessões Persistentes** (Seeding), permitindo que um usuário envie o mesmo arquivo para várias pessoas sem precisar reiniciar o programa.

## 🚀 Funcionalidades

- **Conexão via Código:** O enviador recebe um código único (ex: `XKY9`) e o receptor usa esse código para baixar.
- **Modo "Seed" (Semente):** O enviador permanece online após o envio, permitindo múltiplos downloads simultâneos ou sequenciais.
- **Transferência de Metadados:** O nome original e o tamanho do arquivo são enviados automaticamente.
- **Barra de Progresso (Backend):** O sistema calcula bytes transferidos baseados no tamanho total.
- **Suporte a qualquer arquivo:** Imagens, vídeos, PDFs, executáveis, etc.
- **Tratamento de Erros:** Verificação de arquivos inexistentes, pastas e desconexões abruptas.

## 🛠️ Pré-requisitos

- Python 3.x instalado.
- Conexão de rede (Localhost para testes ou LAN/Internet).

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
   cd seu-repositorio
   ```
2. Certifique-se de ter os arquivos principais na pasta:

   server.py

   client.py

⚙️ Configurações

Antes de rodar o projeto, você precisa configurar o IP do servidor no código do cliente.

    Abra o arquivo client.py em um editor de texto ou IDE.

    Localize a variável SERVER_IP logo no início do código.

Cenário A: Teste Local (No mesmo computador) Se você vai rodar o servidor e os clientes na mesma máquina:
SERVER_IP = 'localhost'

Cenário B: Rede Local (Entre computadores diferentes no mesmo Wi-Fi)

    Descubra o IPv4 do computador onde o server.py vai rodar (comando ipconfig no Windows ou ip a no Linux).

    Coloque esse IP no arquivo client.py de todos os computadores:

SERVER_IP = '192.168.1.15' # Exemplo, coloque o seu IP real

🎮 Como Usar

Abra 3 terminais (ou abas) para simular o sistema completo.

1. Iniciar o Servidor

O servidor deve ser sempre o primeiro a ser iniciado.
python3 servidor.py

2. Enviar Arquivo (Sender)

Em um segundo terminal:
python3 cliente.py
E escolha a opção 1, logo após arraste o arquivo que irá enviar até o terminal e aperte enter

3. Receber Arquivo (Receiver)

Em um terceiro terminal:
python3 cliente.py
Escolha a opção 2, e insira o código gerado no segundo terminal
