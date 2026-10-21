from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image, ImageDraw
T=Path(__file__).resolve().parents[1]
O=T/'pipeline/qa/continue-20261013c-v01'
assert not O.exists()
O.mkdir(parents=True)
A=T/'pipeline/output/4199c69ca35a7597/assembly.json'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=read(A);e=a['output'];p=Path(e['file']);assert sha(p)==e['sha256']
im=Image.open(p).convert('RGB');assert im.size==(4096,4096)
records=[];panels=[]
def save(name,part,kind,box=None,members=None):
 path=O/(name+'.png');assert not path.exists();part.save(path)
 assert Image.open(path).convert('RGB').tobytes()==part.tobytes()
 entry={'id':name,'file':str(path),'sha256':sha(path),'pixels':list(part.size),'kind':kind,'source':e,'cropBox':box,'QAOnly':True,'sourceResampling':False,'visualReview':'pending'}
 if members:entry.update(members=members,cropPixelsUnchanged=True)
 records.append(entry);return entry
def panel(name,entries,side):
 w,h=entries[0]['pixels'];cv=Image.new('RGB',((w+16)*len(entries),h+24) if side else (w,(h+24)*len(entries)),(255,255,255));draw=ImageDraw.Draw(cv)
 for k,en in enumerate(entries):
  x,y=((w+16)*k,24) if side else (0,(h+24)*k+24)
  cv.paste(Image.open(en['file']).convert('RGB'),(x,y));draw.text((x+3,y-20),en['id'],fill=(0,0,0))
 en=save(name,cv,'native-crop-panel',members=[e['id'] for e in entries]);panels.append(en)
for c in range(1,4):
 group=[]
 for r in range(4):
  box=[c*1024-119,r*1024,c*1024+119,(r+1)*1024]
  group.append(save(f'V{c}-{r+1}',im.crop(box),'internal-vertical-seam',box))
 panel(f'V{c}-panel',group,True)
for r in range(1,4):
 group=[]
 for c in range(4):
  box=[c*1024,r*1024-119,(c+1)*1024,r*1024+119]
  group.append(save(f'H{r}-{c+1}',im.crop(box),'internal-horizontal-seam',box))
 panel(f'H{r}-panel',group,False)
for r in range(1,4):
 group=[]
 for c in range(1,4):
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256]
  group.append(save(f'X{r}-{c}',im.crop(box),'internal-intersection',box))
 panel(f'X{r}-panel',group,True)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r16_c05','assembly':str(A),'assemblySha256':sha(A),'candidate':e,'nativeSelected':16,'artworkResampled':False,'artworkModified':False,'records':records,'panelFiles':[e['file'] for e in panels],'nativeCropCount':33,'internalAccepted':False,'formalAccepted':False,'externalQa':'pending-missing-native-neighbors','QAOnly':True}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':str(O/'manifest.json'),'panels':[e['file'] for e in panels],'nativeCropCount':33},ensure_ascii=False))
