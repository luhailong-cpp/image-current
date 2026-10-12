from pathlib import Path
from PIL import Image
D=Path(__file__).resolve().parent;old=Image.open(D/'bench-C2-right-conditioned-v4-bounded-preview-native1254.png').convert('RGB')
im=Image.new('RGB',(1254,1254),'white');im.paste(old.crop((491,630,775,873)),(491,630))
p=D/'bench-C2-right-conditioned-v6-gold-face-color-guide-native1254.png';assert not p.exists();im.save(p)

