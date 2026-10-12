"""Select only explicitly reviewed anatomy edits after a complete preflight."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib
from PIL import Image
B=Path(__file__).resolve().parent.parent
PLAN=B/'review/anatomy-revision-decisions-20261005.json'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(PLAN)
assert plan['status']=='ready_for_selection'
inputs={}; seen=set(); prepared=[]
for item in plan['decisions']:
    key=(item.get('action','run'),item['direction']); slot=item['frame']
    assert (*key,slot) not in seen; seen.add((*key,slot))
    path=B/f'review/{key[0]}-{key[1]}-sequence-input.json'
    data=inputs.setdefault(key,read(path)); f=data['frames'][slot-1]
    old=(B/f['source']).resolve(); expected=(B/item['replaces']).resolve()
    assert old==expected and sha(old)==item['replacesSha256'], (key,slot,'old source changed')
    src=(B/item['source']).resolve(); assert src.is_relative_to(B/'generation')
    meta=read(src.with_name(src.name+'.generation.json'))
    assert sha(src)==meta['sha256']==item['sourceSha256']
    assert (B/item['review']).is_file()
    with Image.open(src) as im:
        assert im.mode=='RGBA' and im.size==(1254,1254)
        bounds=list(im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox())
    assert bounds==meta['alphaGt8Bounds']
    f.update(source=item['source'],sourceSha256=meta['sha256'],sourceGenerationRecord=item['source']+'.generation.json',sourceDimensions=[1254,1254],observedPhase=item['observedPhase'],issues=item.get('issues',[]),durationMs=60 if key[0]=='run' else f['durationMs'])
    for alias in ['alphaGt8Bounds','nativeBoundsAlphaGt8','nativeAlphaGt8Bounds']:
        if alias in f: f[alias]=bounds
    if 'generationRecord' in f: f['generationRecord']=item['source']+'.generation.json'
    for alias in ['review','supportReview']:
        if alias in f: f[alias]=item['review']
    for stale in ['manualContactPointNative','footPoint','diagnosticLowestShoeY','diagnosticFloorClearance']:
        f.pop(stale,None)
    if item.get('contactPointNative'):
        f['manualContactPointNative']=item['contactPointNative']; f['footPoint']=item['contactPointNative']
    prepared.append((src,item))
stamp=datetime.now(ZoneInfo('America/New_York')).isoformat()
for key,data in inputs.items():
    data['updatedAt']=stamp; data['latestAnatomyRevision']=str(PLAN.relative_to(B)).replace('\\','/')
    write(B/f'review/{key[0]}-{key[1]}-sequence-input.json',data)
for src,item in prepared:
    write(src.with_name(src.stem+'.selection-review.json'),dict(item,selectedAt=stamp,status='selected_current_candidate',userAccepted=False,clientAccepted=False))
plan['status']='selected_pending_rebuild'; plan['selectedAt']=stamp
write(PLAN,plan)
print(json.dumps({'selected':len(prepared),'groups':['-'.join(x) for x in inputs]}))
