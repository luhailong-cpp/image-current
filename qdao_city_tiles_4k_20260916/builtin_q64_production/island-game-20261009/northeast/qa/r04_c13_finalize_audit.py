from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sel=read(Z/'selection-r04_c13.json'); tile=Z/'tiles/r04_c13.png'; final=Image.open(tile).convert('RGB'); rebuilt=Image.new('RGB',(4096,4096));checks=[]
for r,line in enumerate(sel['cores']):
 for c,pid in enumerate(line):
  p=Z/'native'/f'{pid}.png';m=read(p.with_suffix('.png.generation.json'))
  rebuilt.paste(Image.open(p).crop(tuple(m['coreCrop'])),(c*1024,r*1024))
for oid in sel['overlays']:
 q=read(Z/'qa'/f'{oid}.overlay.json'); p=Path(q['source']); m=read(p.with_suffix('.png.generation.json')); receipt=read(m['evidence']['receipt'])
 refs=all(Path(x['file']).exists() and sha(x['file'])==x['sha256'] for x in m['references'])
 ok=sha(p)==q['sha256']==m['sha256'] and Image.open(p).size==(1254,1254) and refs and m['actualModel'] is None and m['actualQuality'] is None and not m['resizedAfterGeneration'] and not m['finalArtUpscaled'] and bool(receipt)
 checks.append({'id':oid,'hash':sha(p),'passed':ok,'referenceHashesMatch':refs})
 rebuilt.paste(Image.open(p).crop(tuple(q['coreCrop'])),tuple(q['tileLocalPaste']))
equal=rebuilt.tobytes()==final.tobytes()
borders=[]
for tid,side in [('r04_c12','left'),('r03_c13','top')]:
 p=Z/'tiles'/f'{tid}.png';m=read(p.with_suffix('.png.derivation.json'));assert sha(p)==m['sha256'];other=Image.open(p).convert('RGB')
 out=Image.new('RGB',(512,4096) if side=='left' else (4096,512))
 if side=='left':
  out.paste(other.crop((3840,0,4096,4096)),(0,0));out.paste(final.crop((0,0,256,4096)),(256,0))
 else:
  out.paste(other.crop((0,3840,4096,4096)),(0,0));out.paste(final.crop((0,0,4096,256)),(0,256))
 paths=[]
 for i in range(4):
  q=Z/'qa'/f'r04_c13-external-{side}-{i+1}-100pct.png';out.crop((0,i*1024,512,(i+1)*1024) if side=='left' else (i*1024,0,(i+1)*1024,512)).save(q);paths.append(q.as_posix())
 for i in range(1,4):out.crop((0,i*1024-256,512,i*1024+256) if side=='left' else (i*1024-256,0,i*1024+256,512)).save(Z/'qa'/f'r04_c13-external-{side}-cross-{i}-100pct.png')
 borders.append({'side':side,'neighbor':tid,'neighborSHA256':sha(p),'tileSHA256':sha(tile),'segments':paths,'status':'pending_visual_review'})
corner=Image.new('RGB',(512,512))
for tid,box,at in [('r03_c12',(3840,3840,4096,4096),(0,0)),('r03_c13',(0,3840,256,4096),(256,0)),('r04_c12',(3840,0,4096,256),(0,256)),('r04_c13',(0,0,256,256),(256,256))]:corner.paste(Image.open(Z/'tiles'/f'{tid}.png').crop(box),at)
corner.save(Z/'qa'/'r04_c13-external-top-left-cross-100pct.png')
final.crop((512,2432,1536,2688)).save(Z/'qa'/'r04_c13-adjacent-overlays-100pct.png')
report={'tileId':'r04_c13','generatedAtUtc':datetime.now(timezone.utc).isoformat(),'file':tile.as_posix(),'sha256':sha(tile),'size':list(final.size),'rebuiltPixelExact':equal,'overlaySourceChecks':checks,'allOverlaySourcesPass':all(x['passed'] for x in checks),'baseSourceAudit':(Z/'qa/r04_c13-source-audit.json').as_posix(),'externalBorders':borders,'formalAccepted':False,'actualModel':None,'actualQuality':None,'finalArtUpscaled':False,'resampling':'none; exact native1024 crops pasted'}
(Z/'qa/r04_c13-final-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['sha256','size','rebuiltPixelExact','allOverlaySourcesPass']}))

