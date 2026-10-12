from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
A=Path(sys.argv[1]);a=read(A);tile=a['tile'];im=Image.open(a['output']['file']).convert('RGB');assert im.size==(4096,4096)
Q=A.parent/'root-review-native';assert not Q.exists();Q.mkdir()
records=[]
def save(img,name,box=None):
 p=Q/name;assert not p.exists();img.save(p);records.append({'file':str(p),'sha256':sha(p),'pixels':list(img.size),'sourceBox':box,'QAOnly':True,'sourceResampling':False})
panel=Image.new('RGB',(3*280,3*280),'white');draw=ImageDraw.Draw(panel)
for row in range(1,4):
 for col in range(1,4):
  box=[col*1024-128,row*1024-128,col*1024+128,row*1024+128];panel.paste(im.crop(box),((col-1)*280,(row-1)*280+24));draw.text(((col-1)*280+3,(row-1)*280+3),f'X{row}-{col}',fill='black')
save(panel,'intersections-native-panel.png')
cat=read(B/'current-candidates.json')['tiles'];r,c=int(tile[1:3]),int(tile[5:7]);sources={}
for side,key in [('left',f'r{r:02}_c{c-1:02}'),('right',f'r{r:02}_c{c+1:02}'),('top',f'r{r-1:02}_c{c:02}'),('bottom',f'r{r+1:02}_c{c:02}')]:
 if key not in cat:continue
 e=cat[key]['candidate'];assert sha(e['file'])==e['sha256'];n=Image.open(e['file']).convert('RGB');sources[side]=e
 vertical=side in ['left','right'];panel=Image.new('RGB',(1024,1048) if vertical else (1024,1120),'white');d=ImageDraw.Draw(panel)
 for k in range(4):
  st=k*1024;part=Image.new('RGB',(256,1024) if vertical else (1024,256))
  if side=='left':part.paste(n.crop((3968,st,4096,st+1024)),(0,0));part.paste(im.crop((0,st,128,st+1024)),(128,0))
  elif side=='right':part.paste(im.crop((3968,st,4096,st+1024)),(0,0));part.paste(n.crop((0,st,128,st+1024)),(128,0))
  elif side=='top':part.paste(n.crop((st,3968,st+1024,4096)),(0,0));part.paste(im.crop((st,0,st+1024,128)),(0,128))
  else:part.paste(im.crop((st,3968,st+1024,4096)),(0,0));part.paste(n.crop((st,0,st+1024,128)),(0,128))
  panel.paste(part,(k*256,24) if vertical else (0,k*280+24));d.text((k*256+3,3) if vertical else (3,k*280+3),f'{side} {k+1}',fill='black')
 save(panel,f'{side}-native-panel.png')
for k,step in enumerate(a.get('localNativeRepairs',[])):
 l,t,r,b=step['candidateBox'];save(im.crop((l,t,r,b)),f'repair-{k+1}-native.png',[l,t,r,b])
im.resize((1024,1024)).save(Q/'overview-RESIZED-QA-ONLY.png')
(Q/'manifest.json').write_text(json.dumps({'assembly':str(A),'assemblySha256':sha(A),'target':a['output'],'neighbors':sources,'nativeQAImages':records,'overviewOnlyResized':True,'formalAccepted':False},indent=2)+'\n',encoding='utf-8')
print(Q)
