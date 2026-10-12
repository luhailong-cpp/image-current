from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
D=Path(__file__).resolve().parent;T=D.parents[1];ROOT=T.parent;NAME='r04_c04-pipeline-minimum-error-fbb8f7edb616-fe50f8';Q=T/'qa'/NAME;C=T/'candidate'/(NAME+'.png')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(im,p):
 if p.exists():raise FileExistsError(p)
 im.save(p)
manifest={'candidate':str(C),'candidateSha256':sha(C),'nativePixelScale':1,'resampled':False,'batches':[],'southBoundary':[]}
for axis in ['x','y']:
 for pos in [1024,2048,3072]:
  out=Image.new('RGB',(1024,1384),(25,31,37));dr=ImageDraw.Draw(out);sources=[]
  for i in range(4):
   p=Q/f'internal-{axis}{pos}-segment{i+1:02}.png';im=Image.open(p).convert('RGB');assert im.size==(1024,320);out.paste(im,(0,i*346+26));dr.text((7,i*346+4),p.stem,(255,255,255),font=font);sources.append({'file':str(p),'sha256':sha(p),'pasteXY':[0,i*346+26],'size':list(im.size)})
  p=D/f'batch-internal-{axis}{pos}-native.png';save(out,p);manifest['batches'].append({'file':str(p),'sources':sources})
out=Image.new('RGB',(960,1038),(25,31,37));dr=ImageDraw.Draw(out);sources=[]
for r,y in enumerate([1024,2048,3072]):
 for c,x in enumerate([1024,2048,3072]):
  p=Q/f'junction-x{x}-y{y}.png';im=Image.open(p).convert('RGB');assert im.size==(320,320);out.paste(im,(c*320,r*346+26));dr.text((c*320+4,r*346+4),f'x{x} y{y}',(255,255,255),font=font);sources.append({'file':str(p),'sha256':sha(p),'pasteXY':[c*320,r*346+26],'size':list(im.size)})
p=D/'batch-junctions-native.png';save(out,p);manifest['batches'].append({'file':str(p),'sources':sources})
N=Image.open(C).convert('RGB')
for c in range(1,5):
 sf=ROOT.parent/'northwest/r05_c04/native'/f's01_{c:02}.png';S=Image.open(sf).convert('RGB');assert S.size==(1254,1254);nb=[(c-1)*1024,3776,c*1024,4096];sb=[115,115,1139,435]
 out=Image.new('RGB',(1024,640));out.paste(N.crop(nb),(0,0));out.paste(S.crop(sb),(0,320));p=D/f'external-south-segment{c:02}-native.png';save(out,p)
 manifest['southBoundary'].append({'file':str(p),'sha256':sha(p),'northSource':str(C),'northCrop':nb,'southSource':str(sf),'southSha256':sha(sf),'southCrop':sb,'seamImageY':320,'worldBox':[12288+(c-1)*1024,16064,12288+c*1024,16704],'worldSeamY':16384,'method':'Exact source crop and paste at true world coordinates; no interpolation'})
(D/'review-inputs.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(str(D))
