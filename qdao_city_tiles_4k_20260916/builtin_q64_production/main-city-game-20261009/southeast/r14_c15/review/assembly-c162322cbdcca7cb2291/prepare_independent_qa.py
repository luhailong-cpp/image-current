from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;O=D/'independent-qa-20261012';O.mkdir(exist_ok=True)
def rd(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p),'sha256':sha(p)}
ptr=rd(T/'candidate/latest-assembly.json');north=rd(T.parent/'r13_c15/candidate/latest-assembly.json');west=rd(T.parent/'r14_c14/candidate/latest-assembly.json')
assert ptr['candidate']['sha256']=='e4e2e63caf50abeffcffc2cccb4e38c81128c1bf8699405aa57e17bf466042d6'
assert north['candidate']['sha256'].startswith('173e67') and west['candidate']['sha256'].startswith('66848f')
for a in [ptr['candidate'],ptr['manifest'],north['candidate'],west['candidate']]:assert sha(Path(a['path']))==a['sha256']
im=Image.open(ptr['candidate']['path']).convert('RGB');ni=Image.open(north['candidate']['path']).convert('RGB');wi=Image.open(west['candidate']['path']).convert('RGB')
items=[]
def save(key,image,kind,box,extra=None):
 p=O/(key+'.png')
 with p.open('xb') as f:image.save(f,format='PNG')
 items.append({'id':key,'kind':kind,**art(p),'size':list(image.size),'candidateBox':box,'resized':False,**(extra or {})})
for axis in ['v','h']:
 for seam in [1024,2048,3072]:
  for q in range(4):
   box=[seam-256,q*1024,seam+256,(q+1)*1024] if axis=='v' else [q*1024,seam-256,(q+1)*1024,seam+256]
   save(f'{axis}{seam}-q{q}',im.crop(box),'internal-seam-segment',box)
for y in [1024,2048,3072]:
 for x in [1024,2048,3072]:
  box=[x-450,y-450,x+450,y+450];save(f'j{x}-{y}',im.crop(box),'internal-junction',box)
for edge in ['north','east','south','west']:
 for q in range(4):
  if edge=='north':box=[q*1024,0,(q+1)*1024,256]
  elif edge=='south':box=[q*1024,3840,(q+1)*1024,4096]
  elif edge=='west':box=[0,q*1024,256,(q+1)*1024]
  else:box=[3840,q*1024,4096,(q+1)*1024]
  save(f'edge-{edge}-q{q}',im.crop(box),'candidate-edge-segment',box)
for q in range(4):
 x=q*1024;join=Image.new('RGB',(1024,512));join.paste(ni.crop((x,3840,x+1024,4096)),(0,0));join.paste(im.crop((x,0,x+1024,256)),(0,256));save(f'ext-north-q{q}',join,'external-core-join',[x,0,x+1024,256],{'neighborBox':[x,3840,x+1024,4096],'neighbor':north['candidate'],'seamPixel':256,'seamAxis':'y'})
 y=q*1024;join=Image.new('RGB',(512,1024));join.paste(wi.crop((3840,y,4096,y+1024)),(0,0));join.paste(im.crop((0,y,256,y+1024)),(256,0));save(f'ext-west-q{q}',join,'external-core-join',[0,y,256,y+1024],{'neighborBox':[3840,y,4096,y+1024],'neighbor':west['candidate'],'seamPixel':256,'seamAxis':'x'})
assert len(items)==57
result={'candidate':ptr['candidate'],'assembly':ptr['manifest'],'north':north['candidate'],'west':west['candidate'],'evidence':items,'internalEvidenceCount':49,'externalEvidenceCount':8,'haloUsed':False,'resized':False,'formalAccepted':False}
(O/'index.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'index':art(O/'index.json'),'evidenceCount':len(items)}))

