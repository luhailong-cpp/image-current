from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
from PIL import Image
R=Path(__file__).resolve().parents[1];S=R.parents[2]/'recovery-20260921'/'14-delivery-preview'/'assets'/'idle'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
xs={'N':510,'NE':502,'E':568,'SE':570,'S':515,'SW':520,'W':520,'NW':570}
rows=[]
for d,x in xs.items():
    src=S/f'{d}.png';dest=R/'support-idle'/f'{d}.png';dest.parent.mkdir(exist_ok=True)
    shutil.copy2(src,dest);original=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8-sig'))
    rec={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'recordedAt':datetime.now(timezone.utc).isoformat(),'width':1024,'height':1024,'mode':'RGBA','derivedFrom':{'file':str(src),'sha256':sha(src),'generationRecord':str(src)+'.generation.json','sourceRecordSnapshot':original},'operation':{'type':'reuse_confirmed_legacy_idle','noPoseSynthesis':True},'review':{'status':'pending_registered_review'},'clientStatus':'not_integrated'}
    Path(str(dest)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    rows.append({'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'srcRoot':[x,942],'basis':'manual anatomical double-support center from fixed full-frame grid; legacy source uses common942 ground','confidence':'manual approx +/-8px'})
reg={'globalScale':.8,'targetRoot':[512,942],'coordinateSpace':'legacy source1024 before common global affine','frames':rows}
(R/'support-idle'/'registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
