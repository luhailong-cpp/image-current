import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
for d in ('SE','SW'):
 p=R/'review/run-diagonal'/f'{d}-selection.json'
 m=json.loads(p.read_text(encoding='utf8'))
 m['staticReview']='all_outputs_viewed; exactly_two_hands_and_daggers; sequence pending root review'
 m['phaseReview']='review/run-diagonal/REVIEW.md'
 m['reviewedAt']=datetime.now(timezone.utc).isoformat()
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
 pic=p.with_name(f'{d}-contact.jpg')
 record={'file':str(pic),'sha256':hashlib.sha256(pic.read_bytes()).hexdigest(),'operation':'4-column 300px whole-canvas Lanczos thumbnails alpha-composited on grey, labels; review-only derivative, no AI generation','derivedFrom':m['frames'],'actualModel':None,'actualQuality':None,'evidence':'Per-source PNG generation sidecars','createdAt':datetime.now(timezone.utc).isoformat()}
 Path(str(pic)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print('Recorded 32 static reviewed candidates and two review-derived sheets')

