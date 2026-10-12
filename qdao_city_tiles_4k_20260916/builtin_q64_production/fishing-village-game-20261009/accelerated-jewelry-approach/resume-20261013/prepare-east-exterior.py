from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1];d=b/'resume-20261013/east-r05-c11-c12';d.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
own=b/'r05_c11/candidate/r05_c11-4096-candidate-v4.png';z=b.parent/'northeast';progress=z/'progress.json';p=read(progress);active=p['activeCandidates']['r05_c12'];neighbor=Path(active['path'])
assert sha(neighbor)==active['sha256'];a=Image.open(own).convert('RGB');n=Image.open(neighbor).convert('RGB');assert a.size==n.size==(4096,4096)
pair=Image.new('RGB',(8192,4096));pair.paste(a,(0,0));pair.paste(n,(4096,0))
rows=[]
for y in range(0,4096,1024):
 box=[3840,y,4352,y+1024];f=d/f'east-r{y//1024+1}.png';assert not f.exists();pair.crop(box).save(f);rows.append({'file':str(f),'sha256':sha(f),'dimensions':[512,1024],'combinedTileBox':box,'seamImageX':256})
for y in [0,512,1024]:
 f=d/f'roof-context-y{y}.png';box=[3584,y,4608,y+1024];assert not f.exists();pair.crop(box).save(f);rows.append({'file':str(f),'sha256':sha(f),'dimensions':[1024,1024],'combinedTileBox':box,'seamImageX':512})
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Read-only native combined exterior boundary; pixels from neighbor never modified.','own':{'file':str(own),'sha256':sha(own)},'neighbor':{'file':str(neighbor),'sha256':sha(neighbor),'activeReference':str(progress),'activeReferenceSha256AtRead':sha(progress),'selection':active.get('selection'),'reviewStatusAtRead':active.get('reviewStatus')},'nativePixelsResized':False,'files':rows,'visualReview':'pending'}
(d/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report['neighbor']))
