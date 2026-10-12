from pathlib import Path
from PIL import Image
import json,hashlib,sys
T=Path(__file__).resolve().parent;Q=T/'qa'/'native-repairs';C=T/'candidates'/f'{T.name}.candidate.png';W=T.parent/'r07_c13'/'candidates'/'r07_c13.candidate.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2),encoding='utf-8')
def crop(y):
 im=Image.new('RGB',(1254,1254));im.paste(Image.open(W).convert('RGB').crop((3712,y,4096,y+1254)),(0,0));im.paste(Image.open(C).convert('RGB').crop((0,y,870,y+1254)),(384,0));return im
cmd,name=sys.argv[1:3]
if cmd=='crop':
 y=int(sys.argv[3]);dest=Q/(name+'-input.png');crop(y).save(dest);save(Q/(name+'-input.json'),{'file':str(dest),'sha256':sha(dest),'origin':[-384,y],'size':[1254,1254],'source':str(C),'sourceSha256':sha(C),'west':str(W),'westSha256':sha(W),'operation':'integer joined crop, no resampling'})
elif cmd=='apply':
 meta=json.loads((Q/(name+'-input.json')).read_text());y=meta['origin'][1];assert crop(y).tobytes()==Image.open(meta['file']).convert('RGB').tobytes();l,t,r,b=map(int,sys.argv[3:7]);assert 384<=l<r<=1254
 im=Image.open(C).convert('RGB');before=sha(C);native=T/'native'/(name+'.png');new=Image.open(native).convert('RGB');assert new.size==(1254,1254)
 mask=Image.new('L',(1254,1254),0);pix=mask.load()
 for yy in range(t,b):
  for x in range(l,r):
   dx=r-x if l==384 else min(x-l+1,r-x);dy=yy-t+1 if y+b==4096 else min(yy-t+1,b-yy);pix[x,yy]=round(255*min(1,dx/16,dy/16))
 mp=Q/(name+'-mask.png');mask.save(mp);im.paste(new,(-384,y),mask);im.save(C);crop(y).save(Q/(name+'-after.png'))
 rec={'repair':name,'input':meta,'beforeCandidateSha256':before,'native':str(native),'nativeSha256':sha(native),'mask':str(mp),'maskSha256':sha(mp),'localMaskBounds':[l,t,r,b],'origin':[-384,y],'output':str(C),'outputSha256':sha(C),'resized':False,'blurred':False,'warped':False,'method':'integer native overlay own tile only; 16px mask perimeter taper except exact shared edge and south end; no blur/resampling'}
 save(Q/(name+'-integration.json'),rec);side=Path(str(C)+'.generation.json');d=json.loads(side.read_text());d['repairs'].append(rec);d['sha256']=sha(C);save(side,d);print(rec['outputSha256'])
