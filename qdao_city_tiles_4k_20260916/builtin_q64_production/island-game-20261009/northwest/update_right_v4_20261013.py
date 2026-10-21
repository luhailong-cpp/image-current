import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent
fi=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
p=z/'right-current-selection-20261012.json';d=json.loads(p.read_text(encoding='utf-8'));r=d['tiles']['r07_c04']
r.setdefault('candidateHistory',[]).append({'candidate':r['candidate'],'record':r['record'],'status':'superseded_by_local_native_repairs'})
r.update(candidate=fi(z/'tiles/r07_c04_candidate-v4_4096.png'),record=fi(z/'tiles/r07_c04_candidate-v4_4096.native-repair.json'),assembled4k=True,internalClosurePassed=False,formalAccepted=False)
r['nativeReview21']=fi(z/'qa/assembly_r07_c04_candidate-v1_4096/right_native21_review_20261013.json')
r['pendingFindings']=['Wall-foot three boundary notches: r07_c04_wall_foot_boundary_a02 in flight','Lower middle coarse grout blind endpoint: r07_c04_lower_mid_paving_join_a02 in flight','Final changed-crop review and remaining 12 top-bottom native crops pending.']
d['updatedAtUtc']=datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(fi(p))

