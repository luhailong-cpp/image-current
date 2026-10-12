from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
src=Path('C:/Users/luyua/.codex/generated_images/01a12971-38df-7791-a216-b3fcdd2b4460/exec-baf1862d-2dd7-4c7e-ad3c-ccff9729a653.png')
digest=hashlib.sha256(src.read_bytes()).hexdigest();dest=B/'migration-preserved-external-20261011'/(digest+'.png')
if not dest.exists():shutil.copy2(src,dest)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
record={'savedAtUtc':datetime.now(timezone.utc).isoformat(),'preservedBy':'root','sourceCachePath':str(src),'workspaceCopy':str(dest),'sha256':digest,'bytes':src.stat().st_size,'cacheFileMtimeUtc':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'timestampScope':'File mtime only; actual tool return time not inferred.','requestAttribution':'Pending worker final confirmation; do not treat as selected or accepted.','formalAccepted':False,'imageEdited':False,'reason':'Found existing generated image not referenced by any Southwest JSON during migration freeze; preserve original and byte-identical copy.'}
rp=B/'r09_c01/migration-unattributed-cache-return-20261011.json';atomic_json(rp,record)
mp=B/'migration-preserved-external-20261011/manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
entry={'originalExternalPath':str(src),'referencedBy':[str(rp)],'exists':True,'sha256':digest,'bytes':src.stat().st_size,'workspaceCopy':str(dest),'copyVerified':True,'requestAttributionPending':True}
if not any(e['originalExternalPath']==str(src) for e in m['sourceFiles']):m['sourceFiles'].append(entry)
m['uniqueExternalPathCount']=len(m['sourceFiles']);m['unpreservedExternalImages']=[];m['savedAtUtc']=record['savedAtUtc'];atomic_json(mp,m)
print(json.dumps(record,ensure_ascii=False))

