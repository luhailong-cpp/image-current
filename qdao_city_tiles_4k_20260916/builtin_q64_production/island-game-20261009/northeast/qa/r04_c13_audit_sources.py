from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(Z/'patch-plan-r04_c13.json')
sel=read(Z/'selection-r04_c13.json')
checks=[]
for line in sel['cores']:
 for ident in line:
  if not ident:continue
  p=Z/'native'/f'{ident}.png'; m=read(p.with_suffix('.png.generation.json')); s=next(x for x in plan['patches'] if x['id']==ident.split('_v')[0]);receipt=read(Path(m['evidence']['receipt']))
  q={'id':ident,'nativeSize':list(Image.open(p).size),'nativeHashMatches':sha(p)==m['sha256'],'coreMatchesPlan':m['coreWorldBox']==s['coreWorldBox'],'worldMatchesPlan':m['nativeWorldBox']==s['nativeWorldBox'],'noUpscaling':not m['finalArtUpscaled'] and not m['resizedAfterGeneration'],'receiptSaved':receipt['imageDataOmitted'],'modelAndQualityUnverified':m['actualModel'] is None and m['actualQuality'] is None,'referenceChecks':[]}
  for ref in m['references']:
   rp=Path(ref['file']);q['referenceChecks'].append({'file':rp.as_posix(),'exists':rp.exists(),'hashMatches':rp.exists() and sha(rp)==ref['sha256']})
  q['passed']=all(q[k] for k in ['nativeHashMatches','coreMatchesPlan','worldMatchesPlan','noUpscaling','receiptSaved','modelAndQualityUnverified']) and q['nativeSize']==[1254,1254] and all(x['hashMatches'] for x in q['referenceChecks'])
  checks.append(q)
report={'tileId':'r04_c13','generatedAtUtc':datetime.now(timezone.utc).isoformat(),'selectedCoreCount':len(checks),'allSelectedSourcesPass':all(x['passed'] for x in checks),'complete16CoreCoverage':len(checks)==16,'checks':checks,'formalAccepted':False}
out=Z/'qa'/'r04_c13-source-audit.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['selectedCoreCount','allSelectedSourcesPass','complete16CoreCoverage']}))

