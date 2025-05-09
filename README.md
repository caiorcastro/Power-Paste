# Power Paste

<p align="center">
  <img src="icon.png" alt="Power Paste Logo" width="128" height="128">
</p>

## 📋 Gerenciador de Área de Transferência para macOS

Power Paste é um utilitário leve e eficiente que monitora e gerencia seu histórico de área de transferência no macOS, permitindo acesso rápido aos itens copiados anteriormente, tanto textos quanto imagens.

### ✨ Características

- **Monitoramento contínuo** da área de transferência
- **Suporte para texto e imagens**
- **Interface integrada** na barra de menus do macOS
- **Visualização rápida** do histórico de cópias
- **Seleção parcial** de texto através do TextEdit
- **Persistência** do histórico entre reinicializações
- **Múltiplos métodos de acesso** à área de transferência para máxima compatibilidade

### 🔧 Requisitos

- macOS 10.14 ou superior
- Python 3.7+
- Dependências listadas em `requirements.txt`

### 📦 Instalação

1. Clone este repositório:
```
git clone https://github.com/caiorcastro/Power-Paste.git
cd Power-Paste
```

2. Crie e ative um ambiente virtual Python:
```
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Execute o aplicativo:
```
python power_paste.py
```

### 💡 Uso

1. Após iniciar o aplicativo, você verá um ícone de prancheta (📋) na barra de menus
2. Copie qualquer texto ou imagem normalmente (Cmd+C)
3. Clique no ícone da barra de menus para ver o histórico de itens copiados
4. Selecione um item para:
   - **Texto**: Abrirá no TextEdit para seleção parcial
   - **Imagens**: Serão copiadas diretamente para a área de transferência

### 🔄 Funcionalidades detalhadas

#### Gerenciamento de texto
- Ao clicar em um item de texto, abre-se o TextEdit com o conteúdo completo
- Você pode selecionar apenas partes específicas do texto
- O texto selecionado pode ser copiado com Cmd+C

#### Gerenciamento de imagens
- As imagens são automaticamente convertidas para PNG
- Ao selecionar uma imagem do histórico, ela é copiada para a área de transferência
- Suporte para vários formatos de imagem

#### Opções adicionais
- **Limpar Histórico**: Remove todos os itens do histórico
- **Sobre Power Paste**: Exibe informações sobre o aplicativo

### 🛠️ Tecnologias utilizadas

- **Python**: Linguagem principal
- **rumps**: Interface da barra de menus do macOS
- **pyperclip**: Acesso básico à área de transferência
- **pyobjc**: APIs nativas do macOS
- **Pillow**: Manipulação de imagens

### 📝 Notas

- O histórico é armazenado em `~/.power_paste_history.json`
- As imagens são armazenadas temporariamente em `~/.power_paste_temp_images/`
- O histórico é mantido por 7 dias por padrão

### 🧰 Solução de problemas

Se encontrar problemas ao colar itens em determinados aplicativos, o Power Paste implementa múltiplos métodos de acesso à área de transferência como fallback:

1. APIs nativas NSPasteboard (AppKit)
2. Utilitários de linha de comando (pbcopy/pbpaste)
3. AppleScript

### 📜 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

---

Desenvolvido com ❤️ para simplificar o fluxo de trabalho no macOS. 