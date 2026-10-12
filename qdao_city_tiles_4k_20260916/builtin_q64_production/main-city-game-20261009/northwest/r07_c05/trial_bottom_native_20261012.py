from pathlib import Path
import sys,argparse
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
T=Path(__file__).resolve().parent;Z=T.parent
ap=argparse.ArgumentParser();ap.add_argument('version');a=ap.parse_args()
D=T/'qa'/('trial-'+a.version);D.mkdir(exist_ok=True)
out=Image.new('RGB',(4096,4096));sources=[]
for r in range(1,5):
 for c in range(1,5):
  pid=f's{r:02}_{c:02}';f=T/'native'/(a.version+'.png') if pid==a.version[:6] else p.selected_path(T,pid)
  im=Image.open(f).convert('RGB');out.paste(im.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
  sources.append({'id':pid,'file':str(f),'sha256':p.sha(f)})
f=D/'candidate.png';out.save(f)
imgs={'north':out.crop((0,2752,1024,3392)),'east':out.crop((864,3072,1184,4096)).transpose(Image.Transpose.ROTATE_90),'north-east-junction':out.crop((864,2912,1184,3232))}
west=Image.open(Z/'r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png').convert('RGB')
b=Image.new('RGB',(640,4096));b.paste(west.crop((3776,0,4096,4096)),(0,0));b.paste(out.crop((0,0,320,4096)),(320,0))
imgs['west']=b.crop((0,3072,640,4096)).transpose(Image.Transpose.ROTATE_90)
imgs['north-west-junction']=b.crop((160,2912,480,3232))
entries=[]
for n,im in imgs.items():
 q=D/(n+'.png');im.save(q);entries.append({'name':n,'file':str(q),'sha256':p.sha(q),'nativePixelScale':1})
p.write_json(D/'index.json',{'candidate':{'file':str(f),'sha256':p.sha(f)},'sources':sources,'entries':entries,'formalAccepted':False},replace=False)
print(D)

