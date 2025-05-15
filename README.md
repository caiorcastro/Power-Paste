# Power Paste

<p align="center">
  <img src="icon.png" alt="Power Paste Logo" width="128" height="128">
</p>

<p align="center">
  <b>Gerenciador de Área de Transferência para macOS</b>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/caiorcastro/">
    <img src="https://img.shields.io/badge/LinkedIn-Caio%20Castro-blue?style=flat-square&logo=linkedin" alt="LinkedIn">
  </a>
  <img src="https://img.shields.io/badge/macOS-10.15+-blue?style=flat-square&logo=apple" alt="macOS">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-1.2-orange?style=flat-square" alt="Version">
</p>

## Sobre o Projeto

Power Paste é um gerenciador de área de transferência para macOS que armazena automaticamente seu histórico de cópias, incluindo textos e imagens.

## Recursos

- 📋 Histórico de cópias de texto e imagens
- 🔄 Interface simples na barra de menus
- 🖼️ Visualização de imagens diretamente no Preview
- 🚀 Atalho de teclado para acesso rápido (Ctrl+Cmd+V)
- 🔍 Visualização e edição de texto antes de colar
- 🌙 Integração nativa com macOS
- 🔐 Armazenamento local de dados (não envia dados para a nuvem)

## Instalação

### Instalador Simples (Recomendado)

1. Baixe o arquivo [Power Paste.dmg](https://github.com/caiorcastro/Power-Paste/releases/latest/download/Power.Paste.dmg)
2. Monte a imagem DMG clicando duas vezes no arquivo baixado
3. Clique duas vezes no arquivo "install.command"
4. Pronto! A instalação é totalmente automática

O instalador faz tudo para você:
- Instala o app na pasta Applications do seu usuário 
- Remove versões antigas que possam estar causando conflitos
- Inicia o Power Paste automaticamente
- Configura para iniciar com o sistema
- Não precisa de senha de administrador

Após a instalação, o ícone do Power Paste aparecerá na barra de menus (canto superior direito).

### Instalação Manual

Se preferir, você pode simplesmente:
1. Baixar o arquivo DMG
2. Montar a imagem DMG clicando duas vezes no arquivo baixado
3. Arrastar o ícone do Power Paste para a pasta Applications do seu usuário

## Como Usar

1. Após copiar qualquer texto ou imagem, o Power Paste o salva automaticamente
2. Clique no ícone do Power Paste na barra de menus para ver o histórico
3. Selecione qualquer item para:
   - Textos: Visualizar/editar e depois copiar
   - Imagens: Abrir diretamente no Preview

## Atalhos de Teclado
- `Ctrl+Cmd+V`: Abre o menu do Power Paste

## Como Contribuir

Contribuições são bem-vindas! Sinta-se à vontade para enviar um Pull Request.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

## Contato

Caio Castro - [LinkedIn](https://www.linkedin.com/in/caiorcastro/)

## ✨ Funcionalidades

- 📋 Salva automaticamente as últimas 25 cópias
- 🖼️ Suporte para imagens com visualização no Preview
- 🎨 Suporta formatação rica (RTF)
- 🖥️ Interface minimalista na barra de menus
- 🔄 Inicia automaticamente com o sistema
- ⌨️ Atalho de teclado (Ctrl+Cmd+V) para acesso rápido
- 📝 Suporte a múltiplos itens na área de transferência

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/caiorcastro/Power-Paste.git
cd Power-Paste
```

2. Crie e ative o ambiente virtual:
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

## 💡 Uso

1. O Power Paste aparecerá como um ícone na barra de menus do macOS
2. Clique no ícone ou use o atalho Ctrl+Cmd+V para ver os itens salvos
3. Clique em um texto para copiá-lo ou editá-lo
4. Clique em uma imagem para abri-la no Preview
5. Use o menu para limpar a lista ou sair do aplicativo

## 🗑️ Desinstalação

1. Pare o aplicativo:
```bash
launchctl unload ~/Library/LaunchAgents/com.caiorcastro.powerpaste.plist
```

2. Remova os arquivos:
```bash
rm -rf ~/Applications/PowerPaste
rm ~/Library/LaunchAgents/com.caiorcastro.powerpaste.plist
```

## 👨‍💻 Desenvolvimento

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

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

<p align="center">
  Desenvolvido por <a href="https://www.linkedin.com/in/caiorcastro/">Caio Castro</a>
</p> 