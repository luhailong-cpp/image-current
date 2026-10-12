from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for d in ['E','W']:
 s=json.loads((R/f'review/run-{d}-selection.json').read_text(encoding='utf-8-sig'))
 for f in s['frames']:
  p=R/f['sourcePath'];out=R/f'candidate/run/{d}/{f["frame"]:02}.png'
  im=Image.open(p).convert('RGBA');target=Image.open(out)
  rec=json.loads((R/f['generationRecord']).read_text(encoding='utf-8-sig'))
  outrec=json.loads(out.with_name(out.name+'.generation.json').read_text(encoding='utf-8-sig'))
  receipt=R/rec['evidence']['receipt'];prompt=R/rec['prompt']
  checks={'nativeAtLeast1024':min(im.size)>=1024,'nativeSHA':sha(p)==f['sha256']==rec['sha256'],'rgba1024':target.mode=='RGBA' and target.size==(1024,1024),'hasTransparency':target.getchannel('A').getextrema()==(0,255),'wholeCanvasExact':target.tobytes()==im.resize((1024,1024),Image.Resampling.LANCZOS).tobytes(),'candidateSHA':sha(out)==outrec['sha256'],'originLink':outrec['derivedFrom']['sha256']==sha(p),'receiptPresent':receipt.exists(),'receiptSHA':sha(receipt)==rec['evidence']['receiptSha256'],'promptPresent':prompt.exists(),'uniform75ms':f['durationMs']==75}
  results.append({'direction':d,'frame':f['frame'],'source':f['sourcePath'],'nativeSHA':sha(p),'candidateSHA':sha(out),'checks':checks,'pass':all(checks.values())})
unique=len({x['nativeSHA'] for x in results})==32 and len({x['candidateSHA'] for x in results})==32
result={'createdAt':datetime.now(timezone.utc).isoformat(),'scope':'E/W only','count':len(results),'allNativeAndCandidateUnique':unique,'pass':len(results)==32 and unique and all(x['pass'] for x in results),'results':results}
(R/'review/run-EW-pairs-technical.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='results'}))
if not result['pass']:raise SystemExit(1)
