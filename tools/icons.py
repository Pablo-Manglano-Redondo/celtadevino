"""Genera los iconos «maskable» de la PWA a partir del escudo (public/img/escudo.webp).

El escudo se centra sobre el color de fondo del sitio y se escala para que ningún píxel visible
salga de la zona segura de los iconos maskable (círculo de radio 40 % del lado), así Android puede
recortarlo en círculo, gota o cuadrado sin cortar la corona ni la punta.
Uso: python3 -I tools/icons.py   (necesita Pillow)
"""
import math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
BG = (0xF4, 0xEF, 0xE4)  # --bg del tema claro
SAFE = 0.40 * 0.97        # radio de la zona segura con un pequeño margen

crest = Image.open(PUB / "img" / "escudo.webp").convert("RGBA")
crest = crest.crop(crest.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox())
w, h = crest.size
alpha = crest.getchannel("A").load()
cx, cy = w / 2, h / 2
dmax = max(math.hypot(x + .5 - cx, y + .5 - cy) for y in range(h) for x in range(w) if alpha[x, y] > 16)

for size in (192, 512):
    k = SAFE * size / dmax
    art = crest.resize((round(w * k), round(h * k)), Image.LANCZOS)
    icon = Image.new("RGBA", (size, size), BG + (255,))
    icon.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
    out = PUB / f"icon-maskable-{size}.png"
    icon.convert("RGB").save(out, optimize=True)
    print(out.relative_to(ROOT), art.size)
