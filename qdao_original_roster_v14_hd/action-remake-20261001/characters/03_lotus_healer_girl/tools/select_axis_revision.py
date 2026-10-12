"""Apply explicitly reviewed local axis revisions, with expected-old-source guards."""
from pathlib import Path
import json, hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(B/'review/axis-revision-decisions-20261004.json')
assert plan['status']=='ready_for_selection'
stamp=datetime.now(ZoneInfo('America/New_York')).isoformat()
inputs={}
for item in plan['decisions']:
    d=item['direction']; data=inputs.setdefault(d,read(B/f'review/run-{d}-sequence-input.json'))
    f=data['frames'][item['frame']-1]
    assert f.get('frame',f.get('slot',item['frame']))==item['frame'] and (B/f['source']).resolve()==(B/item['replaces']).resolve(), (d,f)
    src=B/item['source']; meta=read(src.with_name(src.name+'.generation.json'))
    assert sha(src)==meta['sha256']
    im=Image.open(src); assert im.size==(1254,1254) and im.mode=='RGBA'
    bounds=list(im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox())
    f.update(source=item['source'],sourceSha256=meta['sha256'],sourceGenerationRecord=item['source']+'.generation.json',sourceDimensions=[1254,1254],observedPhase=item['observedPhase'],issues=item['issues'],durationMs=75,alphaGt8Bounds=bounds)
    if 'nativeBoundsAlphaGt8' in f: f['nativeBoundsAlphaGt8']=bounds
    if 'nativeAlphaGt8Bounds' in f: f['nativeAlphaGt8Bounds']=bounds
    if 'generationRecord' in f: f['generationRecord']=item['source']+'.generation.json'
    for key in ['review','supportReview']:
        if key in f: f[key]=item.get('review',str(src.relative_to(B).with_suffix('.selection-review.json')).replace('\\','/'))
    for key in ['manualContactPointNative','footPoint','diagnosticLowestShoeY','diagnosticFloorClearance']:
        f.pop(key,None)
    if item.get('contactPointNative'):
        f['manualContactPointNative']=item['contactPointNative']; f['footPoint']=item['contactPointNative']
    review=dict(item,sourceSha256=meta['sha256'],reviewedAt=stamp,status='selected_current_candidate',userAccepted=False,clientAccepted=False)
    write(src.with_name(src.stem+'.selection-review.json'),review)
for d,data in inputs.items():
    data['updatedAt']=stamp; data['latestAxisRevision']='review/axis-revision-decisions-20261004.json'
    write(B/f'review/run-{d}-sequence-input.json',data)
for item in plan['rejectedAttempts']:
    src=B/item['source']; write(src.with_name(src.stem+'.review.json'),dict(item,status='rejected_not_selected',reviewedAt=stamp))
plan['status']='selected_pending_rebuild'; plan['selectedAt']=stamp
write(B/'review/axis-revision-decisions-20261004.json',plan)
print(json.dumps({'selected':len(plan['decisions']),'directions':list(inputs)}))
