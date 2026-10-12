"""Owned r05_c13 candidate selection and native-only QA assembly; no art synthesis."""
import argparse,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent;T='r05_c13';O=(49152,16384)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(p,d):
 Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def select(p,v):
 n=Z/'native'/f'{p}-{v}.png';im=Image.open(n);assert im.size==(1254,1254)
 s=Z/'records'/f'{T}.working-selection.json';d=json.loads(s.read_text(encoding='utf-8')) if s.exists() else {}
 q=list((Z/'qa').glob(f'{p}-{v}-exact_native_*.png'))
 write(Z/'qa'/f'{p}-{v}.visual-review.json',{'reviewer':'southern_extension','createdAtUtc':datetime.now(timezone.utc).isoformat(),'native':ref(n),'nativeDimensions':list(im.size),'viewedFullNative':True,'viewedNativeSeams':[dict(ref(f),verdict='main_geometry_pass') for f in q],'verdict':'candidate_main_geometry_pass','formalAccepted':False,'note':'All listed images visually inspected at native resolution before this selection. Minor painted texture variation is allowed; external unresolved fronts remain pending.'})
 d[p]=n.name;write(s,d);print(json.dumps({'selected':n.name}))
def assemble(v):
 d=json.loads((Z/'records'/f'{T}.working-selection.json').read_text(encoding='utf-8'));assert len(d)==16
 out=Z/'tiles'/f'{T}.candidate-{v}.png';assert not out.exists();im=Image.new('RGB',(4096,4096));contrib=[]
 for r in range(1,5):
  for c in range(1,5):
   p=f'{T}_p{r}{c}';n=Z/'native'/d[p];a=Image.open(n).convert('RGB');assert a.size==(1254,1254);x=(c-1)*1024;y=(r-1)*1024;im.paste(a.crop((115,115,1139,1139)),(x,y));contrib.append(dict(ref(n),patchId=p,sourceCrop=[115,115,1139,1139],destinationBox=[x,y,x+1024,y+1024],globalCoreBox=[O[0]+x,O[1]+y,O[0]+x+1024,O[1]+y+1024]))
 im.save(out);qa=Z/'qa'/f'{T}-{v}';qa.mkdir(exist_ok=False);items=[]
 def crop(name,box):
  p=qa/f'{name}.native-1to1.png';a=im.crop(box);a.save(p);items.append(dict(ref(p),name=name,size=list(a.size),tileBox=list(box),rawRGBPixelSha256=hashlib.sha256(a.tobytes()).hexdigest()))
 for r in range(1,5):
  for c in range(1,5):
   x=(c-1)*1024;y=(r-1)*1024;crop(f'core_p{r}{c}',[x,y,x+1024,y+1024])
   if c<4:crop(f'v_p{r}{c}_p{r}{c+1}',[x+896,y,x+1152,y+1024])
   if r<4:crop(f'h_p{r}{c}_p{r+1}{c}',[x,y+896,x+1024,y+1152])
 for r in range(1,4):
  for c in range(1,4):crop(f'junction_r{r}_c{c}',[c*1024-128,r*1024-128,c*1024+128,r*1024+128])
 write(qa/'manifest.json',{'tile':ref(out),'nativeCoreContributions':contrib,'nativePixelOperationsOnly':['integer crop','opaque integer paste'],'resized':False,'qa':items,'review':'pending full internal QA'})
 write(Z/'records'/f'{T}.selection-{v}.json',{'tile':T,'patches':{p:ref(Z/'native'/n) for p,n in d.items()},'candidate':ref(out),'status':'pending_internal_and_external_qa'})
 print(json.dumps({'saved':str(out),'sha256':sha(out),'qaCount':len(items)}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('op');a.add_argument('p');a.add_argument('v',nargs='?',default='v1');q=a.parse_args()
 if q.op=='select':select(q.p,q.v)
 elif q.op=='assemble':assemble(q.p)

