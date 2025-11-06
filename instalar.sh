#!/bin/bash

# ========================================
# WZIN BOT - INSTALADOR AUTOMÁTICO
# GitHub: https://github.com/werbertofc/wzinbot.git
# Criado por @werbert_ofc
# ========================================

echo "WZIN BOT - INSTALADOR OFICIAL"
echo "Atualizando sistema..."

# Atualiza pacotes
sudo apt update -y && sudo apt upgrade -y

# Instala dependências do sistema
sudo apt install -y python3 python3-pip python3-venv git curl

# Define diretório do bot
BOT_DIR="$HOME/wzin_bot"

# Remove pasta antiga (se existir)
if [ -d "$BOT_DIR" ]; then
    echo "Removendo instalação antiga..."
    rm -rf "$BOT_DIR"
fi

# Clona o repositório
echo "Clonando repositório do GitHub..."
git clone https://github.com/werbertofc/wzinbot.git "$BOT_DIR"

# Entra na pasta
cd "$BOT_DIR" || exit

# Cria ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv

# Ativa o ambiente
source venv/bin/activate

# Atualiza pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instala Telethon
echo "Instalando Telethon..."
pip install telethon

# Verifica se bot.py existe
if [ ! -f "bot.py" ]; then
    echo "ERRO: bot.py não encontrado!"
    echo "Verifique o repositório: https://github.com/werbertofc/wzinbot"
    exit 1
fi

# Pergunta se quer iniciar agora
read -p "Deseja iniciar o bot agora? (s/N): " iniciar
if [[ $iniciar =~ ^[Ss]$ ]]; then
    echo "Iniciando o bot..."
    python bot.py
else
    echo ""
    echo "INSTALAÇÃO CONCLUÍDA!"
    echo ""
    echo "Para iniciar o bot:"
    echo "   cd ~/wzin_bot"
    echo "   source venv/bin/activate"
    echo "   python bot.py"
    echo ""
    echo "Para rodar em segundo plano (recomendado):"
    echo "   screen -S wzinbot"
    echo "   source venv/bin/activate"
    echo "   python bot.py"
    echo "   (pressione Ctrl+A, D para sair do screen)"
    echo ""
    echo "Bot by @werbert_ofc"
fi
