from PIL import Image, ImageDraw, ImageFont
import os

# Criar uma imagem 32x32 pixels com fundo transparente
icon = Image.new('RGBA', (32, 32), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(icon)

# Desenhar um círculo como fundo
draw.ellipse((1, 1, 31, 31), fill=(52, 152, 219, 255), outline=(41, 128, 185, 255))

# Adicionar uma letra "P" ao centro
# Como não temos certeza de quais fontes estão disponíveis no sistema, vamos usar um método alternativo
# para desenhar um "P" 
draw.rectangle((10, 8, 16, 24), fill=(255, 255, 255, 255))
draw.rectangle((10, 8, 22, 14), fill=(255, 255, 255, 255))
draw.rectangle((10, 15, 22, 21), fill=(255, 255, 255, 255))

# Salvar o ícone
icon.save('icon.png')

print(f"Ícone criado com sucesso em: {os.path.abspath('icon.png')}") 