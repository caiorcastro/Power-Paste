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
MAX_ITEMS_TO_SHOW = 25  # Limita o número de itens no menu
LAST_ITEM_HASH = None  # Rastreia o último item processado

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
        super(PowerPasteApp, self).__init__(
            name="Power Paste",
            icon="icon.png",
            title=None,  # Remove o título ao lado do ícone
            key='v',  # Tecla V 
            modifier=['ctrl', 'command']  # Modificadores Ctrl+Cmd
        )
        # Garantir que o diretório de imagens exista
        self.ensure_temp_dir()
        self.history = self.load_history()
        self.clean_history() # Remove duplicatas e itens inválidos
        
        # Atualizar o hash do último item conhecido ao iniciar
        if self.history:
            global LAST_ITEM_HASH
            LAST_ITEM_HASH = self.history[0].get("hash")
        
        # Cria itens fixos do menu
        self.menu_clear = rumps.MenuItem("Limpar Histórico", callback=self.clear_history)
        self.menu_about = rumps.MenuItem("Sobre Power Paste", callback=self.show_about)
            
        # Inicializa o menu
        self.menu.clear()  # Limpa o menu padrão
        self.rebuild_menu()
        
        # Registra o timer para verificação do clipboard
        self.timer = rumps.Timer(self.check_clipboard, 1.0)
        self.timer.start()

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

    def clean_history(self):
        """Remove duplicatas e entradas inválidas."""
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

    def build_history_menu(self):
        """Constrói a parte do menu com os itens do histórico."""
        # Verifica se há itens no histórico
        if not self.history:
            empty_item = rumps.MenuItem("Histórico vazio")
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
                    title = f"{display_time} | 🖼️ Imagem"
                    menu_item = rumps.MenuItem(title)
                    menu_item._idx = idx
                    menu_item.set_callback(self.open_image_in_preview)
                    self.menu.add(menu_item)
                else:
                    # Tipo desconhecido
                    title = f"{display_time} | Item desconhecido"
                    menu_item = rumps.MenuItem(title)
                    self.menu.add(menu_item)

    def paste_text_item(self, sender):
        """Manipula a seleção de um item de texto do menu."""
        try:
            idx = getattr(sender, "_idx", None)
            if idx is None or idx >= len(self.history):
                rumps.notification("Power Paste", "Erro", "Item não encontrado")
                return
                
            item = self.history[idx]
            if item.get("type") != "text":
                rumps.notification("Power Paste", "Erro", "Item não é texto")
                return
                
            text = item.get("content")
            if not text:
                rumps.notification("Power Paste", "Erro", "Texto vazio")
                return
                
            # Exibe o popup com o texto completo e opções
            self.show_text_selection_window(text)
            
        except Exception as e:
            print(f"Erro ao manipular item de texto: {e}")
            rumps.notification("Power Paste", "Erro", f"Falha: {str(e)}")

    def open_image_in_preview(self, sender):
        """Abre a imagem no Preview."""
        rumps.notification("Power Paste", "Debug", "Tentando abrir no Preview")
        print("[DEBUG] open_image_in_preview chamado")
        
        try:
            idx = getattr(sender, "_idx", None)
            if idx is None or idx >= len(self.history):
                rumps.notification("Power Paste", "Erro", "Item não encontrado")
                return
                
            item = self.history[idx]
            if item.get("type") != "image":
                rumps.notification("Power Paste", "Erro", "Item não é uma imagem")
                return
                
            content = item.get("content")
            if not content or not os.path.exists(content):
                rumps.notification("Power Paste", "Erro", "Arquivo de imagem não encontrado")
                return
                
            # Caminho absoluto da imagem
            abs_path = os.path.abspath(content)
            print(f"[DEBUG] Caminho da imagem: {abs_path}")
            
            # Executa o comando de forma mais direta e robusta
            result = subprocess.run(['open', '-a', 'Preview', abs_path], 
                               capture_output=True, 
                               text=True)
            
            if result.returncode == 0:
                rumps.notification("Power Paste", "Sucesso", "Imagem aberta no Preview")
            else:
                error = result.stderr.strip() if result.stderr else "Erro desconhecido"
                rumps.notification("Power Paste", "Erro", f"Falha ao abrir: {error}")
                print(f"[DEBUG] Erro: {error}")
                
        except Exception as e:
            print(f"[DEBUG] Exceção: {str(e)}")
            rumps.notification("Power Paste", "Erro", f"Falha: {str(e)}")

    def show_text_selection_window(self, text):
        """
        Exibe uma janela de seleção de texto usando APIs nativas do macOS
        """
        # Salva o texto temporariamente em um arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = os.path.join(tempfile.gettempdir(), f"power_paste_text_{timestamp}.txt")
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Abre o arquivo no TextEdit (editor de texto nativo do macOS)
            subprocess.run(['open', '-a', 'TextEdit', temp_file], check=False)
            
            # Notifica o usuário
            rumps.notification(
                "Power Paste", 
                "Texto disponível para edição", 
                "Selecione e copie as partes desejadas no TextEdit"
            )
        except Exception as e:
            print(f"Erro ao abrir texto para edição: {e}")
            
            # Fallback: copia o texto diretamente
            if copy_text_to_clipboard_native(text):
                rumps.notification(
                    "Power Paste", 
                    "Texto copiado", 
                    "Use Cmd+V para colar"
                )

    def clear_history(self, _=None):
        """Limpa o histórico de itens."""
        if rumps.alert(
            "Limpar Histórico", 
            "Deseja realmente limpar todo o histórico?", 
            "Sim", "Não"
        ) == 1:  # 1 = Sim, 0 = Não na API do rumps
            try:
                # Remove arquivos de imagem
                for item in self.history:
                    if item.get("type") == "image":
                        path = item.get("content", "")
                        if path and os.path.exists(path):
                            try:
                                os.remove(path)
                            except:
                                pass
                
                # Limpa o histórico
                self.history = []
                self.save_history()
                
                # Reseta o hash
                global LAST_ITEM_HASH
                LAST_ITEM_HASH = None
                
                # Atualiza o menu
                self.rebuild_menu()
                
                # Notifica o usuário
                rumps.notification(
                    "Power Paste", 
                    "Histórico limpo", 
                    "Todos os itens foram removidos"
                )
            except Exception as e:
                print(f"Erro ao limpar histórico: {e}")
                rumps.notification(
                    "Power Paste", 
                    "Erro", 
                    f"Falha ao limpar histórico: {str(e)}"
                )

    def show_about(self, _):
        """Mostra informações sobre o aplicativo."""
        rumps.alert(
            "Power Paste", 
            "Power Paste 1.2\n\n"
            "Um gerenciador de área de transferência eficiente e prático.\n\n"
            "Desenvolvido por Caio Castro\n"
            "LinkedIn: linkedin.com/in/caiorcastro\n\n"
            "Atalho: Ctrl+Cmd+V"
        )

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