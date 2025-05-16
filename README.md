# Power Paste

<p align="center">
  <img src="./icon.png" alt="Power Paste Logo" width="128" height="128">
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
  <img src="https://img.shields.io/badge/Version-1.3-orange?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Languages-PT--Normal%20|%20PT--Arcaico-yellow?style=flat-square" alt="Languages">
</p>

## 📋 Sobre o Projeto

**Power Paste** é um gerenciador de área de transferência leve e elegante para macOS que armazena automaticamente seu histórico de cópias, incluindo textos e imagens. Tudo isso com uma interface minimalista que se integra perfeitamente à barra de menus do seu Mac.

## ✨ Recursos

- 📋 Histórico de cópias de texto e imagens (até 25 itens configuráveis)
- 🔄 Interface simples e discreta na barra de menus
- 🖼️ Visualização de imagens diretamente no Preview
- 🚀 Atalho de teclado para acesso rápido (Ctrl+Cmd+V)
- 🔍 Visualização e edição de texto antes de colar
- 🌙 Integração nativa com macOS
- 🔐 Armazenamento local (privacidade garantida - seus dados nunca saem do seu Mac)
- 🌐 Suporte a dois idiomas: Português Normal (Brasil) (🇧🇷) e Português Arcaico (Guiana Brasileira/Portugal) (🇵🇹)
- ⚙️ Menu de configurações completo para personalizar o aplicativo
- 🚀 Leve e eficiente - consome poucos recursos do sistema

## 🚀 Instalação

### Usando o Script Fornecido (Recomendado)

O método mais simples é usar o script `rebuild_app.sh` incluído:

```bash
# Torne o script executável (apenas uma vez)
chmod +x rebuild_app.sh

# Com ambiente virtual (recomendado para desenvolvedores)
./rebuild_app.sh --venv

# Sem ambiente virtual (instalação rápida)
./rebuild_app.sh
```

Este script irá:
1. Opcionalmente criar um ambiente virtual Python (com a flag --venv)
2. Limpar construções anteriores
3. Converter o ícone para o formato ICNS (melhor qualidade na barra de menus)
4. Construir o aplicativo usando py2app
5. Instalar na pasta Applications do seu usuário
6. Configurar a inicialização automática

### Instalação Manual

Se preferir fazer manualmente:

1. (Opcional) Crie um ambiente virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
pip install py2app
```

3. Construa o aplicativo:
```bash
python3 setup.py py2app
```

4. Copie o aplicativo para a pasta Applications:
```bash
cp -R dist/Power\ Paste.app ~/Applications/
```

## 🖱️ Como Usar

1. Após a instalação, o Power Paste aparecerá como um ícone na barra de menus do macOS
2. O aplicativo captura automaticamente tudo que você copia (texto e imagens)
3. Para acessar seu histórico, clique no ícone na barra de menus
4. Para textos:
   - Clique em um item para ver uma prévia e copiá-lo
   - O texto será copiado para a área de transferência, pronto para colar em qualquer aplicativo
5. Para imagens:
   - Clique em um item de imagem para abri-lo no Preview

### Atalho de Teclado
- `Ctrl+Cmd+V`: Acessa rapidamente o menu do Power Paste de qualquer aplicativo

## ⚙️ Configurações

O Power Paste oferece um menu completo de configurações com as seguintes opções:

- 🌐 **Idioma**: Escolha entre Português Normal (Brasil), Português Arcaico (Guiana Brasileira/Portugal)
- 🔄 **Inicialização com o Sistema**: Configure se o aplicativo deve iniciar automaticamente com o macOS
- 📊 **Número Máximo de Itens**: Defina quantos itens deseja manter no histórico (10, 25, 50 ou 100)

Para acessar as configurações:
1. Clique no ícone do Power Paste na barra de menus
2. Selecione "Configurações" no menu

As alterações nas configurações são aplicadas imediatamente. Se você mudar o idioma, o aplicativo oferecerá a opção de reiniciar para aplicar a mudança.

O Power Paste armazena suas configurações em arquivos locais:

- Histórico: `~/.power_paste_history.json`
- Configurações: `~/.power_paste/config.json`
- Idioma: `~/.power_paste/language`

## 🧹 Limpeza e Desinstalação

Para desinstalar o Power Paste completamente:

```bash
# Encerre o aplicativo
killall "Power Paste"

# Remova o aplicativo
rm -rf ~/Applications/Power\ Paste.app

# Remova os arquivos de dados (opcional)
rm -f ~/.power_paste_history.json
rm -rf ~/.power_paste
```

## 👨‍💻 Desenvolvimento

Para desenvolver ou modificar o Power Paste:

1. Clone o repositório ou faça um fork
2. Crie um ambiente virtual (recomendado):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o aplicativo em modo de desenvolvimento:
```bash
python3 power_paste.py
```

5. Para construir o aplicativo após suas modificações:
```bash
# Usando ambiente virtual
./rebuild_app.sh --venv

# Sem ambiente virtual
./rebuild_app.sh
```

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

## 📞 Contato

Caio Castro - [LinkedIn](https://www.linkedin.com/in/caiorcastro/)

---

<p align="center">
  <i>Um aplicativo elegante para gerenciar seu histórico de área de transferência.</i><br>
  Desenvolvido por <a href="https://www.linkedin.com/in/caiorcastro/">Caio Castro</a><br>
  <small>Maio de 2025</small>
</p> 