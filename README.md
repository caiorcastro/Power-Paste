# Power Paste

Um gerenciador de área de transferência para macOS que permite salvar e reutilizar textos copiados, com suporte a formatação rica (RTF).

## Funcionalidades

- Salva automaticamente textos copiados
- Suporta formatação rica (RTF)
- Interface minimalista na barra de menus
- Inicia automaticamente com o sistema
- Atalhos de teclado para acesso rápido
- Suporte a múltiplos itens na área de transferência

## Requisitos

- macOS 10.15 ou superior
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/power-paste.git
cd power-paste
```

2. Crie e ative um ambiente virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Instale o aplicativo:
```bash
python3 setup.py py2app
```

5. Copie o aplicativo para a pasta de aplicativos:
```bash
mkdir -p ~/Applications/PowerPaste
cp -r dist/Power\ Paste.app ~/Applications/PowerPaste/
```

6. Configure o início automático:
```bash
mkdir -p ~/Library/LaunchAgents
printf '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n    <key>Label</key>\n    <string>com.caiorcastro.powerpaste</string>\n    <key>ProgramArguments</key>\n    <array>\n        <string>open</string>\n        <string>%s/Applications/PowerPaste/Power Paste.app</string>\n    </array>\n    <key>RunAtLoad</key>\n    <true/>\n    <key>ProcessType</key>\n    <string>Interactive</string>\n</dict>\n</plist>' "$HOME" > ~/Library/LaunchAgents/com.caiorcastro.powerpaste.plist
launchctl load ~/Library/LaunchAgents/com.caiorcastro.powerpaste.plist
```

## Uso

1. O Power Paste aparecerá como um ícone na barra de menus do macOS
2. Clique no ícone para ver os textos salvos
3. Clique em um texto salvo para copiá-lo novamente
4. Use o menu para limpar a lista ou sair do aplicativo

## Desinstalação

1. Pare o aplicativo:
```bash
launchctl unload ~/Library/LaunchAgents/com.caiorcastro.powerpaste.plist
```

2. Remova os arquivos:
```bash
rm -rf ~/Applications/PowerPaste
rm ~/Library/LaunchAgents/com.caiorcastro.powerpaste.plist
```

## Desenvolvimento

Para desenvolver ou modificar o aplicativo:

1. Clone o repositório
2. Crie e ative o ambiente virtual
3. Instale as dependências de desenvolvimento:
```bash
pip install -r requirements-dev.txt
```

4. Execute o aplicativo em modo de desenvolvimento:
```bash
python3 power_paste.py
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request 