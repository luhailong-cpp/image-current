from pathlib import Path
from PIL import Image
import json,hashlib,sys
T=Path(__file__).resolve().parents[1];B=T.parent;version=int(sys.argv[1]);D=T/'qa'/f'candidate-v{version}';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=T/'candidate'/f'r05_c11-4096-candidate-v{version}.png';im=Image.open(p);north=B/'r04_c11/candidate/r04_c11-4096-candidate-v3.png';west=B/'r05_c10/candidate/r05_c10-4096-candidate-v2.png';ni=Image.open(north);wi=Image.open(west);crops=[]
def save(name,out,metadata):
 q=D/(name+'.png');out.save(q);crops.append({'file':str(q),'sha256':sha(q),'dimensions':list(out.size),**metadata})
for r in range(1,5):
 for c in range(1,4):
  box=[c*1024-256,(r-1)*1024,c*1024+256,r*1024];save(f'v-p{r}{c}-p{r}{c+1}',im.crop(box),{'tileBox':box,'type':'internal'})
for r in range(1,4):
 for c in range(1,5):
  box=[(c-1)*1024,r*1024-256,c*1024,r*1024+256];save(f'h-p{r}{c}-p{r+1}{c}',im.crop(box),{'tileBox':box,'type':'internal'})
for c in range(1,5):
 x=(c-1)*1024;out=Image.new('RGB',(1024,512));out.paste(ni.crop((x,3840,x+1024,4096)),(0,0));out.paste(im.crop((x,0,x+1024,256)),(0,256));save(f'north-c{c}',out,{'tileBox':[x,0,x+1024,256],'neighborFile':str(north),'neighborCrop':[x,3840,x+1024,4096],'type':'north'})
for r in range(1,5):
 y=(r-1)*1024;out=Image.new('RGB',(512,1024));out.paste(wi.crop((3840,y,4096,y+1024)),(0,0));out.paste(im.crop((0,y,256,y+1024)),(256,0));save(f'west-r{r}',out,{'tileBox':[0,y,256,y+1024],'neighborFile':str(west),'neighborCrop':[3840,y,4096,y+1024],'type':'west'})
manifest={'candidate':str(p),'candidateSha256':sha(p),'north':str(north),'northSha256':sha(north),'west':str(west),'westSha256':sha(west),'cropCount':len(crops),'resampling':False,'crops':crops};(D/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'cropCount':len(crops),'candidateSha256':sha(p)}))
