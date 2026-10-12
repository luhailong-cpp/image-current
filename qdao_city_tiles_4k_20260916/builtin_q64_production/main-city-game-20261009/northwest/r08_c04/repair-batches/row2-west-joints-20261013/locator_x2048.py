from pathlib import Path
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent/'joint-x2048-01';im=Image.open(D/'edit-target.png').convert('RGB');d=ImageDraw.Draw(im)
for b in [(565,262,707,479),(574,928,700,1096)]:d.rectangle(b,outline=(0,220,230),width=2)
im.save(D/'locator-only.png')

