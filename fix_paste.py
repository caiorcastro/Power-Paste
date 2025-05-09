#!/usr/bin/env python3
# Este script auxiliar usa os métodos nativos do macOS para garantir 
# que o conteúdo seja efetivamente colocado na área de transferência

import sys
import os
import subprocess
from Foundation import NSString, NSUTF8StringEncoding
from AppKit import NSPasteboard, NSPasteboardTypeString

def copy_text_to_clipboard(text):
    """
    Coloca texto na área de transferência usando APIs nativas do macOS.
    Mais confiável que métodos Python padrão.
    """
    # Método 1: Via APIs nativas
    try:
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        ns_string = NSString.stringWithString_(text)
        result = pb.setString_forType_(ns_string, NSPasteboardTypeString)
        print(f"Método 1 (AppKit): {'Sucesso' if result else 'Falha'}")
    except Exception as e:
        print(f"Erro no método AppKit: {e}")
    
    # Método 2: Via pbcopy (backup)
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        print("Método 2 (pbcopy): Completado")
    except Exception as e:
        print(f"Erro no método pbcopy: {e}")
    
    # Método 3: Via AppleScript (último recurso)
    try:
        escaped_text = text.replace('"', '\\"').replace("'", "\\'")
        script = f'set the clipboard to "{escaped_text}"'
        subprocess.run(['osascript', '-e', script], check=True)
        print("Método 3 (AppleScript): Completado")
    except Exception as e:
        print(f"Erro no método AppleScript: {e}")

def copy_image_to_clipboard(image_path):
    """
    Coloca imagem na área de transferência usando APIs nativas do macOS.
    """
    # Primeiro verificamos se o arquivo existe
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo {image_path} não existe")
        return False
    
    # Obter o caminho absoluto
    abs_path = os.path.abspath(image_path)
    print(f"Copiando imagem: {abs_path}")
    
    # Método 1: Via AppleScript versão PNG
    try:
        script = f'''
        set theImage to (POSIX file "{abs_path}")
        set the clipboard to (read theImage as «class PNGf»)
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True)
        if result.returncode == 0:
            print("Método 1 (AppleScript PNG): Sucesso")
            return True
        else:
            print(f"Método 1 erro: {result.stderr.decode()}")
    except Exception as e:
        print(f"Erro no método 1: {e}")
    
    # Método 2: Via AppleScript versão TIFF
    try:
        script = f'''
        set theImage to (POSIX file "{abs_path}")
        set the clipboard to (read theImage as «class TIFF»)
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True)
        if result.returncode == 0:
            print("Método 2 (AppleScript TIFF): Sucesso")
            return True
        else:
            print(f"Método 2 erro: {result.stderr.decode()}")
    except Exception as e:
        print(f"Erro no método 2: {e}")
    
    # Método 3: Via AppleScript simplificado
    try:
        script = f'''
        set theImage to (POSIX file "{abs_path}")
        tell application "System Events"
            set the clipboard to (read theImage)
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True)
        if result.returncode == 0:
            print("Método 3 (AppleScript genérico): Sucesso")
            return True
        else:
            print(f"Método 3 erro: {result.stderr.decode()}")
    except Exception as e:
        print(f"Erro no método 3: {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python fix_paste.py [text|image] [conteúdo/caminho]")
        sys.exit(1)
        
    tipo = sys.argv[1]
    conteudo = sys.argv[2]
    
    if tipo == "text":
        copy_text_to_clipboard(conteudo)
        print("Texto copiado para área de transferência")
    elif tipo == "image":
        if copy_image_to_clipboard(conteudo):
            print("Imagem copiada para área de transferência")
        else:
            print("Falha ao copiar imagem")
    else:
        print(f"Tipo desconhecido: {tipo}") 