from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
T=Path(__file__).resolve().parent;Z=T.parent
C=T/'candidate/r07_c05-candidate-hard-1672ae5e4698.png'
N=Z/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c05-joint-4096.png'
W=Z/'r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png'
O=T/'qa/external-north-west-1672ae5e4698';O.mkdir(exist_ok=True)
a=Image.open(C).convert('RGB');n=Image.open(N).convert('RGB');w=Image.open(W).convert('RGB')
entries=[]
for side,other in [('north',n),('west',w)]:
 band=Image.new('RGB',(4096,640) if side=='north' else (640,4096))
 if side=='north':
  band.paste(other.crop((0,3776,4096,4096)),(0,0));band.paste(a.crop((0,0,4096,320)),(0,320))
 else:
  band.paste(other.crop((3776,0,4096,4096)),(0,0));band.paste(a.crop((0,0,320,4096)),(320,0))
 for i in range(4):
  im=band.crop((i*1024,0,(i+1)*1024,640)) if side=='north' else band.crop((0,i*1024,640,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90)
  f=O/f'{side}-segment{i+1:02}.png';im.save(f)
  entries.append({'name':f.stem,'file':str(f),'sha256':p.sha(f),'side':side,'nativePixelScale':1})
 for i in range(1,4):
  im=band.crop((i*1024-160,160,i*1024+160,480)) if side=='north' else band.crop((160,i*1024-160,480,i*1024+160))
  f=O/f'{side}-junction-{i*1024}.png';im.save(f)
  entries.append({'name':f.stem,'file':str(f),'sha256':p.sha(f),'side':side,'nativePixelScale':1})
p.write_json(O/'index.json',{'candidate':{'file':str(C),'sha256':p.sha(C)},'north':{'file':str(N),'sha256':p.sha(N)},'west':{'file':str(W),'sha256':p.sha(W)},'entries':entries,'formalAccepted':False},replace=False)
print(O)

