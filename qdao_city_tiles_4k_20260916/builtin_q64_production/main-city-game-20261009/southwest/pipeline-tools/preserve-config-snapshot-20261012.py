from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent
src=B/'r09_c06/pipeline/prompts/p03_04.resume-20261012-v01.request.json'
raw=src.read_bytes();d=json.loads(raw.decode('utf-8-sig'));out=B/'pipeline-tools/image-generation.last-request-snapshot-20261012.json'
assert not out.exists()
out.write_text(json.dumps(d['configSnapshot'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
e={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceRequest':str(src),'sourceRequestSha256':hashlib.sha256(raw).hexdigest(),'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'reason':'Original workspace config/image-generation.json absent when preparing p04_01. Preserve exact previous request snapshot for metadata only; no actual model/quality parameter available or changed.','actualModel':None,'actualQuality':None,'originalGlobalConfigModified':False}
out.with_suffix('.provenance.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(e,ensure_ascii=False))
