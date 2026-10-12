from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(__file__).resolve().parents[1];R=B/'review'
# Read current selection only; never mutate selected frame issues during verification.
proof=dict(checkedAt=datetime.datetime.now().astimezone().isoformat(),visualAccepted=False,clientTested=False,directions={})
for dr in ['SE','SW']:
 s=json.loads((R/f'run-{dr}-sequence-input.json').read_text(encoding='utf-8'));fs=s['frames'];assert len(fs)==16 and [x['slot'] for x in fs]==list(range(1,17));assert sum(x['durationMs'] for x in fs)==1200 and all(x['durationMs']==75 for x in fs)
 hashes=[]
 for f in fs:
  path=Path(f['source']);sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==f['sourceSha256'];hashes.append(sha)
  m=json.loads(path.with_name(path.name+'.generation.json').read_text(encoding='utf-8-sig'))
  assert m['sha256']==sha
  assert m['actualModel'] is None and m['actualQuality'] is None
  assert hashlib.sha256((B/m['prompt']).read_bytes()).hexdigest()==m['promptSha256']
  for ref in m['references']:assert hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()==ref['sha256']
  im=Image.open(path);assert im.mode=='RGBA' and im.size==(1254,1254);assert im.getchannel('A').getextrema()==(0,255)
 assert len(set(hashes))==16
 ap=Image.open(R/f'run-{dr}-trial.apng');assert ap.n_frames==16
 ds=[]
 for i in range(ap.n_frames):ap.seek(i);ds.append(ap.info['duration'])
 assert ds==[75.0]*16
 proof['directions'][dr]=dict(frameCount=16,uniqueSourceHashes=16,nativeCanvas=[1254,1254],nativeMode='RGBA',nativeAlpha=[0,255],sourceAndPromptAndReferenceHashesVerified=True,apngFrameCount=16,apngDurationsMs=ds,totalMs=sum(ds))
(R/'run-SE-SW-integrity-check.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False))

