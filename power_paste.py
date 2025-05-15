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
        "settings_title": "Configurações do Power Paste"
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
        "settings_title": "Configurações do Power Paste"
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
        "settings_title": "Power Paste Settings"
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
        try:
            # Carrega o idioma antes de inicializar o app
            load_language()
            
            super(PowerPasteApp, self).__init__(
                name="Power Paste",
                icon="icon.png",
                quit_button=None,  # Vamos criar nosso próprio botão de sair
                template=True      # Ícone em preto e branco para se encaixar na barra de menus
            )
            
            # Configura atalho de teclado global
            self.hotkey = "control+command+v"
            
            # Menu Vazio inicialmente
            self.menu = ['']
            
            # Configure o menu
            self.build_menu()
            
            # Garante que o diretório temporário exista
            self.ensure_temp_dir()
            
            # Carrega o histórico
            self.history = self.load_history()
            
            # Configura o timer para verificar a área de transferência
            self.timer = rumps.Timer(self.check_clipboard, 1)
            self.timer.start()
            
        except Exception as e:
            print(f"Erro na inicialização: {e}")
    
    def build_menu(self):
        # Limpa o menu atual
        self.menu.clear()
        
        # Adiciona os itens do histórico
        self.build_history_menu()
        
        # Adiciona os itens do menu básico
        separator = rumps.MenuItem(title=None)  # Separador
        clear_history = rumps.MenuItem(title=_("clear_history"))
        settings_item = rumps.MenuItem(title=_("settings"))
        about_item = rumps.MenuItem(title=_("about"))
        quit_item = rumps.MenuItem(title=_("quit"))
        
        # Conecta os callbacks
        clear_history.set_callback(self.clear_history)
        settings_item.set_callback(self.show_settings)
        about_item.set_callback(self.show_about)
        quit_item.set_callback(self.quit_app)
        
        # Adiciona items ao menu
        self.menu.add(separator)
        self.menu.add(clear_history)
        self.menu.add(settings_item)
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
        if os.path.exists(HISTORY_FILE):
            try:
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
                return []
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
        # Limpa o menu atual, mas preserva o botão de sair
        self.menu.clear()
        
        # Adiciona itens do histórico
        self.build_history_menu()
        
        # Adiciona separador e opções de gerenciamento (fixas na parte inferior)
        self.menu.add(None)  # Separador
        self.menu.add(self.menu_clear)
        self.menu.add(self.menu_about)
        self.menu.add(self.menu_quit)

    def build_history_menu(self):
        """Constrói a parte do menu com os itens do histórico."""
        # Verifica se há itens no histórico
        if not self.history:
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
        """Cola o item selecionado ou mostra janela para seleção parcial."""
        print("[DEBUG] paste_item chamado!")
        rumps.notification(
            "Power Paste", 
            _("notice"), 
            _("callback_called")
        )
        try:
            idx = getattr(sender, '_idx', None)
            if idx is None or idx >= len(self.history):
                return
                
            item = self.history[idx]
            text = item.get("content", "")
            
            if not text:
                return
                
            # Mostra uma janela para permitir seleção parcial do texto
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
            # Cria uma janela simples para mostrar o texto com pyobjc
            script = f'''
            tell application "System Events"
                set theText to "{text.replace('"', '\\"').replace('\n', '\\n')}"
                set theResult to display dialog theText buttons {{"{_('cancel')}", "{_('copy')}"}} default button 2 with title "{_('text_preview')}"
                set theButton to button returned of theResult
                
                if theButton is "{_('copy')}" then
                    return "copy_all"
                else
                    return "cancel"
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                   capture_output=True, text=True)
            
            action = result.stdout.strip()
            
            if action == "copy_all":
                # Copia o texto selecionado
                if copy_text_to_clipboard_native(text):
                    rumps.notification(
                        "Power Paste", 
                        _("notice"), 
                        _("copy_success")
                    )
                else:
                    rumps.notification(
                        "Power Paste", 
                        _("error"), 
                        _("copy_error")
                    )
            
        except Exception as e:
            print(f"Erro ao mostrar janela de seleção: {e}")
    
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
        about_window = rumps.Window(
            message=f"{_('developed_by')}\n{_('version')}\n\n{_('linkedIn')}\n{_('github')}\n\n{_('language')}",
            title=_("about"),
            ok="OK"
        )
        about_window.run()
    
    def show_settings(self, _):
        # Carrega configurações atuais
        config = load_config()
        
        settings_window = rumps.Window(
            message=f"{_('max_items_label')} {config.get('max_items', 25)}\n"
                   f"{_('start_at_login_label')} {'✓' if config.get('start_at_login', True) else '✗'}\n"
                   f"{_('language_label')} {_('language').split(':')[1].strip()}",
            title=_("settings_title"),
            dimensions=(300, 200)
        )
        
        # Dropdown de idiomas
        language_menu = [
            "🇧🇷 Português do Brasil", 
            "🇵🇹 Português de Portugal", 
            "🇺🇸 English"
        ]
        settings_window.add_buttons("Cancel")
        settings_window.add_buttons(_("save_button"))
        
        # Dropdown para número máximo de itens
        max_items_options = ["10", "15", "20", "25", "30", "50", "100"]
        current_max = str(config.get('max_items', 25))
        if current_max not in max_items_options:
            max_items_options.append(current_max)
            max_items_options.sort(key=lambda x: int(x))
        
        # Índice da língua atual
        current_lang = config.get('language', 'pt_BR')
        lang_index = 0
        if current_lang == "pt_PT":
            lang_index = 1
        elif current_lang == "en_US":
            lang_index = 2
        
        # Adiciona campos ao formulário
        settings_window.add_dropdown(max_items_options, max_items_options.index(current_max) if current_max in max_items_options else 3)
        settings_window.add_dropdown(language_menu, lang_index)
        settings_window.add_checkbox("Iniciar com o sistema", config.get('start_at_login', True))
        
        # Processa o resultado
        response = settings_window.run()
        if response.clicked == 1:  # Botão "Salvar"
            try:
                # Mapeia a resposta do dropdown para o código de idioma
                selected_lang_index = response.dropdown[1]
                lang_map = {
                    0: "pt_BR",
                    1: "pt_PT",
                    2: "en_US"
                }
                selected_lang = lang_map.get(selected_lang_index, "pt_BR")
                
                # Número máximo de itens
                selected_max_items = int(max_items_options[response.dropdown[0]])
                
                # Atualiza configurações
                new_config = {
                    'max_items': selected_max_items,
                    'start_at_login': response.checkbox,
                    'language': selected_lang
                }
                
                # Salva configurações
                if save_config(new_config):
                    # Atualiza idioma imediatamente
                    global CURRENT_LANGUAGE, MAX_ITEMS_TO_SHOW
                    CURRENT_LANGUAGE = selected_lang
                    MAX_ITEMS_TO_SHOW = selected_max_items
                    
                    # Salva o idioma em um arquivo separado para compatibilidade
                    os.makedirs(os.path.dirname(LANGUAGE_FILE), exist_ok=True)
                    with open(LANGUAGE_FILE, 'w') as f:
                        f.write(selected_lang)
                    
                    # Configura início automático
                    set_start_at_login(response.checkbox)
                    
                    # Aviso de sucesso
                    success_window = rumps.Window(
                        message=f"{_('settings_saved')}\n{_('restart_required')}",
                        title=_("notice"),
                        ok="OK"
                    )
                    success_window.run()
                    
                    # Reconstrói o menu
                    self.build_menu()
                else:
                    error_window = rumps.Window(
                        message="Erro ao salvar configurações",
                        title=_("error"),
                        ok="OK"
                    )
                    error_window.run()
            except Exception as e:
                error_window = rumps.Window(
                    message=f"Erro: {str(e)}",
                    title=_("error"),
                    ok="OK"
                )
                error_window.run()
    
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