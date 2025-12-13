# SocketsWithPython

# 📂 Sistema de Transferência de Arquivos P2P (Relay)

Este é um projeto de transferência de arquivos desenvolvido em **Python** utilizando **Sockets**. O sistema funciona através de um servidor intermediário (Relay) que conecta dois clientes (um Enviador e um Receptor) através de um **código curto**, eliminando a necessidade de digitar endereços IP manualmente.

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
