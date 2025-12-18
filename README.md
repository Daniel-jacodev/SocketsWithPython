📂 Python P2P File Transfer (Socket TCP)

Um sistema de transferência de arquivos via rede baseado em arquitetura Cliente-Servidor (Relay). O projeto permite enviar e receber arquivos de qualquer tamanho, com verificação de integridade (Hash SHA256) e suporte a conexões via Internet (usando Ngrok) ou Rede Local.
🚀 Funcionalidades

    Transferência via TCP: Garante a integridade e ordem dos dados.

    Arquitetura Relay: O servidor atua como intermediário, permitindo conexão entre clientes mesmo atrás de NATs restritivos.

    Hash SHA256: Verifica se o arquivo recebido é idêntico ao original bit a bit.

    Chunks de 4KB: Transferência eficiente de memória (não carrega o arquivo todo na RAM).


🛠️ Pré-requisitos

    Python 3.x instalado.

    (Opcional) Ngrok: Para transferências via internet.

        Criar conta e baixar Ngrok

⚙️ Configuração e Execução

Você pode rodar este projeto de duas formas: Via Internet (pessoas em casas diferentes) ou Rede Local (mesmo Wi-Fi).
MODO 1: Via Internet (Com Ngrok) 🌍

Ideal para transferir arquivos para amigos em qualquer lugar do mundo.

1. Configurar o Ngrok (Servidor)

Abra o terminal onde está o Ngrok e inicie um túnel TCP na porta do seu servidor (padrão 19034):
Bash

ngrok tcp 19034

O Ngrok vai gerar um endereço, exemplo: tcp://0.tcp.sa.ngrok.io:12345. 2. Configurar o Cliente (client.py)

No arquivo do cliente, atualize as variáveis com os dados que o Ngrok forneceu:
Python

# Exemplo baseado na saída do Ngrok

NGROK_HOST = '0.tcp.sa.ngrok.io' # O endereço sem o 'tcp://' e sem a porta
NGROK_PORT = 12345 # O número da porta gerado pelo Ngrok

3. Rodar

   Execute o servidor: python server.py

   Execute o cliente (Remetente): python client.py

   Execute o cliente (Destinatário): python client.py

MODO 2: Rede Local (Sem Ngrok/LAN) 🏠

Ideal para transferir arquivos entre computadores no mesmo Wi-Fi ou rede cabeada. Não precisa de internet.

1. Descobrir o IP do Servidor

No computador que vai rodar o servidor, abra o terminal e digite:

    Windows: ipconfig (Procure por Endereço IPv4, ex: 192.168.0.15)

    Linux/Mac: ifconfig ou ip a

2. Configurar o Cliente (client.py)

No arquivo do cliente, aponte diretamente para o IP local do servidor e a porta padrão definida no servidor:
Python

# Coloque o IP do computador que está rodando o servidor

NGROK_HOST = '192.168.0.15'  
NGROK_PORT = 19034 # A porta original definida no server.py

3. Rodar

   Execute o servidor.

   Execute os clientes nas outras máquinas da rede.

📖 Como Usar

1.  Enviando um Arquivo

    Inicie o client.py e escolha a Opção 1.

    Cole o caminho do arquivo (pode arrastar o arquivo para o terminal).

    O programa gerará um CÓDIGO (ex: 1234).

    Envie esse código para quem vai receber.

    Aguarde a conexão. Se precisar cancelar, aperte ENTER.

2.  Recebendo um Arquivo

    Inicie o client.py e escolha a Opção 2.

    Digite o CÓDIGO fornecido pelo remetente.

    O download iniciará automaticamente.

    Ao final, o programa valida o Hash SHA256.

        ✅ SUCESSO: O arquivo é perfeito.

        ❌ PERIGO: O arquivo foi corrompido.

🧠 Como Funciona (Técnico)

O sistema utiliza sockets puros do Python. O fluxo de dados acontece da seguinte forma:

    Handshake: O remetente envia metadados (Nome, Tamanho, Hash) para o servidor.

    Matchmaking: O servidor gera um código único e aguarda um receptor com esse código.

    Tunneling: O servidor conecta as duas pontas.

    Streaming:

        O remetente lê 4KB do disco e envia para o servidor.

        O servidor recebe (buffer em RAM) e imediatamente repassa para o receptor.

        O receptor escreve 4KB no disco.

        Nota: O arquivo não fica salvo no servidor, apenas passa pela memória volátil.
