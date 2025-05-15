from PIL import Image, ImageDraw
import os

# Criar uma nova imagem com fundo transparente
img = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Cores
primary = (52, 152, 219, 255)  # Azul principal
secondary = (41, 128, 185, 255)  # Azul escuro para contorno
white = (255, 255, 255, 255)  # Branco

# Desenhar o círculo de fundo com gradiente suave
draw.ellipse((0, 0, 17, 17), fill=primary, outline=secondary)

# Desenhar o símbolo de copiar (documento)
# Documento principal
draw.rectangle((4, 3, 14, 15), fill=white, outline=secondary)
# Linha superior do documento
draw.line([(4, 6), (14, 6)], fill=secondary, width=1)
# Linha do meio do documento
draw.line([(4, 9), (14, 9)], fill=secondary, width=1)
# Linha inferior do documento
draw.line([(4, 12), (14, 12)], fill=secondary, width=1)

# Salvar a imagem
img.save('icon.png')

print(f"Ícone criado com sucesso em: {os.path.abspath('icon.png')}") 