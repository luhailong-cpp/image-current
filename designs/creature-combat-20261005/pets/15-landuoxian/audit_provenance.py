from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(value):
 p=Path(value)
 return p if p.is_absolute() else R/p
def main():
 m=json.loads((R/'manifest.json').read_text(encoding='utf-8-sig')); errors=[]; rows=[]
 for f in m['frames']:
  rp=R/f['generationRecord'];r=json.loads(rp.read_text(encoding='utf-8-sig'))
  row={'file':f['file'],'record':f['generationRecord'],'prompt':r.get('prompt'),'actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality'),'sha256':f['sha256']}
  for k in ['configSnapshot','submittedParameters','actualModel','actualQuality','unverifiedReason','prompt','references','evidence','derivedFrom','generatedAt']:
   if k not in r:errors.append({'frame':f['file'],'missingField':k})
  if r.get('sha256')!=sha(R/f['file']):errors.append({'frame':f['file'],'error':'output SHA mismatch'})
  p=resolve(r['prompt'])
  if not p.is_file():errors.append({'frame':f['file'],'error':'missing prompt','path':str(p)})
  ev=r['evidence'];ev=ev.get('receipt') if isinstance(ev,dict) else ev
  if ev and not resolve(ev).is_file():errors.append({'frame':f['file'],'error':'missing receipt','path':ev})
  for ref in r.get('references',[]):
   p=resolve(ref.get('path') or ref.get('file'))
   if not p.is_file():
    if not ref.get('removedAfterProduction'):errors.append({'frame':f['file'],'error':'missing active reference','path':str(p)})
   elif ref.get('sha256') and sha(p)!=ref['sha256']:errors.append({'frame':f['file'],'error':'reference SHA mismatch','path':str(p)})
  native=r['derivedFrom'];native=native[0] if isinstance(native,list) else native
  p=resolve(native.get('file') or native.get('nativeFile'))
  if p.is_file():
   if native.get('sha256') and sha(p)!=native['sha256']:errors.append({'frame':f['file'],'error':'native SHA mismatch'})
  elif not native.get('removedAfterProduction'):errors.append({'frame':f['file'],'error':'native source missing without cleanup record'})
  rows.append(row)
 out={'checkedAt':datetime.now(timezone.utc).isoformat(),'frameCount':len(rows),'status':'passed' if not errors and len(rows)==68 else 'incomplete_or_failed','errors':errors,'frames':rows,'actualModelConfirmedCount':sum(x['actualModel'] is not None for x in rows),'actualQualityConfirmedCount':sum(x['actualQuality'] is not None for x in rows)}
 (R/'provenance-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# 逐图来源索引','','型号目标：GPT Image 2.5 Sunburst / max。内置工具实际型号与质量未披露；以下每张实际值均以记录为准。','','|图片|生成记录|实际型号|实际质量|','|---|---|---|---|']
 lines += [f"|[{x['file']}]({x['file']})|[记录]({x['record']})|{x['actualModel'] or '未确认'}|{x['actualQuality'] or '未确认'}|" for x in rows]
 (R/'PROVENANCE_INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(json.dumps({'frames':len(rows),'errors':errors},ensure_ascii=False))
if __name__=='__main__':main()
