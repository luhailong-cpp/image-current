import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent
Q=Z/'qa/r05_c14-v4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 p=Path(p);assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=json.loads((Q/'manifest.json').read_text())
assert sha(m['candidate']['path'])==m['candidate']['sha256']
im=Image.open(m['candidate']['path']).convert('RGB');assert im.size==(4096,4096)
proof=[]
for s in m['nativeSources']:
 assert sha(s['path'])==s['sha256']
 a=Image.open(s['path']).convert('RGB');assert a.size==(1254,1254)
 assert im.crop(s['pasteAt']).tobytes()==a.crop(s['cropBox']).tobytes()
 proof.append({'patch':s['patch'],'sha256':s['sha256'],'exactCorePixels':True})
checked=[]
for group in ['internalSeams','externalSeams','junctions','externalJunctions','repairCutBoundaries','quadrants']:
 for item in m[group]:
  p=Path(item['path']);assert sha(p)==item['sha256']
  d=json.loads(Path(str(p)+'.derived.json').read_text());actual=Image.open(p).convert('RGB')
  if 'sources' in d:
   rebuilt=Image.new('RGB',actual.size)
   for s in d['sources']:
    assert sha(s['path'])==s['sha256'];rebuilt.paste(Image.open(s['path']).convert('RGB').crop(s['cropBox']),s['pasteAt'][:2])
  else:rebuilt=im.crop(d['cropBox'])
  assert actual.tobytes()==rebuilt.tobytes(),p
  checked.append({'group':group,'path':str(p),'sha256':sha(p),'exactPixelsVerified':True})
coreDir=Q/'central-resume-core-qa';coreDir.mkdir(exist_ok=False)
cores=[]
for r in range(1,5):
 for c in range(1,5):
  box=[(c-1)*1024,(r-1)*1024,c*1024,r*1024];p=coreDir/f'p{r}{c}.png';im.crop(box).save(p)
  cores.append({'path':str(p),'sha256':sha(p),'candidateCrop':box,'resized':False})
write(Q/'central-resume-provenance-20261013.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':m['candidate'],'reviewer':'/root/central_resume','selectedCoreProof':proof,'qaPixelProof':checked,'coreQa':cores,'status':'exact_native_pixels_verified','formalAccepted':False})
print(json.dumps({'sourcesVerified':len(proof),'qaVerified':len(checked),'coresPrepared':len(cores)}))
