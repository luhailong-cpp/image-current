"""Validate complete selected-image provenance and actual whole-canvas export pixels."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,traceback
from PIL import Image
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'manifest.json').read_text(encoding='utf-8'));cache={}
def sha(p):
 p=Path(p)
 if str(p) not in cache:cache[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[str(p)]
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
issues=[];rows=[];toolpaths=[];historical_refs=[];historical_index=None
def reference_check(ref,frame):
 global historical_index
 path=Path(ref['file']);current=sha(path)
 if current==ref['sha256']:return
 reference_root=R.parent/'09_bamboo_archer_girl'
 assert path.resolve().is_relative_to(reference_root.resolve()),'Unexpected changed reference '+str(path)
 if historical_index is None:
  historical_index={}
  for record in (reference_root/'provenance').rglob('*.generation.json'):
   old=rd(record)
   if old.get('sha256'):historical_index.setdefault(old['sha256'],record)
 evidence=historical_index.get(ref['sha256'])
 assert evidence,'Historical reference hash has no provenance record: '+ref['sha256']
 saved=R/'sources/reference-history'/(ref['sha256']+'.generation.json')
 saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(evidence.read_bytes())
 historical_refs.append({'frame':frame,'reference':str(path),'recordedSha256':ref['sha256'],'currentSha256':current,'status':'historical_reference_superseded','historicalRecord':saved.relative_to(R).as_posix(),'historicalRecordSha256':sha(saved),'originalRecord':str(evidence),'historicalImageBytesReverified':False})
for s in m['sequences']:
 for f in s['frames']:
  try:
   dst=R/f['path'];dg=rd(R/f['generationRecord']);der=dg['derivedFrom']
   src=R/(der.get('file') or der['path']);sgp=R/der['generationRecord'];sg=rd(sgp)
   assert sha(src)==der['sha256']==sg['sha256']
   assert sha(dst)==f['sha256']==dg['sha256']
   if der.get('generationRecordSha256'):assert sha(sgp)==der['generationRecordSha256']
   receipt=R/sg['evidence']['receipt'];rec=rd(receipt);assert sha(receipt)==sg['evidence']['receiptSha256']
   assert (R/sg['prompt']).is_file()
   assert sg['actualModel'] is None and sg['actualQuality'] is None and sg['generatedAt']
   for ref in sg['references']:reference_check(ref,f['path'])
   original=Image.open(src);exported=Image.open(dst)
   assert min(original.size)>=1024 and original.mode=='RGBA' and exported.mode=='RGBA' and exported.size==(1024,1024)
   assert exported.getchannel('A').getextrema()==(0,255)
   assert original.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()==exported.tobytes()
   returned=rec.get('output',{}).get('toolReturnedPath')
   if not returned:
    hint=rec.get('toolResult',{}).get('output_hint','')
    match=re.search(r'as (C:\\[^\r\n]+?\.png) by default',hint)
    if match:returned=match.group(1)
   if returned:toolpaths.append(returned)
   rows.append({'file':f['path'],'sha256':f['sha256'],'native':src.relative_to(R).as_posix(),'nativeSize':list(original.size),'receipt':receipt.relative_to(R).as_posix(),'passed':True})
  except Exception as e:issues.append({'file':f['path'],'error':str(e) or repr(e),'line':traceback.extract_tb(e.__traceback__)[-1].lineno})
if len(toolpaths)!=len(set(toolpaths)):issues.append({'error':'duplicate tool output paths'})
result={'checkedAt':datetime.now(timezone.utc).isoformat(),'expectedFrames':196,'checked':len(rows),'passed':len(rows)==196 and not issues,'issues':issues,'frames':rows,'historicalReferences':historical_refs,'checks':['PNG/source/receipt SHA','reference SHA or explicit historical provenance for subsequently replaced 09 reference','native>=1024 RGBA','actual model/quality evidence null','exact full-canvas LANCZOS export pixels','output alpha0..255','prompt retained','tool output paths unique when disclosed'],'clientRuntimeVerified':False}
(R/'review/delivery-provenance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['checked','expectedFrames','passed','issues']},ensure_ascii=False))
