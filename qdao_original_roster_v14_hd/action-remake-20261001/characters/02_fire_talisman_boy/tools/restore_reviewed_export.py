from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
invpath=R/'inventory-root.json'
inv=json.loads(invpath.read_text(encoding='utf-8'))
restored=[]
for n in [2,3]:
    rp=R/f'records/run-SE-{n:02}-20261003-attempt-04.json'
    rec=json.loads(rp.read_text(encoding='utf-8-sig'))
    p=R/rec['export']['file']; rejected_sha=sha(p)
    im=Image.open(rec['native']['sourceFile'])
    assert sha(Path(rec['native']['sourceFile']))==rec['native']['sha256']
    im.resize((1024,1024),Image.Resampling.LANCZOS).save(p)
    assert sha(p)==rec['export']['sha256']
    item={'frame':n,'original_generation_record':rp.relative_to(R).as_posix(),'restored_sha256':sha(p),'rejected_sha256':rejected_sha,'reason':'attempt20 changed stance/lead leg rather than only shoe yaw; restore independently generated prior correct support candidate. No new AI generation.'}
    restored.append(item)
    for f in inv['frames']:
        if (f['action'],f['direction'],f['frame'])==('run','SE',n):
            f.update(sha256=sha(p),native_evidence=rp.relative_to(R).as_posix(),native_size=[im.width,im.height],visual_status='support_pose_reviewed_sequence_pending')
    side={'file':p.relative_to(R).as_posix(),'sha256':sha(p),'derivedFrom':{'sha256':rec['native']['sha256'],'generationRecord':rp.relative_to(R).as_posix(),'nativeSize':[im.width,im.height]},'operation':'uniform full-canvas downsample to 1024x1024 RGBA; prior support candidate restored after visual rejection of attempt20','actualModel':None,'actualQuality':None}
    p.with_suffix('.png.generation.json').write_text(json.dumps(side,ensure_ascii=False,indent=2),encoding='utf-8')
    rejected=R/f'records/run-SE-{n:02}-20261003-attempt-20.json'
    rr=json.loads(rejected.read_text(encoding='utf-8'));rr.update(status='rejected_after_visual_review',rejectionReason=item['reason'])
    rejected.write_text(json.dumps(rr,ensure_ascii=False,indent=2),encoding='utf-8')
invpath.write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'reviews/restored-support-20261003.json').write_text(json.dumps({'reviewedAt':datetime.now(timezone.utc).isoformat(),'restored':restored},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(restored,ensure_ascii=False))
