from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json
t=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c07');base=Image.open(t/'native/s02_02_layout01.png').convert('RGB');north=Image.open(t/'native/s01_02_geometry05.png').convert('RGB');west=Image.open(t/'native/s02_01.png').convert('RGB');nw=Image.open(t/'native/s01_01.png').convert('RGB')
im=base.copy();im.paste(north.crop((0,1024,1254,1254)),(0,0));im.paste(west.crop((1024,0,1254,1254)),(0,0));im.paste(nw.crop((1024,1024,1254,1254)),(0,0))
d=ImageDraw.Draw(im);d.rectangle((230,230,1037,279),fill=(233,227,216))
a=np.array(north)
def groups(y):
 q=np.where((a[y,:,0]<170)&(a[y,:,0].astype(int)-a[y,:,2]>30)&(np.arange(1254)>230)&(np.arange(1254)<1038))[0]
 chunks=np.split(q,np.where(np.diff(q)>1)[0]+1);return [float(v.mean()) for v in chunks if len(v)>0]
row1=groups(1243);row2=groups(1253)
strokes=[]
for x in row2:
 before=min(row1,key=lambda v:abs(v-x));dx=x-before
 endx=x+dx*5.1
 d.line([(x-dx*.5,224),(endx,280)],fill=(255,250,232),width=8);d.line([(x-dx*.5,224),(endx,280)],fill=(130,99,58),width=3)
 strokes.append({'atTopBandEnd':[x,229],'directionPer10Rows':dx,'atHorizontalTransition':[endx,280]})
target=t/'layout-only/s02_02_cap02.continuation-guide.png';assert not target.exists();im.save(target)
(target.with_suffix('.png.derivation.json')).write_text(json.dumps({'operation':'LAYOUT ONLY, exact native TOP230 LEFT230 NW230 and 50px flat diamond-continuation strip, original slab/road artwork outside strip preserved','north':'native/s01_02_geometry05.png bottom230','west':'native/s02_01.png right230','northwest':'native/s01_01.png bottom-right230','guideStrokes':strokes,'sourceResampled':False,'finalArt':False},indent=2)+'\n')
print(json.dumps({'file':str(target),'strokes':strokes}))

