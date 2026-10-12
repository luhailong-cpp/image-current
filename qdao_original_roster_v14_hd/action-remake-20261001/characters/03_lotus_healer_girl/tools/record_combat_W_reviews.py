from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
ROLE=Path(__file__).resolve().parent.parent
observations=json.loads((ROLE/'review/combat-W-observations.json').read_text(encoding='utf8'))
plans=json.loads((ROLE/'review/combat-W-phase-plan.json').read_text(encoding='utf8'))['frames']
for item in observations:
 action=item['action'];frame=item['frame'];stem=f"{frame:02d}-v{item['version']}";folder=ROLE/'generation'/action/'W';png=folder/(stem+'.png')
 im=Image.open(png);a=im.getchannel('A');generation=Path(str(png)+'.generation.json');source=json.loads(generation.read_text(encoding='utf8'));plan=plans[action][frame-1]
 review=dict(item,direction='W',reviewedAtUtc=datetime.now(timezone.utc).isoformat(),file=png.relative_to(ROLE).as_posix(),sha256=hashlib.sha256(png.read_bytes()).hexdigest(),status='candidate_observed_issues_not_accepted',inspection='actual generated full image inspected; saved source hash verified; alpha measurements diagnostic only',intendedPhase=plan['phase'],eventCandidate=plan['event'],durationMs=plan['durationMs'],plannedCycleMs={'hit':240,'attack':360,'cast':720}[action],native=list(im.size),mode=im.mode,alphaExtrema=a.getextrema(),alphaGt8BoundsExclusive=a.point(lambda v:255 if v>8 else 0).getbbox(),alphaGt128BoundsExclusive=a.point(lambda v:255 if v>128 else 0).getbbox(),actualModel=None,actualQuality=None,clientAcceptance='not_performed',dynamicAcceptance=False,visualAccepted=False,pixelsModifiedByReview=False)
 rp=png.with_suffix('.review.json');rp.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf8')
 source.update(status=review['status'],reviewFile=rp.relative_to(ROLE).as_posix(),action=action,direction='W',frame=frame,operation='one independent native AI pose generation/edit; no programmatic frame transform')
 generation.write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'reviewed':len(observations),'PNGModified':False}))

