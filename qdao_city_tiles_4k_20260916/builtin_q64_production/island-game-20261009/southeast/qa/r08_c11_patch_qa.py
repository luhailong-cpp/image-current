from pathlib import Path
from PIL import Image
import json,hashlib,sys,os
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
pid,ver=sys.argv[1:3];sr,sc=int(pid[-2]),int(pid[-1]);file=R/'native'/f'{pid}_{ver}.png';im=Image.open(file).convert('RGB');entries=[]
def actual_neighbor_core(nr,nc,native):
 core=native.crop((115,115,1139,1139));x0=(nc-1)*1024;y0=(nr-1)*1024;sf=R/'selected-overlays-r08_c11.json'
 if sf.exists():
  for z in json.loads(sf.read_text())['overlays']:
   db=z['destinationBox'];scrop=z['sourceCrop'];ix0=max(x0,db[0]);iy0=max(y0,db[1]);ix1=min(x0+1024,db[2]);iy1=min(y0+1024,db[3])
   if ix0>=ix1 or iy0>=iy1:continue
   box=(scrop[0]+ix0-db[0],scrop[1]+iy0-db[1],scrop[0]+ix1-db[0],scrop[1]+iy1-db[1]);core.paste(Image.open(z['file']).convert('RGB').crop(box),(ix0-x0,iy0-y0))
 return core
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,im,desc):
 p=Q/f'{pid}-{ver}-{name}.png';im.save(p);entries.append({'file':str(p),'sha256':sh(p),'composition':desc,'nativeScale':True})
if sr==4:
 lower=Image.open(R/'tiles/r09_c11.candidate-v05.png').convert('RGB');x=(sc-1)*1024;out=Image.new('RGB',(1024,512));out.paste(im.crop((115,883,1139,1139)),(0,0));out.paste(lower.crop((x,0,x+1024,256)),(0,256));save('south',out,'New core bottom256 above final r09c11v05 top256; true boundary y256.')
if sc==4:
 right=Image.open(R/'tiles/r08_c12.candidate-v15.png').convert('RGB');y=(sr-1)*1024;out=Image.new('RGB',(512,1024));out.paste(im.crop((883,115,1139,1139)),(0,0));out.paste(right.crop((0,y,256,y+1024)),(256,0));save('east',out,'New core right256 left of final r08c12v15 left256; true boundary x256.')
if sr==4 and sc==4:
 se=Image.open(R/'tiles/r09_c12.candidate-v09.png').convert('RGB');out=Image.new('RGB',(512,512));out.paste(im.crop((883,883,1139,1139)),(0,0));out.paste(right.crop((0,3840,256,4096)),(256,0));out.paste(lower.crop((3840,0,4096,256)),(0,256));out.paste(se.crop((0,0,256,256)),(256,256));save('four-tile-corner',out,'Actual four candidate/core corners meet at [256,256].')
for neighbor in sys.argv[3:]:
 n=R/'native'/neighbor;a=Image.open(n).convert('RGB');nr,nc=int(neighbor.split('_p')[1][0]),int(neighbor.split('_p')[1][1])
 if nr==sr and nc==sc+1:
  out=Image.new('RGB',(512,1024));out.paste(im.crop((883,115,1139,1139)),(0,0));out.paste(actual_neighbor_core(nr,nc,a).crop((0,0,256,1024)),(256,0));save('right-native',out,'Adjacent original1024 cores with selected native repair overlays at x256, no blend.')
 elif nr==sr+1 and nc==sc:
  out=Image.new('RGB',(1024,512));out.paste(im.crop((115,883,1139,1139)),(0,0));out.paste(actual_neighbor_core(nr,nc,a).crop((0,0,1024,256)),(0,256));save('bottom-native',out,'Adjacent original1024 cores with selected native repair overlays at y256, no blend.')
 else:raise ValueError(neighbor)
(Q/f'{pid}-{ver}-evidence.json').write_text(json.dumps({'native':str(file),'sha256':sh(file),'entries':entries,'formalAccepted':False},indent=2)+'\n')
print(json.dumps(entries,indent=2))
