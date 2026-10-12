from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,math
t=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c07');base=Image.open(t/'native/s04_02_road02.png').convert('RGB');im=base.copy();d=ImageDraw.Draw(im)
def upper(x):return 300+101*math.exp(-.00673*(x-230))-.0008*max(x-850,0)**2
# Guide-only erase the old offset road around corrected route; fully AI-rendered material will replace flats.
for x in range(230,1071):
 u=upper(x);d.line([(x,238),(x,660)],fill=(231,225,214),width=1)
 d.line([(x,round(u-53)),(x,round(u+74+54))],fill=(234,229,219),width=1)
 d.line([(x,round(u)),(x,round(u+74))],fill=(130,155,174),width=1)
for offset,color,width in [(-53,(112,91,64),3),(0,(103,97,82),3),(74,(103,97,82),3),(128,(112,91,64),3)]:
 pts=[(x,upper(x)+offset) for x in range(230,1071)];d.line(pts,fill=color,width=width)
for x in [330,450,580,710,840,970]:
 u=upper(x)
 d.line([(x-15,u),(x+15,u+74)],fill=(225,229,222),width=5);d.line([(x-15,u),(x+15,u+74)],fill=(115,107,88),width=2)
 d.line([(x-25,u-53),(x-15,u)],fill=(119,101,77),width=2);d.line([(x+15,u+74),(x+25,u+128)],fill=(119,101,77),width=2)
# Preserve roof silhouette and all its current native finished samples.
a=np.array(base);b=np.array(im);roof=(a[:,:,1].astype(int)-a[:,:,0]>35)&(a[:,:,2].astype(int)-a[:,:,0]>25)&(a[:,:,1]>70);b[roof]=a[roof];im=Image.fromarray(b)
im.paste(Image.open(t/'native/s04_01_continuity05.png').convert('RGB').crop((1024,0,1254,1254)),(0,0))
target=t/'layout-only/s04_02_continuity03.continuation-guide.png';assert not target.exists();im.save(target)
(target.with_suffix('.png.derivation.json')).write_text(json.dumps({'operation':'LAYOUT ONLY: current tile context, exact native LEFT230 and simple road route placeholders; not production art','leftAnchor':'native/s04_01_continuity05.png right230','interior':'flat geometric road with nativeLEFT upper400/lower474 endpoint; existing roof samples retained','sourceResampled':False,'finalArt':False},indent=2)+'\n')
print(target)

