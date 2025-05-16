#!/bin/bash

# Verifica se o usuário deseja usar um ambiente virtual
USE_VENV=0
if [[ "$1" == "--venv" || "$1" == "-v" ]]; then
    USE_VENV=1
    echo "Usando ambiente virtual para a construção..."
fi

# Criação e ativação de ambiente virtual
if [ $USE_VENV -eq 1 ]; then
    # Verifica se o Python 3 está instalado
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 não encontrado. Por favor, instale o Python 3."
        exit 1
    fi
    
    # Cria o ambiente virtual se não existir
    if [ ! -d ".venv" ]; then
        echo "Criando ambiente virtual..."
        python3 -m venv .venv
    fi
    
    # Ativa o ambiente virtual
    echo "Ativando ambiente virtual..."
    source .venv/bin/activate
    
    # Instala dependências
    echo "Instalando dependências..."
    pip install -r requirements.txt
    pip install py2app
fi

# Limpa builds anteriores
echo "Limpando builds anteriores..."
rm -rf build dist

# Converte o ícone
echo "Convertendo ícone para formato ICNS..."
python3 convert_icon.py

# Executa o setup.py para construir o aplicativo
echo "Construindo o aplicativo..."
python3 setup.py py2app

# Verifica se a pasta Applications existe em $HOME
if [ ! -d "$HOME/Applications" ]; then
    echo "Criando diretório Applications no diretório home do usuário..."
    mkdir -p "$HOME/Applications"
fi

# Copia o aplicativo para a pasta Applications
echo "Copiando aplicativo para a pasta Applications..."
cp -R dist/Power\ Paste.app "$HOME/Applications/"

# Configura para iniciar automaticamente com o sistema
echo "Configurando inicialização automática..."
osascript -e '
tell application "System Events"
    try
        set loginItems to the name of every login item
        set needToAdd to true
        repeat with itemName in loginItems
            if itemName contains "Power Paste" then
                set needToAdd to false
                exit repeat
            end if
        end repeat
        
        if needToAdd then
            make login item at end with properties {path:"'$HOME'/Applications/Power Paste.app", hidden:false}
        end if
    end try
end tell'

echo "Aplicativo reconstruído com sucesso!"
echo "O aplicativo está disponível em $HOME/Applications/Power Paste.app"
echo "Configuração de inicialização automática aplicada."

# Desativa o ambiente virtual se estiver usando
if [ $USE_VENV -eq 1 ]; then
    echo "Desativando ambiente virtual..."
    deactivate 2>/dev/null || true
fi

# Pergunta se deseja iniciar o aplicativo
read -p "Deseja iniciar o Power Paste agora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "Iniciando o Power Paste..."
    open "$HOME/Applications/Power Paste.app"
fi 