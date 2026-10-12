from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
Q=T/'qa/full-native-finish-20261013-v1'
manifest=json.loads((Q/'manifest.json').read_text(encoding='utf-8-sig'))
imgs=sorted(Q.glob('p*--p*.png'))+sorted(Q.glob('cross-*.png'))
assert len(imgs)==33
record={'tile':'r14_c10','reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'c10_finish_20261013','selectedCount':16,'geometryPassed':True,'materialDetailPassed':True,'colorPending':True,'internalReady':False,'formalAccepted':False,'method':'All 24 seam strips and 9 crossings directly visually inspected at native 100 percent; overview QA only','observations':'Continuous fine caustic endpoints and broad cyan facets; no land, objects, rectangular density or blank bands; mild RGB joins remain for bounded additive field candidate','candidate':manifest['candidate'],'sources':manifest['sources'],'qaImages':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'geometry':'passed','material':'passed','color':'minor join pending'} for p in imgs]}
out=Q/'native-geometry-review.json';assert not out.exists();out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
backup=T/'native-selected-before-color-finish-v1.json';assert not backup.exists();shutil.copyfile(T/'selected-patches.json',backup)
s=(T.parent/'r13_c08/color_match_tile_resume_v2_20261012.py').read_text(encoding='utf-8-sig')
s=s.replace('native-selected-before-color-v2.json','native-selected-before-color-finish-v1.json').replace('colorpass-resume-20261012-v2','colorpass-finish-20261013-v1').replace('colorpass-selected-resume-20261012-v2.json','colorpass-selected-finish-20261013-v1.json').replace('r13_c08','r14_c10')
dest=T/'color_match_tile_finish_20261013.py';assert not dest.exists();dest.write_text(s,encoding='utf-8')
print(json.dumps({'geometryReview':str(out),'colorScript':str(dest),'QAcount':33}))

