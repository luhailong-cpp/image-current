from PIL import Image, ImageDraw
from pathlib import Path
b = Path(__file__).resolve().parent.parent
c = Image.new('RGB', (1000, 870), '#eee9d9')
d = ImageDraw.Draw(c)
for k, n in enumerate(range(8, 13)):
    im = Image.open(b / f'runtime/cast/W/{n:02}.png').convert('RGBA')
    cr = im.crop((924, 360, 1024, 780)).resize((200, 840))
    c.paste(cr, (k * 200, 30), cr)
    d.text((k * 200 + 10, 8), f'W cast {n:02} RIGHT EDGE', fill='#162528')
c.save(b / 'qa/cast-W-right-edge.png')
