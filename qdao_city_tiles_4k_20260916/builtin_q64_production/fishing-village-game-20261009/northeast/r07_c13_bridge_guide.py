import json,hashlib,sys
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
name=sys.argv[1];x,y=map(int,sys.argv[2:4]);w=int(sys.argv[4])if len(sys.argv)>4 else 1254;h=int(sys.argv[5])if len(sys.argv)>5 else w;box=[x,y,x+w,y+h]
im=Image.new('RGB',(w,h));sources=[];area=0
for tile in ['r07_c12','r07_c13']:
 s=read(Z/'records'/f'{tile}.working-selection.json');s=s.get('patches',s)
 for r in range(1,5):
  for c in range(1,5):
   pid=f'{tile}_p{r}{c}';entry=s.get(pid,pid+'-v1.png');entry=entry.get('path',entry.get('file'))if isinstance(entry,dict)else entry
   p=Z/'native'/Path(entry).name
   nx=(int(tile[5:7])-1)*4096+(c-1)*1024;ny=(int(tile[1:3])-1)*4096+(r-1)*1024
   a,b,cc,d=max(x,nx),max(y,ny),min(x+w,nx+1024),min(y+h,ny+1024)
   if a>=cc or b>=d:continue
   q=Image.open(p);crop=[a-nx+115,b-ny+115,cc-nx+115,d-ny+115];paste=[a-x,b-y]
   im.paste(q.crop(crop),paste);area+=(cc-a)*(d-b);sources.append({**ref(p),'sourceCropBox':crop,'targetPasteAt':paste,'provenanceRecord':ref(Path(str(p)+'.generation.json'))})
assert area==w*h,area
out=Z/'guides'/f'r07_c13-{name}.native-target.png';assert not out.exists();im.save(out)
record={**ref(out),'nativeGlobalBox':box,'nativeSize':[w,h],'operation':'Exact selected core integer crop and opaque paste only, no resize or repaint','sources':sources}
Path(str(out)+'.derived.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
