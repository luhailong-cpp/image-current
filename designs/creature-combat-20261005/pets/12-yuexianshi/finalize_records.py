import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def save(p,r):(ROOT/p).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
p='records/root-static-review.json';r=read(p)
r['method']='Each generated single-frame result inspected by its author. Root additionally opened all six exported contact sheets, full W01 and W12 before support correction, corrected W10/W11 and selected W12. No actual playback approval claimed.'
r['attack-W']={'status':'reviewed-static-after-targeted-fixes','notes':'True rear camera and left support/right playing hand retained. Initial10–12 narrower shoe spacing corrected through actual AI edits. Corrected10/11 exported images and selected12 raw/exported images viewed. Lower-body structure and diagonal heels acceptable in static review; small residual center variation remains for playback assessment.','nativeDarkShoeCenters':{'09':[438.5,701.4],'10':[425.3,701.4],'11':[455.0,703.9],'12-selected-root':[439.1,703.0]},'measurementLimit':'Auxiliary dark-shoe pixel centroid at y>=1135, max RGB<185, alpha>150. Static support proxy, not animation or foot-ground contact proof.'}
save(p,r)
p='records/attack-W/12-root-fix.generation.json';r=read(p);r['disposition']='selected native source for runtime/attack/W/12.png';r['replacement']='runtime/attack/W/12.png';save(p,r)
p='records/attack-W/12.candidate-initial.generation.json';r=read(p);r['disposition']='superseded: visible shoe spacing narrowing; replaced by root W09-based AI edit';r['supersededBy']='records/attack-W/12.generation.json';save(p,r)
for p in ['records/attack-W/12.generation.json','records/attack-W/12-root-fix.job.json']:
    r=read(p);r['visualStatus']='reviewed-static: selected W09-based AI edit preserves wider diagonal heel support and independent upper-body return gesture; actual playback pending';r['visualReview']='records/root-static-review.json';save(p,r)
for group in ['hit-E','hit-W']:
    for i in range(1,7):
        p=f'records/{group}/{i:02}.generation.json';r=read(p);r['visualReview']='records/root-static-review.json';save(p,r)
print('Final static review and candidate dispositions updated.')
