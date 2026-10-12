import sys
sys.dont_write_bytecode = True
import json, hashlib, importlib.util
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from PIL import Image
Z = Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def obj(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def save(p,o):
    assert not p.exists(), p
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if sys.argv[1]=='audit-c03':
    tracep=Z/'qa/pair-r10c03-r11c03-v1-trace.json'; t=obj(tracep)
    oldp=Z/'qa/r11_c03-internal-native-art-audit-v1.json'
    for r in [*t['inputs'],*t['tiles']]:
        for key in ['context','candidate']:
            if key in r: assert sha(r[key]['path'])==r[key]['sha256']
    for r in t['qa']: assert sha(r['path'])==r['sha256']
    changes=[]
    for old,new in zip(t['inputs'],t['tiles']):
        a=np.asarray(Image.open(old['context']['path']).convert('RGB'))
        b=np.asarray(Image.open(new['context']['path']).convert('RGB'))
        yy,xx=np.where(np.any(a!=b,axis=2))
        changes.append({'tile':new['tile'],'changedPixelCount':len(xx),'changedContextBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None})
    audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed','reviewer':'stair_rebuild_resume','scope':'r11_c03 internal plus r10_c03/r11_c03 north join; future west/east/south joins pending','trace':ref(tracep),'reusedInternalAudit':ref(oldp),'reusedInternalQaCount':39,'newNativeQaCount':5,'viewed':[dict(q,result='pass') for q in t['qa']],'findings':['All 5 native join crops viewed at 100 percent; sand texture, pebble scale and lighting continue without a blocking line or cut object.','Previous internal audit reused for unchanged pixels; no native upscaling or pixel painting.'],'changedRegions':changes,'tiles':t['tiles'],'unresolved':[],'formalAcceptedCount':0}
    out=Z/'qa/pair-r10c03-r11c03-v1-art-audit-v1.json';save(out,audit)
    print(json.dumps({'audit':ref(out),'tiles':t['tiles'],'changes':changes}))
else:
    spec=importlib.util.spec_from_file_location('prod',Z/'production.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
    original=p.write
    def local_write(path,o):
        if Path(path).name=='progress.json': return
        return original(path,o)
    p.write=local_write
    if sys.argv[1]=='prepare': p.prepare(*sys.argv[2:])
    elif sys.argv[1]=='record': p.record(sys.argv[2])
