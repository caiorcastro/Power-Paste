import os
import subprocess

# Verifica se o arquivo original existe
if not os.path.exists("icon.png"):
    print("Arquivo icon.png não encontrado!")
    exit(1)

# Cria um diretório temporário
if not os.path.exists("icns.iconset"):
    os.makedirs("icns.iconset")

# Tamanhos necessários para um ícone macOS
sizes = [16, 32, 64, 128, 256, 512, 1024]

# Gera as imagens em diferentes tamanhos
for size in sizes:
    # Ícone normal
    output_file = f"icns.iconset/icon_{size}x{size}.png"
    subprocess.run([
        "sips",
        "-z", str(size), str(size),
        "icon.png",
        "--out", output_file
    ])
    
    # Ícone @2x para Retina
    if size < 512:  # Não precisamos de 2048
        output_file = f"icns.iconset/icon_{size}x{size}@2x.png"
        double_size = size * 2
        subprocess.run([
            "sips",
            "-z", str(double_size), str(double_size),
            "icon.png",
            "--out", output_file
        ])

# Converte para formato .icns
subprocess.run([
    "iconutil",
    "-c", "icns",
    "-o", "icon.icns",
    "icns.iconset"
])

# Limpa arquivos temporários
subprocess.run(["rm", "-rf", "icns.iconset"])

print("Ícone convertido com sucesso para icon.icns") 