from pathlib import Path
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;D=B/'attempt-02';D.mkdir(exist_ok=False)
im=Image.open(B/'edit-target.png').convert('RGB');d=ImageDraw.Draw(im);d.rectangle((280,310,1010,1253),outline=(0,220,230),width=3);im.save(D/'locator-only.png')

