#!/usr/bin/env python3
"""
Script para criar o arquivo DMG do Power Paste com um único instalador.
Este script:
1. Compila o aplicativo usando py2app
2. Cria a estrutura de diretórios para o DMG
3. Copia o aplicativo e o instalador para o DMG
4. Gera o arquivo .dmg final
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Configurações
APP_NAME = "Power Paste"
DMG_NAME = "Power Paste.dmg"
VERSION = "1.3"

def run_command(cmd):
    """Executa um comando e retorna seu status"""
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao executar {' '.join(cmd)}:")
        print(result.stderr)
        return False
    return True

def cleanup():
    """Remove arquivos temporários e compilações anteriores"""
    print("Limpando arquivos temporários...")
    
    # Remove diretórios de build anteriores
    for dir_to_remove in ["build", "dist"]:
        if os.path.exists(dir_to_remove):
            shutil.rmtree(dir_to_remove)
    
    # Remove o arquivo DMG antigo
    if os.path.exists(DMG_NAME):
        os.remove(DMG_NAME)

def build_app():
    """Compila o aplicativo usando py2app"""
    print(f"Compilando o aplicativo {APP_NAME}...")
    
    # Verifica se o ambiente virtual está ativado
    if not os.environ.get('VIRTUAL_ENV'):
        print("AVISO: Ambiente virtual não detectado. Recomenda-se usar um venv.")
    
    # Compila o aplicativo
    if not run_command(["python3", "setup.py", "py2app"]):
        print("Erro ao compilar o aplicativo!")
        return False
    
    # Verifica se a compilação foi bem-sucedida
    app_path = f"dist/{APP_NAME}.app"
    if not os.path.exists(app_path):
        print(f"Erro: {app_path} não foi criado!")
        return False
    
    return True

def prepare_dmg_structure():
    """Prepara a estrutura de diretórios para o DMG"""
    print("Preparando estrutura do DMG...")
    
    # Cria diretório para o DMG
    dmg_build_dir = "build/dmg"
    os.makedirs(dmg_build_dir, exist_ok=True)
    
    # Copia o aplicativo para o diretório do DMG
    app_src = f"dist/{APP_NAME}.app"
    app_dest = f"{dmg_build_dir}/{APP_NAME}.app"
    
    if os.path.exists(app_dest):
        shutil.rmtree(app_dest)
    
    shutil.copytree(app_src, app_dest)
    
    # Copia o ícone
    icon_src = "icon.png"
    icon_dest = f"{dmg_build_dir}/icon.png"
    shutil.copy2(icon_src, icon_dest)
    
    # Cria o arquivo install.command
    create_installer_script(dmg_build_dir)
    
    # Cria o README.txt
    create_readme(dmg_build_dir)
    
    # Torna os scripts executáveis
    os.chmod(f"{dmg_build_dir}/install.command", 0o755)
    
    return dmg_build_dir

def create_installer_script(dmg_dir):
    """Cria o script de instalação"""
    print("Criando script de instalação...")
    
    # Conteúdo do script installer.command
    installer_script = """#!/bin/bash

# Power Paste Installer - Instalador com seleção de idioma
clear
echo "=== Power Paste Installer ==="
echo "Iniciando instalação..."

# Caminhos
APP_NAME="Power Paste.app"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_PATH="$SCRIPT_DIR/Power Paste.app"
DEST_PATH="$HOME/Applications/$APP_NAME"
ICON_PATH="$SCRIPT_DIR/Power Paste.app/Contents/Resources/icon.png"

# Verifica se o ícone existe
if [ ! -f "$ICON_PATH" ]; then
    # Tenta encontrar o ícone em outros locais comuns
    if [ -f "$SCRIPT_DIR/icon.png" ]; then
        ICON_PATH="$SCRIPT_DIR/icon.png"
    elif [ -f "/Volumes/Power Paste/icon.png" ]; then
        ICON_PATH="/Volumes/Power Paste/icon.png"
    fi
fi

# Função para mostrar diálogo com ícone
mostrar_dialogo() {
    if [ -f "$ICON_PATH" ]; then
        osascript <<EOD
        tell application "System Events"
            set theIcon to (POSIX file "$ICON_PATH")
            set theResult to display dialog "$1" buttons {"$2", "$3", "$4"} default button "$4" with title "Power Paste Installer" with icon file (theIcon as string)
            return button returned of theResult
        end tell
EOD
    else
        osascript <<EOD
        tell application "System Events"
            set theResult to display dialog "$1" buttons {"$2", "$3", "$4"} default button "$4" with title "Power Paste Installer" with icon note
            return button returned of theResult
        end tell
EOD
    fi
}

# Função para mostrar mensagem
mostrar_mensagem() {
    if [ -f "$ICON_PATH" ]; then
        osascript <<EOD
        tell application "System Events"
            set theIcon to (POSIX file "$ICON_PATH")
            display dialog "$1" buttons {"OK"} default button "OK" with title "Power Paste Installer" with icon file (theIcon as string)
        end tell
EOD
    else
        osascript <<EOD
        tell application "System Events"
            display dialog "$1" buttons {"OK"} default button "OK" with title "Power Paste Installer" with icon note
        end tell
EOD
    fi
}

# Encerra qualquer instância existente do Power Paste
echo "Verificando instalação anterior..."
pkill -f "Power Paste" > /dev/null 2>&1
killall "Power Paste" > /dev/null 2>&1
osascript -e 'tell application "Power Paste" to quit' > /dev/null 2>&1
sleep 1

# Verifica se o arquivo fonte existe
if [ ! -d "$SOURCE_PATH" ]; then
    # Tenta encontrar em outros lugares comuns
    if [ -d "$SCRIPT_DIR/../$APP_NAME" ]; then
        SOURCE_PATH="$SCRIPT_DIR/../$APP_NAME"
    elif [ -d "/Volumes/Power Paste/$APP_NAME" ]; then
        SOURCE_PATH="/Volumes/Power Paste/$APP_NAME"
    else
        mostrar_mensagem "Não foi possível encontrar o aplicativo para instalar. Verifique se está executando o instalador do DMG original."
        exit 1
    fi
fi

# Selecionar o idioma com bandeiras
LANGUAGE=$(mostrar_dialogo "Escolha o idioma do Power Paste / Choose language / Escolha a língua:" "🇧🇷 Português BR" "🇵🇹 Português PT" "🇺🇸 English")

# Configura o idioma escolhido
case "$LANGUAGE" in
    *"BR"*) 
        IDIOMA="pt_BR"
        IDIOMA_TEXTO="Português do Brasil"
        ;;
    *"PT"*) 
        IDIOMA="pt_PT"
        IDIOMA_TEXTO="Português de Portugal"
        ;;
    *) 
        IDIOMA="en_US"
        IDIOMA_TEXTO="English"
        ;;
esac

# Cria o arquivo de configuração do idioma
echo "Configurando idioma: $IDIOMA_TEXTO"
mkdir -p "$HOME/.power_paste"
echo "$IDIOMA" > "$HOME/.power_paste/language"

# Certifica-se de que a pasta Applications do usuário existe
if [ ! -d "$HOME/Applications" ]; then
    echo "Criando pasta Applications no diretório do usuário..."
    mkdir -p "$HOME/Applications"
fi

# Remove instalação anterior se existir
if [ -d "$DEST_PATH" ]; then
    echo "Removendo instalação anterior..."
    rm -rf "$DEST_PATH"
fi

# Remove itens de login antigos via AppleScript
echo "Limpando configurações de inicialização anteriores..."
osascript <<EOD
tell application "System Events"
    try
        set loginItems to the name of every login item
        repeat with itemName in loginItems
            if itemName contains "Power Paste" then
                delete login item itemName
            end if
        end repeat
    end try
end tell
EOD

# Copia o aplicativo para a pasta Applications do usuário
echo "Instalando Power Paste..."
cp -R "$SOURCE_PATH" "$DEST_PATH"
if [ ! -d "$DEST_PATH" ]; then
    mostrar_mensagem "Falha ao copiar o aplicativo. Verifique as permissões do diretório de destino."
    exit 1
fi

# Configura permissões
chmod -R 755 "$DEST_PATH"

# Adiciona ao Login Items para iniciar com o sistema
echo "Configurando inicialização automática..."
osascript <<EOD
tell application "System Events"
    make login item at end with properties {path:"$DEST_PATH", hidden:false}
end tell
EOD

# Mensagens em diferentes idiomas
case "$IDIOMA" in
    "pt_BR")
        MSG_INICIANDO="Iniciando o Power Paste..."
        MSG_TENTATIVA="Tentativa %d: Aguardando o aplicativo iniciar..."
        MSG_SUCESSO="Power Paste foi instalado com sucesso!\\n\\nO ícone do Power Paste está na barra de menus (canto superior direito).\\nIdioma: Português do Brasil\\n\\nO aplicativo será iniciado automaticamente quando você fizer login."
        MSG_FALHA="Power Paste foi instalado mas pode não estar visível na barra de menus.\\n\\nPara iniciar manualmente:\\n1. Abra o Finder\\n2. Vá para a pasta Aplicativos no seu diretório de usuário\\n3. Clique duas vezes em \\"Power Paste\\""
        MSG_TITULO_SUCESSO="Instalação Concluída"
        MSG_TITULO_FALHA="Instalação Concluída com Avisos"
        ;;
    "pt_PT")
        MSG_INICIANDO="A iniciar o Power Paste..."
        MSG_TENTATIVA="Tentativa %d: A aguardar a inicialização da aplicação..."
        MSG_SUCESSO="O Power Paste foi instalado com sucesso!\\n\\nO ícone do Power Paste está na barra de menus (canto superior direito).\\nIdioma: Português de Portugal\\n\\nA aplicação será iniciada automaticamente quando iniciar sessão."
        MSG_FALHA="O Power Paste foi instalado mas pode não estar visível na barra de menus.\\n\\nPara iniciar manualmente:\\n1. Abra o Finder\\n2. Vá para a pasta Aplicações no seu diretório pessoal\\n3. Faça duplo clique em \\"Power Paste\\""
        MSG_TITULO_SUCESSO="Instalação Concluída"
        MSG_TITULO_FALHA="Instalação Concluída com Avisos"
        ;;
    *)
        MSG_INICIANDO="Starting Power Paste..."
        MSG_TENTATIVA="Attempt %d: Waiting for the application to start..."
        MSG_SUCESSO="Power Paste was successfully installed!\\n\\nThe Power Paste icon is in the menu bar (top right corner).\\nLanguage: English\\n\\nThe application will start automatically when you log in."
        MSG_FALHA="Power Paste was installed but may not be visible in the menu bar.\\n\\nTo start manually:\\n1. Open Finder\\n2. Go to the Applications folder in your user directory\\n3. Double-click \\"Power Paste\\""
        MSG_TITULO_SUCESSO="Installation Complete"
        MSG_TITULO_FALHA="Installation Complete with Warnings"
        ;;
esac

# Inicia o aplicativo
echo "$MSG_INICIANDO"
open "$DEST_PATH"
sleep 2

# Verifica se está realmente em execução
IS_RUNNING=false
for i in {1..5}; do
    # Verifica usando ps
    PS_COUNT=$(ps aux | grep -v grep | grep -c "Power Paste")
    # Verifica usando AppleScript
    PROCESS_COUNT=$(osascript -e 'tell application "System Events" to count (every process whose name is "Power Paste")' 2>/dev/null || echo "0")
    
    if [ "$PS_COUNT" -gt "0" ] || [ "$PROCESS_COUNT" -gt "0" ]; then
        IS_RUNNING=true
        break
    fi
    
    printf "$MSG_TENTATIVA\\n" $i
    open "$DEST_PATH"  # Tenta iniciar novamente
    sleep 2
done

# Mostra mensagem final com base no resultado
if [ "$IS_RUNNING" = true ]; then
    # Tenta destacar o ícone na barra de menu
    osascript <<EOD
    tell application "System Events"
        try
            tell process "Power Paste"
                set frontmost to true
                click menu bar item 1 of menu bar 1
                delay 0.5
                key code 53  # ESC key
            end tell
        end try
    end tell
EOD
    
    # Mostra mensagem de sucesso
    if [ -f "$ICON_PATH" ]; then
        osascript <<EOD
        tell application "System Events"
            set theIcon to (POSIX file "$ICON_PATH")
            display dialog "$MSG_SUCESSO" buttons {"OK"} default button "OK" with title "$MSG_TITULO_SUCESSO" with icon file (theIcon as string)
        end tell
EOD
    else
        osascript -e "display dialog \\"$MSG_SUCESSO\\" buttons {\\"OK\\"} default button \\"OK\\" with title \\"$MSG_TITULO_SUCESSO\\" with icon note"
    fi
else
    # Mostra mensagem de alerta com instruções para iniciar manualmente
    if [ -f "$ICON_PATH" ]; then
        osascript <<EOD
        tell application "System Events"
            set theIcon to (POSIX file "$ICON_PATH")
            display dialog "$MSG_FALHA" buttons {"OK"} default button "OK" with title "$MSG_TITULO_FALHA" with icon caution
        end tell
EOD
    else
        osascript -e "display dialog \\"$MSG_FALHA\\" buttons {\\"OK\\"} default button \\"OK\\" with title \\"$MSG_TITULO_FALHA\\" with icon caution"
    fi
fi

echo "Instalação concluída! Obrigado por usar o Power Paste."
exit 0 
"""
    
    # Salva o script
    installer_path = os.path.join(dmg_dir, "install.command")
    with open(installer_path, "w") as f:
        f.write(installer_script)

def create_readme(dmg_dir):
    """Cria o arquivo README.txt"""
    print("Criando README.txt...")
    
    readme_content = f"""=== Power Paste {VERSION} ===

INSTALAÇÃO SIMPLES EM 3 PASSOS
1. Clique duas vezes no arquivo "install.command"
2. Escolha seu idioma preferido (🇧🇷 Português BR, 🇵🇹 Português PT ou 🇺🇸 English)
3. Aguarde a instalação automática
4. Pronto! O Power Paste já está ativo na barra de menus

TRÊS IDIOMAS DISPONÍVEIS
- 🇧🇷 Português do Brasil - Para usuários brasileiros
- 🇵🇹 Português de Portugal - Para usuários portugueses 
- 🇺🇸 Inglês (English) - Para usuários internacionais

O QUE O INSTALADOR FAZ AUTOMATICAMENTE:
- Permite escolher seu idioma preferido
- Instala o app na pasta Applications do seu usuário
- Remove versões antigas que possam estar causando conflitos
- Inicia o Power Paste automaticamente
- Configura para iniciar quando você ligar o computador
- NÃO precisa de senha de administrador

APÓS A INSTALAÇÃO:
- O ícone do Power Paste aparecerá na barra de menus (canto superior direito)
- Se não estiver vendo o ícone, verifique se ele não está oculto
- O instalador tentará mostrar o ícone automaticamente

NOVIDADES DA VERSÃO {VERSION}
- Nova tela de configurações personalizáveis
- Opção para alterar o idioma diretamente pelo aplicativo
- Possibilidade de configurar o número de itens no histórico
- Controle da inicialização automática
- Melhorias de interface e estabilidade
- Correções de bugs

USO
- O Power Paste monitora automaticamente sua área de transferência
- Acesse o histórico de cópias clicando no ícone na barra de menus
- Use Ctrl+Cmd+V para abrir o menu rapidamente
- Clique em um item de texto para visualizá-lo antes de colar
- Clique em uma imagem para abri-la no Preview
- Acesse as configurações pelo menu para personalizar o aplicativo

SOBRE
Desenvolvido por Caio Castro (linkedin.com/in/caiorcastro)
Site do projeto: github.com/caiorcastro/Power-Paste
"""
    
    # Salva o README
    readme_path = os.path.join(dmg_dir, "README.txt")
    with open(readme_path, "w") as f:
        f.write(readme_content)

def create_dmg(dmg_dir):
    """Cria o arquivo DMG"""
    print(f"Criando arquivo DMG '{DMG_NAME}'...")
    
    # Verifica se o utilitário create-dmg está instalado
    try:
        subprocess.run(["which", "create-dmg"], capture_output=True, check=True)
    except:
        print("AVISO: 'create-dmg' não encontrado. Usando comando hdiutil diretamente.")
        return create_dmg_hdiutil(dmg_dir)
    
    # Usando create-dmg (se disponível)
    dmg_cmd = [
        "create-dmg",
        "--volname", f"{APP_NAME}",
        "--volicon", "icon.png",
        "--window-pos", "200", "120",
        "--window-size", "800", "400",
        "--icon-size", "100",
        "--icon", f"{APP_NAME}.app", "200", "120",
        "--icon", "install.command", "400", "120",
        "--icon", "README.txt", "600", "120",
        "--hide-extension", "install.command",
        "--hide-extension", "README.txt",
        "--app-drop-link", "600", "300",
        "--no-internet-enable",
        DMG_NAME,
        dmg_dir
    ]
    
    if not run_command(dmg_cmd):
        print("Erro ao criar DMG com create-dmg. Tentando método alternativo...")
        return create_dmg_hdiutil(dmg_dir)
    
    return True

def create_dmg_hdiutil(dmg_dir):
    """Cria DMG usando hdiutil (método alternativo)"""
    print("Criando DMG com hdiutil...")
    
    # Cria o DMG temporário
    temp_dmg = "temp.dmg"
    if not run_command([
        "hdiutil", "create",
        "-srcfolder", dmg_dir,
        "-volname", APP_NAME,
        "-format", "UDRW",
        "-size", "200m",
        temp_dmg
    ]):
        return False
    
    # Converte para o formato final
    if not run_command([
        "hdiutil", "convert",
        temp_dmg,
        "-format", "UDZO",
        "-o", DMG_NAME
    ]):
        return False
    
    # Remove o DMG temporário
    os.remove(temp_dmg)
    
    return True

def main():
    """Função principal"""
    print(f"=== Criando {APP_NAME} DMG versão {VERSION} ===")
    
    cleanup()
    
    if not build_app():
        sys.exit(1)
    
    dmg_dir = prepare_dmg_structure()
    
    if not create_dmg(dmg_dir):
        print("Erro ao criar o arquivo DMG!")
        sys.exit(1)
    
    print(f"\nDMG criado com sucesso: {DMG_NAME}")
    print("Apenas UM instalador está incluído!")

if __name__ == "__main__":
    main() 