from PIL import Image, ImageDraw
import os

# Criar uma nova imagem com fundo transparente
img = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Cores
primary = (52, 152, 219, 255)  # Azul principal
shadow = (41, 128, 185, 255)   # Azul escuro para sombra
highlight = (93, 173, 226, 255) # Azul claro para destaque
white = (255, 255, 255, 255)   # Branco

# Desenhar o círculo de fundo com gradiente
draw.ellipse((0, 0, 17, 17), fill=primary, outline=shadow)

# Desenhar a prancheta (documento)
# Corpo principal da prancheta
draw.rectangle((4, 3, 14, 15), fill=white, outline=shadow)

# Clip da prancheta (parte superior)
draw.rectangle((5, 2, 13, 4), fill=highlight, outline=shadow)

# Linhas do documento
draw.line([(4, 6), (14, 6)], fill=shadow, width=1)
draw.line([(4, 9), (14, 9)], fill=shadow, width=1)
draw.line([(4, 12), (14, 12)], fill=shadow, width=1)

# Salvar a imagem
img.save('icon.png')

print(f"Ícone criado com sucesso em: {os.path.abspath('icon.png')}") 