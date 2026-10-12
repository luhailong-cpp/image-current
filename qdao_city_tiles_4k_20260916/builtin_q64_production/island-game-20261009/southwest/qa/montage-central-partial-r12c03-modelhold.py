from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
p='central-partial-r12c03-rows123-modelhold-v01';out=[]
def concat(paths,dest,axis):
 ims=[Image.open(x).convert('RGB') for x in paths];w=sum(i.width for i in ims) if axis==0 else max(i.width for i in ims);h=sum(i.height for i in ims) if axis==1 else max(i.height for i in ims);canvas=Image.new('RGB',(w,h));x=y=0
 for im in ims:canvas.paste(im,(x,y));x+=im.width if axis==0 else 0;y+=im.height if axis==1 else 0
 assert not dest.exists();canvas.save(dest);out.append(metadata(dest,'native100 QA montage; only exact crop/paste; no resampling'))
for r in range(1,4):concat([ROOT/'qa'/(p+f'-v{x}-r{r}-native100.png') for x in [1024,2048,3072]],ROOT/'qa'/(p+f'-vertical-row{r}-native100.png'),0)
for c in range(1,5):concat([ROOT/'qa'/(p+f'-h{y}-c{c}-native100.png') for y in [1024,2048]],ROOT/'qa'/(p+f'-horizontal-column{c}-native100.png'),1)
dump(ROOT/'qa'/(p+'-montages.json'),{'views':out,'scale':'1:1','segments':17,'formalAccepted':False})
print({'montages':len(out),'segments':17})
