from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
p='central-north-roof-reselect-v01';m=load(ROOT/'qa'/(p+'-manifest.json'));a,b=[Image.open(x['candidate']['path']).convert('RGB') for x in m['tiles']]
views=[]
for c in range(4):
 out=Image.new('RGB',(1024,600));out.paste(a.crop((c*1024,3796,(c+1)*1024,4096)),(0,0));out.paste(b.crop((c*1024,0,(c+1)*1024,300)),(0,300));path=ROOT/'qa'/(p+f'-paired-c{c+1}-native100.png');assert not path.exists();out.save(path);views.append({**metadata(path,'paired north boundary 1:1 QA only'),'globalBox':[12288+c*1024,40660,12288+(c+1)*1024,41260],'boundaryY':300,'nativeScale':'1:1'})
dump(ROOT/'qa'/(p+'-paired-views.json'),{'sources':m['tiles'],'views':views,'interpolation':False,'formalAccepted':False})
print({'views':len(views)})
