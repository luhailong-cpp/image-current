"""Technical provenance/alpha/export audit only. Does not certify animation art or client behavior."""
import hashlib,json,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
rows=[];issues=[];missing=[];rawhash=[];outhash=[];calls=[]
for action,n,ms in [('hit',6,40),('attack',12,30),('cast',16,45)]:
 for direction in ['E','W']:
  sp=R/f'review/combat-{action}-{direction}-selection.json'
  if not sp.exists():missing.append(f'{action}/{direction}');continue
  s=read(sp);assert len(s['frames'])==n and s['timing']['frameDurationsMs']==[ms]*n
  for f in s['frames']:
   try:
    src=R/f['sourcePath'];dst=R/f['path'];sgp=R/f['sourceGenerationRecord'];gp=R/f['generationRecord'];sg=read(sgp);g=read(gp)
    assert sha(src)==f['sourceSha256']==sg['sha256']==g['derivedFrom']['sha256']
    assert sha(dst)==f['sha256']==g['sha256']
    assert sha(sgp)==g['derivedFrom']['generationRecordSha256']
    receiptpath=R/sg['evidence']['receipt'];rec=read(receiptpath);assert sha(receiptpath)==sg['evidence']['receiptSha256']
    assert rec.get('callCount',1)==1 and rec['completedAt'] and rec['submittedParameters']['referenced_image_paths']
    assert sg['actualModel'] is None and sg['actualQuality'] is None
    a=Image.open(src);c=Image.open(dst);assert min(a.size)>=1024 and a.mode=='RGBA' and c.size==(1024,1024) and c.mode=='RGBA'
    assert a.getchannel('A').getextrema()==(0,255) and c.getchannel('A').getextrema()==(0,255)
    assert a.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()==c.tobytes()
    for ref in sg['references']:assert sha(Path(ref['file']))==ref['sha256']
    assert f['durationMs']==ms
    returned=rec.get('output',{}).get('toolReturnedPath')
    if returned is None:
     match=re.search(r'as (C:\\[^\r\n]+?\.png) by default',rec.get('toolResult',{}).get('output_hint',''))
     if match is None:raise ValueError('missing returned tool path evidence')
     returned=match.group(1)
    rawhash.append(sha(src));outhash.append(sha(dst));calls.append(returned)
    rows.append({'action':action,'direction':direction,'frame':f['frame'],'source':f['sourcePath'],'sourceSha256':sha(src),'candidate':f['path'],'candidateSha256':sha(dst),'nativeSize':list(a.size),'durationMs':ms,'technicalPass':True,'actualModel':None,'actualQuality':None})
   except Exception as e:issues.append({'action':action,'direction':direction,'frame':f['frame'],'error':str(e) or repr(e)})
assert len(rawhash)==len(set(rawhash)) and len(outhash)==len(set(outhash)) and len(calls)==len(set(calls))
v={'createdAt':datetime.now(timezone.utc).isoformat(),'expectedSlots':68,'checkedSlots':len(rows),'complete':len(rows)==68 and not missing and not issues,'technicalPassForCheckedSlots':not issues,'missingSegments':missing,'issues':issues,'checks':['native>=1024 RGBA','source and receipt SHA','reference-image SHA','candidate whole-canvas resize pixel identity','true alpha 0..255','independent source/output/tool-path uniqueness','fixed requested combat timing'],'artAcceptance':False,'clientRuntimeVerified':False,'formalExportCount':0,'frames':rows}
(R/'review/combat-technical.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v[k] for k in ['checkedSlots','complete','technicalPassForCheckedSlots','missingSegments','issues']}))
