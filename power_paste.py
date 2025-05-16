import rumps
import pyperclip
import subprocess
import json
import os
import hashlib
from datetime import datetime, timedelta
from PIL import Image
import io
import base64
import tempfile
# Importações para APIs nativas do macOS
from Foundation import NSString, NSUTF8StringEncoding
from AppKit import NSPasteboard, NSPasteboardTypeString, NSImage, NSData, NSPasteboardTypePNG, NSPasteboardTypeTIFF
import threading

# Configurações
HISTORY_FILE = os.path.expanduser("~/.power_paste_history.json")
TEMP_IMAGE_DIR = os.path.expanduser("~/.power_paste_temp_images")
LANGUAGE_FILE = os.path.expanduser("~/.power_paste/language")
CONFIG_FILE = os.path.expanduser("~/.power_paste/config.json")
MAX_ITEMS_TO_SHOW = 25  # Limita o número de itens no menu
LAST_ITEM_HASH = None  # Rastreia o último item processado
DEFAULT_CONFIG = {
    "max_items": 25,
    "start_at_login": True,
    "language": "pt_BR"
}

# Dicionário de traduções
TRANSLATIONS = {
    "pt_BR": {
        "clipboard_empty": "Histórico vazio",
        "clear_history": "Limpar Histórico",
        "about": "Sobre Power Paste",
        "quit": "Sair",
        "confirm_clear": "Deseja realmente limpar todo o histórico?",
        "confirm_yes": "Sim",
        "confirm_no": "Não",
        "history_cleared": "Histórico limpo",
        "notice": "Aviso",
        "error": "Erro",
        "copy_success": "Texto copiado para a área de transferência",
        "copy_error": "Erro ao copiar texto",
        "image_open_error": "Erro ao abrir imagem",
        "image_not_found": "Arquivo de imagem não encontrado",
        "image_opened": "Imagem aberta no Preview",
        "copy": "Copiar",
        "cancel": "Cancelar",
        "text_preview": "Visualização de Texto",
        "developed_by": "Desenvolvido por Caio Castro",
        "version": "Versão 1.3",
        "linkedIn": "LinkedIn: linkedin.com/in/caiorcastro",
        "github": "GitHub: github.com/caiorcastro/Power-Paste",
        "language": "Idioma: Português do Brasil",
        "settings": "Configurações",
        "max_items_label": "Número máximo de itens no histórico:",
        "start_at_login_label": "Iniciar com o sistema:",
        "language_label": "Idioma:",
        "save_button": "Salvar",
        "settings_saved": "Configurações salvas com sucesso!",
        "restart_required": "Algumas mudanças podem exigir reiniciar o aplicativo.",
        "settings_title": "Configurações do Power Paste",
        "settings_message": "Configure as opções do Power Paste",
        "language_pt_BR": "🇧🇷 Português do Brasil",
        "language_pt_PT": "🇵🇹 Português de Portugal",
        "language_en_US": "🇺🇸 Inglês (English)",
        "start_at_login_select": "Iniciar o Power Paste automaticamente?",
        "max_items_select": "Escolha quantos itens manter no histórico:",
        "yes": "Sim",
        "no": "Não"
    },
    "pt_PT": {
        "clipboard_empty": "Histórico vazio",
        "clear_history": "Limpar Histórico",
        "about": "Sobre Power Paste",
        "quit": "Sair",
        "confirm_clear": "Deseja realmente limpar todo o histórico?",
        "confirm_yes": "Sim",
        "confirm_no": "Não",
        "history_cleared": "Histórico limpo",
        "notice": "Aviso",
        "error": "Erro",
        "copy_success": "Texto copiado para a área de transferência",
        "copy_error": "Erro ao copiar texto",
        "image_open_error": "Erro ao abrir imagem",
        "image_not_found": "Ficheiro de imagem não encontrado",
        "image_opened": "Imagem aberta no Preview",
        "copy": "Copiar",
        "cancel": "Cancelar",
        "text_preview": "Visualização de Texto",
        "developed_by": "Desenvolvido por Caio Castro",
        "version": "Versão 1.3",
        "linkedIn": "LinkedIn: linkedin.com/in/caiorcastro",
        "github": "GitHub: github.com/caiorcastro/Power-Paste",
        "language": "Idioma: Português de Portugal",
        "settings": "Configurações",
        "max_items_label": "Número máximo de itens no histórico:",
        "start_at_login_label": "Iniciar com o sistema:",
        "language_label": "Idioma:",
        "save_button": "Guardar",
        "settings_saved": "Configurações guardadas com sucesso!",
        "restart_required": "Algumas alterações podem requerer reiniciar a aplicação.",
        "settings_title": "Configurações do Power Paste",
        "settings_message": "Configure as opções do Power Paste",
        "language_pt_BR": "🇧🇷 Português do Brasil",
        "language_pt_PT": "🇵🇹 Português de Portugal",
        "language_en_US": "🇺🇸 Inglês (English)",
        "start_at_login_select": "Iniciar o Power Paste automaticamente?",
        "max_items_select": "Escolha quantos itens manter no histórico:",
        "yes": "Sim",
        "no": "Não"
    },
    "en_US": {
        "clipboard_empty": "Empty history",
        "clear_history": "Clear History",
        "about": "About Power Paste",
        "quit": "Quit",
        "confirm_clear": "Do you really want to clear the entire history?",
        "confirm_yes": "Yes",
        "confirm_no": "No",
        "history_cleared": "History cleared",
        "notice": "Notice",
        "error": "Error",
        "copy_success": "Text copied to clipboard",
        "copy_error": "Error copying text",
        "image_open_error": "Error opening image",
        "image_not_found": "Image file not found",
        "image_opened": "Image opened in Preview",
        "copy": "Copy",
        "cancel": "Cancel",
        "text_preview": "Text Preview",
        "developed_by": "Developed by Caio Castro",
        "version": "Version 1.3",
        "linkedIn": "LinkedIn: linkedin.com/in/caiorcastro",
        "github": "GitHub: github.com/caiorcastro/Power-Paste",
        "language": "Language: English",
        "settings": "Settings",
        "max_items_label": "Maximum items in history:",
        "start_at_login_label": "Start at login:",
        "language_label": "Language:",
        "save_button": "Save",
        "settings_saved": "Settings saved successfully!",
        "restart_required": "Some changes may require restarting the app.",
        "settings_title": "Power Paste Settings",
        "settings_message": "Configure Power Paste options",
        "language_pt_BR": "🇧🇷 Brazilian Portuguese",
        "language_pt_PT": "🇵🇹 Portuguese",
        "language_en_US": "🇺🇸 English",
        "start_at_login_select": "Start Power Paste automatically?",
        "max_items_select": "Choose how many items to keep in history:",
        "yes": "Yes",
        "no": "No"
    }
}

# Idioma padrão
CURRENT_LANGUAGE = "pt_BR"

# Lê o idioma definido pelo usuário
def load_language():
    global CURRENT_LANGUAGE
    if os.path.exists(LANGUAGE_FILE):
        try:
            with open(LANGUAGE_FILE, 'r') as f:
                lang = f.read().strip()
                if lang in TRANSLATIONS:
                    CURRENT_LANGUAGE = lang
                    return lang
        except Exception as e:
            print(f"Erro ao carregar arquivo de idioma: {e}")
    return CURRENT_LANGUAGE

# Carrega configurações
def load_config():
    global MAX_ITEMS_TO_SHOW
    
    # Certifique-se que o diretório existe
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    # Tenta carregar o arquivo de configuração existente
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Atualiza configurações globais
                if 'max_items' in config:
                    MAX_ITEMS_TO_SHOW = config['max_items']
                if 'language' in config:
                    # Salva no arquivo de idioma para compatibilidade com versões antigas
                    with open(LANGUAGE_FILE, 'w') as lang_file:
                        lang_file.write(config['language'])
                return config
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    # Se não conseguir carregar, cria um arquivo de configuração padrão
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

# Salva configurações
def save_config(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

# Obtém uma string traduzida
def _(key):
    lang = CURRENT_LANGUAGE
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    # Fallback para inglês
    if key in TRANSLATIONS["en_US"]:
        return TRANSLATIONS["en_US"][key]
    # Se não encontrar, retorna a própria chave
    return key

# Função para definir o início automático
def set_start_at_login(enable=True):
    try:
        app_path = "/Applications/Power Paste.app"
        if not os.path.exists(app_path):
            app_path = os.path.expanduser("~/Applications/Power Paste.app")
            if not os.path.exists(app_path):
                return False
        
        if enable:
            script = f'''
            tell application "System Events"
                make login item at end with properties {{path:"{app_path}", hidden:false}}
            end tell
            '''
        else:
            script = '''
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
            '''
        
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except Exception as e:
        print(f"Erro ao configurar inicialização automática: {e}")
        return False

# Carrega o idioma na inicialização
load_language()

# Carrega configurações
config = load_config()

# Funções de manipulação da área de transferência usando APIs nativas
def copy_text_to_clipboard_native(text):
    """
    Coloca texto na área de transferência usando APIs nativas do macOS.
    Muito mais confiável que métodos Python padrão.
    """
    success = False
    
    # Método 1: Via APIs nativas AppKit (mais confiável)
    try:
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        ns_string = NSString.stringWithString_(text)
        success = pb.setString_forType_(ns_string, NSPasteboardTypeString)
    except Exception as e:
        print(f"Erro ao copiar texto (API nativa): {e}")
    
    # Método 2: Via pbcopy (backup)
    if not success:
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            success = True
        except Exception as e:
            print(f"Erro ao copiar texto (pbcopy): {e}")
    
    # Método 3: Via AppleScript (último recurso)
    if not success:
        try:
            escaped_text = text.replace('"', '\\"').replace("'", "\\'")
            script = f'set the clipboard to "{escaped_text}"'
            subprocess.run(['osascript', '-e', script], check=True)
            success = True
        except Exception as e:
            print(f"Erro ao copiar texto (AppleScript): {e}")
    
    return success

def copy_image_to_clipboard_native(image_path):
    """
    Coloca imagem na área de transferência usando APIs nativas do macOS.
    """
    if not os.path.exists(image_path):
        return False
    
    abs_path = os.path.abspath(image_path)
    success = False
    
    # Método 1: Via AppleScript para PNG
    try:
        script = f'''
        set theImage to (POSIX file "{abs_path}")
        set the clipboard to (read theImage as «class PNGf»)
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True)
        if result.returncode == 0:
            success = True
        
    except Exception:
        pass
    
    # Método 2: Via AppleScript para TIFF
    if not success:
        try:
            script = f'''
            set theImage to (POSIX file "{abs_path}")
            set the clipboard to (read theImage as «class TIFF»)
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True)
            if result.returncode == 0:
                success = True
            
        except Exception:
            pass
    
    # Método 3: Via AppKit nativo
    if not success:
        try:
            image = NSImage.alloc().initWithContentsOfFile_(abs_path)
            if image:
                pb = NSPasteboard.generalPasteboard()
                pb.clearContents()
                types = [NSPasteboardTypePNG]
                pb.declareTypes_owner_(types, None)
                success = image.writeToPasteboard_(pb)
        except Exception:
            pass
    
    # Método 4: Via dados binários como último recurso
    if not success:
        try:
            with open(abs_path, 'rb') as f:
                img_data = f.read()
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(img_data)
            success = True
        except Exception:
            pass
    
    return success

def copy_selected_text_to_clipboard(text):
    """
    Copia apenas o texto selecionado para a área de transferência
    """
    if text:
        return copy_text_to_clipboard_native(text)
    return False

class PowerPasteApp(rumps.App):
    def __init__(self):
        # Inicializa atributos essenciais logo no início
        self.history = []  # Inicializa o histórico como lista vazia
        
        try:
            # Carrega o idioma antes de inicializar o app
            load_language()
            
            # Carrega as configurações
            self.config = load_config()
            
            # Configura inicialização automática se necessário
            if self.config.get('start_at_login', True):
                set_start_at_login(True)
            
            # Verifica qual arquivo de ícone usar (preferindo o .icns se disponível)
            icon_file = "icon.icns" if os.path.exists("icon.icns") else "icon.png"
            
            super(PowerPasteApp, self).__init__(
                name="Power Paste",
                icon=icon_file,
                quit_button=None,  # Vamos criar nosso próprio botão de sair
                template=False     # Ícone em preto e branco para se encaixar na barra de menus
            )
            
            # Configura atalho de teclado global
            self.hotkey = "control+command+v"
            
            # Garante que o diretório temporário exista
            self.ensure_temp_dir()
            
            # Carrega o histórico
            historical_data = self.load_history() 
            if historical_data:
                self.history = historical_data
            
            # Constrói o menu inicial
            self.build_menu()
            
            # Configura o timer para verificar a área de transferência
            self.timer = rumps.Timer(self.check_clipboard, 1)
            self.timer.start()
            
        except Exception as e:
            print(f"Erro na inicialização: {e}")
            # Se ocorrer erro, mostra uma notificação
            import traceback
            traceback.print_exc()
    
    def build_menu(self):
        # Limpa o menu atual
        if hasattr(self, 'menu'):
            self.menu.clear()
        else:
            # Certifica que o menu existe
            self.menu = []
        
        # Adiciona os itens do histórico
        self.build_history_menu()
        
        # Adiciona os itens do menu básico (com separador)
        self.menu.add(rumps.separator)  # Usa separador nativo do rumps
        
        clear_history = rumps.MenuItem(title=_("clear_history"))
        about_item = rumps.MenuItem(title=_("about"))
        quit_item = rumps.MenuItem(title=_("quit"))
        
        # Conecta os callbacks
        clear_history.set_callback(self.clear_history)
        about_item.set_callback(self.show_about)
        quit_item.set_callback(self.quit_app)
        
        # Adiciona items ao menu
        self.menu.add(clear_history)
        self.menu.add(about_item)
        self.menu.add(quit_item)
    
    def quit_app(self, _):
        # Limpa a pasta temporária
        try:
            if os.path.exists(TEMP_IMAGE_DIR):
                for f in os.listdir(TEMP_IMAGE_DIR):
                    try:
                        os.remove(os.path.join(TEMP_IMAGE_DIR, f))
                    except:
                        pass
        except:
            pass
        
        rumps.quit_application()
    
    def ensure_temp_dir(self):
        """Garante que o diretório temporário para imagens existe."""
        if not os.path.exists(TEMP_IMAGE_DIR):
            os.makedirs(TEMP_IMAGE_DIR)

    def load_history(self):
        """Carrega o histórico do arquivo."""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
                    # Ordena por timestamp (mais recente primeiro)
                    return sorted(
                        history, 
                        key=lambda x: datetime.strptime(x.get("timestamp", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"), 
                        reverse=True
                    )
        except (json.JSONDecodeError, ValueError, KeyError, Exception) as e:
            print(f"Erro ao carregar histórico: {e}")
            # Em caso de erro, retorna lista vazia
            return []
        # Se não existir arquivo ou qualquer outro caso, retorna lista vazia
        return []

    def save_history(self):
        """Salva o histórico no arquivo."""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    def clean_history(self, _=None):
        """Limpa todo o histórico."""
        if not self.history:
            return
            
        # Remove itens duplicados baseados no hash
        seen_hashes = set()
        unique_items = []
        
        for item in self.history:
            item_hash = item.get("hash")
            if not item_hash or item_hash in seen_hashes:
                continue
                
            # Verifica se é uma imagem e se o arquivo existe
            if item.get("type") == "image":
                img_path = item.get("content", "")
                if img_path and not os.path.exists(img_path):
                    continue
            
            seen_hashes.add(item_hash)
            unique_items.append(item)
        
        # Atualiza o histórico
        self.history = unique_items
        self.save_history()

    def rebuild_menu(self):
        """Reconstrói o menu completo da aplicação."""
        # Limpa o menu atual
        self.menu.clear()
        
        # Adiciona itens do histórico
        self.build_history_menu()
        
        # Adiciona separador e opções de gerenciamento
        self.menu.add(rumps.separator)  # Usa separador nativo do rumps
        
        clear_history = rumps.MenuItem(title=_("clear_history"))
        about_item = rumps.MenuItem(title=_("about"))
        quit_item = rumps.MenuItem(title=_("quit"))
        
        # Conecta os callbacks
        clear_history.set_callback(self.clear_history)
        about_item.set_callback(self.show_about)
        quit_item.set_callback(self.quit_app)
        
        # Adiciona items ao menu
        self.menu.add(clear_history)
        self.menu.add(about_item)
        self.menu.add(quit_item)

    def build_history_menu(self):
        """Constrói a parte do menu com os itens do histórico."""
        # Verifica se há itens no histórico
        if not hasattr(self, 'history') or not self.history:
            empty_item = rumps.MenuItem(_("clipboard_empty"))
            empty_item.set_callback(None)  # Torna não clicável
            self.menu.add(empty_item)
        else:
            # Limita para os N itens mais recentes e garante que estão ordenados por data
            items_to_show = sorted(
                self.history[:MAX_ITEMS_TO_SHOW],
                key=lambda x: datetime.strptime(x.get("timestamp", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"),
                reverse=True  # Ordem decrescente (mais recentes primeiro)
            )
            
            # Adiciona os itens ao menu
            for idx, item in enumerate(items_to_show):
                # Obtém o timestamp formatado
                try:
                    item_timestamp = datetime.strptime(
                        item.get("timestamp", "2000-01-01 00:00:00"), 
                        "%Y-%m-%d %H:%M:%S"
                    )
                    display_time = item_timestamp.strftime("%H:%M")
                except (ValueError, KeyError):
                    display_time = "--:--"
                
                # Formata o item com base no tipo
                if item.get("type") == "text":
                    text_content = item.get("content", "")
                    # Limpa o texto para o menu
                    preview = text_content.replace('\n', ' ').replace('\r', ' ')
                    preview = ' '.join(preview.split())
                    
                    if len(preview) > 40:
                        preview = preview[:40] + "..."
                    
                    title = f"{display_time} | {preview}"
                    
                    # Cria o item de menu para texto
                    menu_item = rumps.MenuItem(title)
                    menu_item._idx = idx  # Associa um índice ao invés do objeto completo
                    menu_item.set_callback(self.paste_text_item)
                    self.menu.add(menu_item)
                    
                elif item.get("type") == "image":
                    # Cria item direto para abrir no Preview
                    title = f"{display_time} | 🖼️ {_('image_preview') if CURRENT_LANGUAGE != 'en_US' else 'Image'}"
                    menu_item = rumps.MenuItem(title)
                    menu_item._idx = idx
                    menu_item.set_callback(self.open_image_in_preview)
                    self.menu.add(menu_item)
                else:
                    # Tipo desconhecido
                    title = f"{display_time} | {_('unknown_item')}"
                    menu_item = rumps.MenuItem(title)
                    self.menu.add(menu_item)

    def paste_text_item(self, sender):
        """Mostra uma janela para visualizar e copiar o texto selecionado."""
        try:
            idx = getattr(sender, '_idx', None)
            if idx is None or idx >= len(self.history):
                return
                
            item = self.history[idx]
            text = item.get("content", "")
            
            if not text:
                return
                
            # Mostra uma janela para permitir visualização e cópia do texto
            self.show_text_selection_window(text)
            
        except Exception as e:
            print(f"Erro ao processar item: {e}")
    
    def open_image_in_preview(self, sender):
        """Abre a imagem diretamente no Preview."""
        try:
            idx = getattr(sender, '_idx', None)
            if idx is None or idx >= len(self.history):
                return
                
            item = self.history[idx]
            content = item.get("content", "")
            
            if not content:
                return
                
            # Verifica se o arquivo existe
            if not os.path.exists(content):
                rumps.notification(
                    "Power Paste", 
                    _("error"), 
                    _("image_not_found")
                )
                return
                
            # Verifica se o Preview está instalado
            if not os.path.exists("/Applications/Preview.app"):
                # Tenta abrir com o visualizador padrão
                subprocess.run(['open', content], check=False)
            else:
                # Usa caminho absoluto para o arquivo
                subprocess.run(['open', '-a', 'Preview', os.path.abspath(content)], check=False)
                
            rumps.notification(
                "Power Paste", 
                _("notice"), 
                _("image_opened")
            )
            
        except Exception as e:
            rumps.notification(
                "Power Paste", 
                _("error"), 
                f"{_('image_open_error')}: {str(e)}"
            )
    
    def show_text_selection_window(self, text):
        """Mostra uma janela para selecionar parte do texto."""
        try:
            # Escapa aspas e caracteres especiais para AppleScript
            escaped_text = text.replace('"', '\\"').replace("\n", "\\n")

            script = f'''
            tell application "System Events"
                set theText to "{escaped_text}"
                display dialog theText buttons {{"Cancelar", "Copiar"}} default button 2 with title "Visualização de Texto"
            end tell
            '''
            
            # Executa o script e verifica o resultado
            subprocess.run(["osascript", "-e", script], check=False)
            
            # Copia o texto para a área de transferência de qualquer forma
            if copy_text_to_clipboard_native(text):
                rumps.notification(
                    "Power Paste", 
                    _("notice"), 
                    _("copy_success")
                )
            
        except Exception as e:
            print(f"Erro ao mostrar janela de seleção: {e}")
            # Tenta copiar diretamente como fallback
            if copy_text_to_clipboard_native(text):
                rumps.notification(
                    "Power Paste", 
                    _("notice"), 
                    _("copy_success")
                )
    
    def clear_history(self, _=None):
        """Limpa todo o histórico."""
        if not self.history:
            return
            
        # Confirmação antes de limpar
        script = f'''
        tell application "System Events"
            display dialog "{_('confirm_clear')}" buttons {{"{_('confirm_no')}", "{_('confirm_yes')}"}} default button 1 with icon caution
            set theButton to button returned of result
            if theButton is "{_('confirm_yes')}" then
                return "yes"
            else
                return "no"
            end if
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, text=True)
        
        if result.stdout.strip() == "yes":
            # Limpa o histórico
            self.history = []
            self.save_history()
            
            # Limpa arquivos temporários de imagens
            for file in os.listdir(TEMP_IMAGE_DIR):
                try:
                    os.remove(os.path.join(TEMP_IMAGE_DIR, file))
                except:
                    pass
            
            self.rebuild_menu()
            
            # Notifica o usuário
            rumps.notification(
                "Power Paste", 
                _("notice"), 
                _("history_cleared")
            )
            
    def show_about(self, _):
        """Mostra uma janela 'Sobre' nativa do macOS"""
        try:
            # Importa os módulos necessários do PyObjC
            from AppKit import NSAlert, NSImage, NSString
            from Foundation import NSMakeRect, NSURL
            
            # Cria um alerta nativo do macOS
            alert = NSAlert.alloc().init()
            alert.setAlertStyle_(0)  # Estilo informativo
            alert.setShowsHelp_(False)
            
            # Define o título e o botão
            alert.setMessageText_("Power Paste")
            alert.setInformativeText_(
                "O gerenciador de área de transferência elegante para macOS\n\n"
                "Copie textos e imagens e acesse-os de forma rápida e intuitiva!\n\n"
                "Versão 1.3 - Maio de 2025\n\n"
                "Desenvolvido por Caio Castro\n"
                "LinkedIn: linkedin.com/in/caiorcastro\n"
                "GitHub: github.com/caiorcastro/Power-Paste"
            )
            
            # Adiciona um botão OK
            alert.addButtonWithTitle_("OK")
            
            # Tenta carregar o ícone se existir
            icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon.png")
            if os.path.exists(icon_path):
                icon_image = NSImage.alloc().initWithContentsOfFile_(icon_path)
                if icon_image:
                    alert.setIcon_(icon_image)
            
            # Exibe o alerta em modo modal (bloqueante)
            alert.runModal()
            
        except Exception as e:
            print(f"Erro ao mostrar janela Sobre: {e}")
            # Fallback para uma abordagem mais simples
            rumps.notification(
                "Power Paste", 
                "Sobre", 
                "Desenvolvido por Caio Castro - Versão 1.3"
            )

    def show_settings(self, _):
        """Mostra a janela de configurações"""
        global MAX_ITEMS_TO_SHOW, CURRENT_LANGUAGE
        
        try:
            # Obtém as configurações atuais
            current_config = self.config.copy() if hasattr(self, 'config') else load_config()
            
            # Configurações atuais
            max_items = current_config.get('max_items', MAX_ITEMS_TO_SHOW)
            start_at_login = current_config.get('start_at_login', True)
            current_language = current_config.get('language', CURRENT_LANGUAGE)
            
            # Mostra configurações mais simples com AppleScript
            script_language = f'''
            tell application "System Events"
                set langOptions to {{"{_('language_pt_BR')}", "{_('language_pt_PT')}", "{_('language_en_US')}"}}
                set langValues to {{"pt_BR", "pt_PT", "en_US"}}
                set currentLangIndex to 1
                
                if "{current_language}" is "pt_BR" then
                    set currentLangIndex to 1
                else if "{current_language}" is "pt_PT" then
                    set currentLangIndex to 2
                else if "{current_language}" is "en_US" then
                    set currentLangIndex to 3
                end if
                
                set theLanguageChoice to choose from list langOptions ¬
                    with title "{_('language_label')}" ¬
                    with prompt "{_('settings_title')}" ¬
                    default items {{item currentLangIndex of langOptions}} ¬
                    OK button name "OK" ¬
                    cancel button name "Cancel"
                
                if theLanguageChoice is false then
                    return "CANCEL"
                else
                    set languageIndex to 1
                    repeat with i from 1 to count of langOptions
                        if item 1 of theLanguageChoice is item i of langOptions then
                            set languageIndex to i
                            exit repeat
                        end if
                    end repeat
                    
                    return item languageIndex of langValues
                end if
            end tell
            '''
            
            # Obtém idioma
            result_language = subprocess.run(['osascript', '-e', script_language], 
                                            capture_output=True, text=True)
            selected_language = result_language.stdout.strip()
            
            if selected_language == "CANCEL":
                return
            
            # Script para inicialização automática
            script_startup = f'''
            tell application "System Events"
                set startupOptions to {{"{_('yes')}", "{_('no')}"}}
                set startupDefault to "{_('yes')}"
                
                if {str(start_at_login).lower()} is "false" then
                    set startupDefault to "{_('no')}"
                end if
                
                set theStartupChoice to choose from list startupOptions ¬
                    with title "{_('start_at_login_label')}" ¬
                    with prompt "{_('start_at_login_select')}" ¬
                    default items {{startupDefault}} ¬
                    OK button name "OK" ¬
                    cancel button name "Cancel"
                
                if theStartupChoice is false then
                    return "CANCEL"
                else
                    set selectedStartup to (item 1 of theStartupChoice is "{_('yes')}")
                    return selectedStartup as string
                end if
            end tell
            '''
            
            # Obtém configuração de inicialização
            result_startup = subprocess.run(['osascript', '-e', script_startup], 
                                          capture_output=True, text=True)
            selected_startup = result_startup.stdout.strip()
            
            if selected_startup == "CANCEL":
                return
            
            selected_startup_bool = (selected_startup.lower() == "true")
            
            # Script para número máximo de itens
            script_max_items = f'''
            tell application "System Events"
                set maxItemsOptions to {{"10", "25", "50", "100"}}
                set maxDefault to "25"
                
                if {max_items} is 10 then
                    set maxDefault to "10"
                else if {max_items} is 25 then
                    set maxDefault to "25"
                else if {max_items} is 50 then
                    set maxDefault to "50"
                else if {max_items} is 100 then
                    set maxDefault to "100"
                end if
                
                set theMaxItemsChoice to choose from list maxItemsOptions ¬
                    with title "{_('max_items_label')}" ¬
                    with prompt "{_('max_items_select')}" ¬
                    default items {{maxDefault}} ¬
                    OK button name "OK" ¬
                    cancel button name "Cancel"
                
                if theMaxItemsChoice is false then
                    return "CANCEL"
                else
                    return item 1 of theMaxItemsChoice
                end if
            end tell
            '''
            
            # Obtém número máximo de itens
            result_max_items = subprocess.run(['osascript', '-e', script_max_items], 
                                            capture_output=True, text=True)
            selected_max_items = result_max_items.stdout.strip()
            
            if selected_max_items == "CANCEL":
                return
            
            max_item_count = int(selected_max_items)
            
            # Atualiza as configurações
            new_config = current_config.copy()
            new_config['language'] = selected_language
            new_config['start_at_login'] = selected_startup_bool
            new_config['max_items'] = max_item_count
            
            # Salva as configurações
            if save_config(new_config):
                # Aplica a configuração de inicialização automática
                set_start_at_login(selected_startup_bool)
                
                # Notifica o usuário
                notify_script = f'''
                tell application "System Events"
                    display notification "{_('settings_saved')}" with title "Power Paste"
                end tell
                '''
                subprocess.run(['osascript', '-e', notify_script], check=False)
                
                # Se mudou de idioma, precisa reiniciar para aplicar
                if selected_language != current_language:
                    script_restart = f'''
                    tell application "System Events"
                        set theResponse to display dialog "{_('restart_required')}" ¬
                            with title "{_('settings_title')}" ¬
                            buttons {{"Later", "Restart Now"}} ¬
                            default button "Restart Now" ¬
                            with icon note
                        
                        if button returned of theResponse is "Restart Now" then
                            return "RESTART"
                        end if
                    end tell
                    '''
                    
                    restart_result = subprocess.run(['osascript', '-e', script_restart], 
                                                  capture_output=True, text=True)
                    
                    if restart_result.stdout.strip() == "RESTART":
                        # Reinicia o aplicativo
                        app_path = os.path.join(os.path.expanduser("~/Applications"), "Power Paste.app")
                        if not os.path.exists(app_path):
                            app_path = "/Applications/Power Paste.app"
                        
                        # Encerra esta instância e inicia uma nova
                        subprocess.Popen(['open', app_path])
                        rumps.quit_application()
                else:
                    # Apenas atualiza as configurações em tempo real
                    MAX_ITEMS_TO_SHOW = max_item_count
                    self.config = new_config
                    self.rebuild_menu()
                
        except Exception as e:
            print(f"Erro ao mostrar configurações: {e}")
            import traceback
            traceback.print_exc()

    def check_clipboard(self, _):
        """Verifica a área de transferência por novos conteúdos."""
        global LAST_ITEM_HASH
        
        try:
            # 1. Verifica se há texto
            text = pyperclip.paste()
            if text and text.strip():
                # Normaliza e gera hash
                normalized = text.replace('\r\n', '\n').replace('\r', '\n')
                text_hash = hashlib.md5(normalized.encode('utf-8', 'ignore')).hexdigest()
                
                # Verifica se é diferente do último item
                if text_hash != LAST_ITEM_HASH:
                    # Filtra textos indesejados
                    if (len(normalized) > 2 and 
                        "demorou demais" not in normalized and 
                        "# Por ora" not in normalized and
                        not (normalized.strip() in ['#', '...', '# ...', '@'])):
                        
                        # Adiciona ao histórico
                        self.add_history_item("text", normalized, text_hash)
                        print(f"Novo texto adicionado ao histórico: {normalized[:30]}...")
                        return
        except Exception as e:
            print(f"Erro ao verificar texto no clipboard: {e}")
        
        # Continua verificando imagens...
        # 2. Verifica se há imagem - primeiro tenta com APIs nativas
        try:
            pb = NSPasteboard.generalPasteboard()
            if pb.dataForType_(NSPasteboardTypePNG):
                png_data = pb.dataForType_(NSPasteboardTypePNG)
                data_bytes = png_data.bytes().tobytes()
                
                if data_bytes and len(data_bytes) > 100:
                    img_hash = hashlib.md5(data_bytes).hexdigest()
                    
                    if img_hash != LAST_ITEM_HASH:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"img_{timestamp}.png"
                        path = os.path.join(TEMP_IMAGE_DIR, filename)
                        
                        with open(path, 'wb') as f:
                            f.write(data_bytes)
                            
                        self.add_history_item("image", path, img_hash)
                        return
        except:
            pass
            
        # 3. Tenta obter imagem via comandos pbpaste como fallback
        try:
            process = subprocess.Popen(
                ['pbpaste', '-Prefer', 'public.png'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            data, _ = process.communicate(timeout=0.5)
            
            if process.returncode == 0 and data and len(data) > 100:
                # Gera hash dos dados
                img_hash = hashlib.md5(data).hexdigest()
                
                # Verifica se é diferente do último item
                if img_hash != LAST_ITEM_HASH:
                    # Salva a imagem
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"img_{timestamp}.png"
                    path = os.path.join(TEMP_IMAGE_DIR, filename)
                    
                    with open(path, 'wb') as f:
                        f.write(data)
                        
                    # Adiciona ao histórico
                    self.add_history_item("image", path, img_hash)
                    return
                    
        except:
            pass
            
        # 4. Tenta TIFF se PNG falhar
        try:
            process = subprocess.Popen(
                ['pbpaste', '-Prefer', 'public.tiff'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            data, _ = process.communicate(timeout=0.5)
            
            if process.returncode == 0 and data and len(data) > 100:
                # Gera hash dos dados
                img_hash = hashlib.md5(data).hexdigest()
                
                # Verifica se é diferente do último item
                if img_hash != LAST_ITEM_HASH:
                    try:
                        # Converte para PNG
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"img_{timestamp}.png"
                        path = os.path.join(TEMP_IMAGE_DIR, filename)
                        
                        img = Image.open(io.BytesIO(data))
                        if img.mode not in ('RGBA', 'LA'):
                            img = img.convert('RGBA')
                        img.save(path, "PNG")
                        
                        # Adiciona ao histórico
                        self.add_history_item("image", path, img_hash)
                    except:
                        pass
        except:
            pass

    def add_history_item(self, item_type, content, item_hash):
        """Adiciona um novo item ao histórico."""
        global LAST_ITEM_HASH
        
        try:
            # Verifica se já existe um item com esse hash
            for existing_item in self.history:
                if existing_item.get("hash") == item_hash:
                    # Item já existe, não adiciona duplicata
                    print(f"Item ignorado (duplicado): {item_type}, hash: {item_hash[:8]}")
                    return
            
            # Cria o item
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item = {
                "type": item_type,
                "content": content,
                "timestamp": timestamp,
                "hash": item_hash
            }
            
            # Adiciona ao início do histórico
            self.history.insert(0, item)
            
            # Remove itens antigos (mais de 7 dias)
            cutoff = datetime.now() - timedelta(days=7)
            self.history = [i for i in self.history if 
                            datetime.strptime(i.get("timestamp", "2000-01-01 00:00:00"), 
                                            "%Y-%m-%d %H:%M:%S") >= cutoff]
            
            # Atualiza o hash global
            LAST_ITEM_HASH = item_hash
            
            # Salva e atualiza o menu
            self.save_history()
            self.rebuild_menu()
            
            # Log para depuração
            print(f"Item adicionado ao histórico: {item_type}, hash: {item_hash[:8]}")
        except Exception as e:
            print(f"Erro ao adicionar item ao histórico: {e}")

if __name__ == "__main__":
    app = PowerPasteApp()
    app.run() 