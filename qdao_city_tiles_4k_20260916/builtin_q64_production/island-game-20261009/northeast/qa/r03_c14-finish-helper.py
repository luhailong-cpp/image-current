"""r03_c14 only: exact native crop repair guides and 1:1 overlay inspection."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def current():
 s=read(Z/'selection-r03_c14.json');out=Image.new('RGB',(4096,4096));sources=[]
 for r,line in enumerate(s['cores']):
  for c,ident in enumerate(line):
   assert ident
   p=Z/'native'/f'{ident}.png';d=read(p.with_suffix('.png.generation.json'));assert sha(p)==d['sha256']
   out.paste(Image.open(p).crop((115,115,1139,1139)),(c*1024,r*1024))
   sources.append({'file':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[c*1024,r*1024]})
 for ident in s['overlays']:
  d=read(Z/'qa'/f'{ident}.overlay.json');assert d['review'].startswith('passed_')
  out.paste(Image.open(d['source']).crop(tuple(d['coreCrop'])),tuple(d['tileLocalPaste']));sources.append({'file':d['source'],'sha256':d['sha256'],'generationRecord':d['generationRecord'],'coreCrop':d['coreCrop'],'tileLocalPaste':d['tileLocalPaste']})
 return out,sources
mode,ident=sys.argv[1:3]
assert ident.startswith('r03_c14_')
if mode=='prepare':
 cy,cx=map(int,ident.split('_')[3:5]);x=cx*1024-627;y=cy*1024-627;out,sources=current();box=[x,y,x+1254,y+1254]
 dest=Z/'guides'/f'{ident}.png';assert not dest.exists();out.crop(tuple(box)).save(dest);used=[]
 for s in sources:
  a,b=s['tileLocalPaste'];inter=[max(a,x),max(b,y),min(a+1024,x+1254),min(b+1024,y+1254)]
  if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
  used.append({**s,'sourceCrop':[inter[0]-a+115,inter[1]-b+115,inter[2]-a+115,inter[3]-b+115],'targetPaste':[inter[0]-x,inter[1]-y]})
 replay=Image.new('RGB',(1254,1254))
 for s in used:replay.paste(Image.open(s['file']).crop(tuple(s['sourceCrop'])),tuple(s['targetPaste']))
 assert replay.tobytes()==Image.open(dest).tobytes()
 d={'operation':'exact native core mosaic crop including selected repair overlays in order; no resampling or feathering','file':dest.as_posix(),'sha256':sha(dest),'size':[1254,1254],'tileLocalBox':box,'nativeWorldBox':[53248+x,8192+y,53248+x+1254,8192+y+1254],'coreWorldBox':[53248+x+115,8192+y+115,53248+x+1139,8192+y+1139],'coreCrop':[115,115,1139,1139],'sources':used,'pixelReplayDifference':0,'finalArt':False}
 write(dest.with_suffix('.png.derivation.json'),d)
 refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: exact native four-core junction and all four perimeter anchors; repair center only','derivationRecord':dest.with_suffix('.png.derivation.json').as_posix()},*read(Z/'reference-audit-resumed-20261010.json')['references']]
 write(Z/'prompts'/f'{ident}.inputs.json',refs);print(json.dumps({'guide':dest.as_posix(),'box':box,'sources':len(used)}))
elif mode=='inspect':
 d=read(Z/'guides'/f'{ident}.png.derivation.json');base,sources=current();src=Z/'native'/f'{ident}.png';im=Image.open(src);assert im.size==(1254,1254);x,y=d['tileLocalBox'][:2];a=x+115;b=y+115
 base.paste(im.crop((115,115,1139,1139)),(a,b))
 base.crop((x,y,x+1254,y+1254)).save(Z/'qa'/f'{ident}.overlay-composite-100pct.png')
 crops={'top':(a-115,b-115,a+1139,b+115),'bottom':(a-115,b+909,a+1139,b+1139),'left':(a-115,b-115,a+115,b+1139),'right':(a+909,b-115,a+1139,b+1139),'center':(a+256,b+256,a+768,b+768)}
 evidence=[]
 for name,box in crops.items():
  p=Z/'qa'/f'{ident}.{name}-100pct.png';base.crop(box).save(p);evidence.append(p.as_posix())
 rec={'operation':'exact native1024 repair core overlay; no feathering or scaling','source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[a,b],'worldPaste':[53248+a,8192+b],'review':'pending','reviewerEvidence':evidence}
 write(Z/'qa'/f'{ident}.overlay.json',rec);print(json.dumps(rec))

