"""Inventory actual generation evidence including discarded candidates; never draw frames."""
import json, re, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
R=Path(__file__).resolve().parent
C=json.loads((R.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig'))
previous={}
if (R/'generation-audit.json').is_file():
 for item in json.loads((R/'generation-audit.json').read_text(encoding='utf-8-sig')).get('entries',[]):
  if item.get('nativePath'):
   previous[str(Path(item['nativePath']).resolve()).lower()]=item
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for p in sorted((R/'records').rglob('*.json')):
 try:
  v=json.loads(p.read_text(encoding='utf-8-sig'))
  if isinstance(v,dict) and 'native' in v and 'file' in v and re.fullmatch(r'\d{2}',p.stem):records.append((p,v))
 except Exception:pass
used={str(Path(v['native']['path']).resolve()).lower():p.relative_to(R).as_posix() for p,v in records if isinstance(v.get('native'),dict) and v['native'].get('path')}
entries=[]
for p in sorted((R/'receipts').rglob('*.json')):
 v=json.loads(p.read_text(encoding='utf-8-sig'))
 strings=[]
 def scan(x):
  if isinstance(x,dict):
   for k,y in x.items():
    if k=='output_hint' and isinstance(y,str):strings.append(y)
    else:scan(y)
  elif isinstance(x,list):
   for y in x:scan(y)
 scan(v)
 paths=[v['recoveredNativePath']] if v.get('recoveredNativePath') else []
 for s in strings:
  m=re.search(r' as (.+\.png) by default',s)
  if m:paths.append(m.group(1))
 if not paths:
  entries.append({'receipt':p.relative_to(R).as_posix(),'status':'no_image_returned','error':v.get('error',v.get('result'))})
 for raw in sorted(set(paths)):
  native=Path(raw);key=str(native.resolve()).lower()
  a={'receipt':p.relative_to(R).as_posix(),'nativePath':raw,'status':'selected' if key in used else 'rejected_or_superseded','linkedRecord':used.get(key),'generatedAt':v.get('completedAt',v.get('generatedAt')),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':C,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool did not expose or return model/quality.','retained':native.exists()}
  if native.exists():
   im=Image.open(native);a.update({'sha256':sha(native),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode})
  elif key in previous:
   for field in ['sha256','width','height','format','mode','removedAt','removalReason']:
    if field in previous[key]:a[field]=previous[key][field]
   a['evidenceStatus']='Historical source metadata retained after original pixel cleanup'
  entries.append(a)
unique_selected={str(Path(e['nativePath']).resolve()).lower() for e in entries if e['status']=='selected'}
out={'auditedAt':datetime.now(timezone.utc).isoformat(),'uniqueSelectedImages':len(unique_selected),'receiptEntries':len(entries),'entries':entries,'notes':['Every selected runtime frame has a per-frame record.','Historical and current receipt copies can refer to the same native image; image counts use unique normalized paths.','This ledger also records discarded generated candidates and calls that produced no image.','No actual model/quality is inferred from prompt or configuration.']}
(R/'generation-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'entries':len(entries),'uniqueSelectedImages':len(unique_selected),'otherReceiptEntries':sum(e['status']=='rejected_or_superseded' for e in entries),'failed':sum(e['status']=='no_image_returned' for e in entries)}))
