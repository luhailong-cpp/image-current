from pathlib import Path
from PIL import Image
D=Path(__file__).resolve().parent;old=Image.open(D/'bench-G3-left-conditioned-v6-before-guide-native1254.png').convert('RGBA')
im=Image.new('RGBA',(1254,1254),(255,255,255,0));im.paste(old.crop((456,312,679,467)),(456,312));im.paste((255,255,255,0),(520,344,615,435))
p=D/'bench-G3-left-conditioned-v8-upper-contour-guide-native1254.png';assert not p.exists();im.save(p)

