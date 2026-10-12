import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(R/'candidate/manifest.json')
a=np.array(Image.open(m['candidate']))
checks=[];issues=[];coreerrors=[]
for s in m['sources']:
 p=Path(s['path']);g=read(s['generationRecord']);x,y,x2,y2=s['destination']
 exact=np.array_equal(a[y:y2,x:x2],np.array(Image.open(p))[115:1139,115:1139])
 assert exact and Image.open(p).size==(1254,1254) and sha(p)==s['sha256']==g['sha256']
 assert g['actualModel'] is None and g['actualQuality'] is None
 records=[('prompt',g['prompt'],g['promptSha256']),('request',g['evidence']['request'],g['evidence']['requestSha256']),('receipt',g['evidence']['receipt'],g['evidence']['receiptSha256'])]
 for kind,path,expected in records:
  if not Path(path).exists() or sha(path)!=expected: coreerrors.append({'patch':s['patch'],'kind':kind,'path':path})
 refs=[]
 for ref in g['references']:
  pth=Path(ref['path']);present=pth.exists();match=present and sha(pth)==ref['sha256']
  refs.append({'path':str(pth),'recordedSha256':ref['sha256'],'present':present,'matches':match})
  if not match:issues.append({'patch':s['patch'],'path':str(pth),'kind':'historical_reference_unavailable_or_changed','recordedSha256':ref['sha256'],'historyPreserved':True})
 checks.append({'patch':s['patch'],'nativeDimensions':[1254,1254],'sha256':sha(p),'coreExactlyReproduced':exact,'actualModel':None,'actualQuality':None,'refs':refs})
for axis in ['vertical','horizontal']:
 paths=[Path(i['qaNativeStrip']) for i in m['internalSeams'] if i['axis']==axis]
 for j in range(0,len(paths),4):
  out=Image.new('RGB',(1024,1088),'#333333');d=ImageDraw.Draw(out)
  for k,p in enumerate(paths[j:j+4]):
   im=Image.open(p)
   if axis=='vertical':out.paste(im,(k*256,32));d.text((k*256+3,4),p.stem,fill='white')
   else:out.paste(im,(0,k*272+16));d.text((3,k*272),p.stem,fill='white')
  out.save(R/'qa'/f'contact-{axis}-{j//4+1}-native.png')
for row in range(1,4):
 out=Image.new('RGB',(1152,400),'#333333');d=ImageDraw.Draw(out)
 for col in range(1,4):
  p=R/'qa'/f'cross-r{row}c{col}-native.png';out.paste(Image.open(p),((col-1)*384,16));d.text(((col-1)*384+3,0),p.stem,fill='white')
 out.save(R/'qa'/f'contact-cross-row{row}-native.png')
result={'tile':R.name,'createdAt':datetime.now(timezone.utc).isoformat(),'selected':len(checks),'nativeGeneratedCount':len(list((R/'native').glob('*.png'))),'candidateSha256':sha(m['candidate']),'candidateDimensions':[4096,4096],'allCoreCopiesExact':True,'actualModelQualityNull':True,'resizeFinalPixels':False,'mainEvidenceErrors':coreerrors,'historicalReferenceReplayIssues':issues,'checks':checks,'formalAccepted':False,'note':'Historical missing reference evidence remains unchanged; new requests use current contract style. Recorded hashes are never rewritten to match replacements.'}
(R/'candidate/provenance-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','historicalReferenceReplayIssues')},ensure_ascii=False))
print('Historical ref replay issues:',len(issues))

