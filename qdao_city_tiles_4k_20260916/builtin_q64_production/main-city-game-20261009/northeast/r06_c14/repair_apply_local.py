from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,sys
T=Path(__file__).resolve().parent;Q=T/'qa'/'native-repairs';C=T/'candidates'/f'{T.name}.candidate.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
cmd,name=sys.argv[1:3]
if cmd=='crop':
 x,y=map(int,sys.argv[3:5]);im=Image.open(C).convert('RGB');assert 0<=x<=2842 and 0<=y<=2842
 dest=Q/(name+'-input.png');im.crop((x,y,x+1254,y+1254)).save(dest)
 save(Q/(name+'-input.json'),{'file':str(dest),'sha256':sha(dest),'source':str(C),'sourceSha256':sha(C),'origin':[x,y],'size':[1254,1254],'operation':'integer crop no resampling'})
 print(dest)
elif cmd=='apply':
 bounds=list(map(int,sys.argv[3:7]))
 meta=json.loads((Q/(name+'-input.json')).read_text(encoding='utf8'))
 im=Image.open(C).convert('RGB');before=sha(C);ox,oy=meta['origin'];actual=im.crop((ox,oy,ox+1254,oy+1254))
 sourcecrop=Image.open(meta['file']).convert('RGB')
 assert actual.tobytes()==sourcecrop.tobytes(),'Current candidate crop must equal recorded source input pixels'
 native=T/'native'/(name+'.png');new=Image.open(native).convert('RGB');assert new.size==(1254,1254)
 x1,y1,x2,y2=bounds;assert 0<=x1<x2<=1254 and 0<=y1<y2<=1254
 mask=Image.new('L',(1254,1254),0);pix=mask.load()
 for y in range(y1,y2):
  for x in range(x1,x2):
   dx=min(x-x1+1,x2-x);dy=min(y-y1+1,y2-y)
   if ox+x2==4096:dx=x-x1+1
   if oy+y2==4096:dy=y-y1+1
   pix[x,y]=round(255*min(1,dx/16,dy/16))
 mp=Q/(name+'-mask.png');mask.save(mp)
 im.paste(new,(ox,oy),mask);im.save(C)
 record={'repair':name,'input':meta,'beforeCandidateSha256':before,'native':str(native),'nativeSha256':sha(native),'mask':str(mp),'maskSha256':sha(mp),'localMaskBounds':bounds,'origin':[ox,oy],'output':str(C),'outputSha256':sha(C),'resized':False,'blurred':False,'warped':False,'method':'integer native overlay; 16px alpha perimeter taper only; no pixel resampling or blur'}
 save(Q/(name+'-integration.json'),record)
 im.crop((ox,oy,ox+1254,oy+1254)).save(Q/(name+'-after.png'))
 summary=json.loads(Path(str(C)+'.generation.json').read_text(encoding='utf8'))
 summary['repairs'].append(record);summary['sha256']=sha(C);summary['operation']='native core assembly plus localized native repair overlays';save(Path(str(C)+'.generation.json'),summary)
 side=Path(str(native)+'.generation.json');d=json.loads(side.read_text());d['status']='integrated-candidate-awaiting-seam-review';save(side,d)
 print(json.dumps(record))
else:raise ValueError(cmd)

