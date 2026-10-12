from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
q,src,p,out=map(Path,sys.argv[1:5]);r=json.loads(q.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r['prompt']=p.read_text(encoding='utf-8');r['promptFile']=str(p);r['promptSha256']=sha(p)
r['references'][0]={'file':str(src),'sha256':sha(src),'role':'actual native edit target, narrowly scoped geometry correction'}
r['referenced_image_paths'][0]=str(src);r['preparedAtUtc']=datetime.now(timezone.utc).isoformat();r['priorRequest']=str(q);r['priorRequestSha256']=sha(q);r['nativeEditOperation']='scoped native geometry correction, no spatial resampling'
if len(sys.argv)>5:
 r['references']=r['references'][:4];r['referenced_image_paths']=r['referenced_image_paths'][:4]
 guide=Path(sys.argv[5]);r['references'].append({'file':str(guide),'sha256':sha(guide),'role':'exact approved patch guide geometry only; enlarged guide is not final art'});r['referenced_image_paths'].append(str(guide))
assert not out.exists();out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r))
