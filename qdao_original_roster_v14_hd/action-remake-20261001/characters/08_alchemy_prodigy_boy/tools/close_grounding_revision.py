"""Record this offline revision. Does not certify game movement or delete images."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
m=read(ROOT/'manifest.json'); profile=read(ROOT/'run-timing.json'); selection=read(ROOT/'grounding-selection.json')
assert len(selection)==34, 'Complete all planned foot-direction edits before final closure'
baseline=read(ROOT/'provenance/grounding-20261003/before-manifest.json')
weight=read(ROOT/'provenance/grounding-20261003/weight-stage-manifest.json')
baseby={f['slot']:f for f in baseline['frames']}; weightby={f['slot']:f for f in weight['frames']}
lineage=[]
records=sorted(p for folder in ['grounding-20261003','bamboo-reference-20261003']
               for p in (ROOT/'generation'/folder).rglob('*.png.generation.json'))
for p in records:
    r=read(p); refs=[]
    for entry in r.get('references',[]):
        file=entry.get('file') or entry.get('path')
        if not file:continue
        q=Path(file)
        if not q.is_absolute():q=ROOT/q
        item={'file':file}
        if entry.get('sha256'):
            item.update({'sha256':entry['sha256'],'evidence':'input hash captured at generation submission'})
        elif q.is_relative_to(ROOT/'runtime'):
            slot=q.relative_to(ROOT/'runtime').with_suffix('').as_posix()
            snap=weightby if slot=='run/E/10' and 'straight' in str(p) else baseby
            item.update({'sha256':snap[slot]['sha256'],'evidence':'historical runtime input snapshot before this edit chain'})
        elif q.is_file():item.update({'sha256':sha(q),'evidence':'file hash before cleanup'})
        else:item['evidence']='See original per-image record; source no longer present'
        refs.append(item)
    lineage.append({'generationRecord':p.relative_to(ROOT).as_posix(),'generationRecordSha256':sha(p),'nativeFile':r.get('file'),'nativeSha256':r.get('sha256'),'references':refs})
write(ROOT/'provenance/grounding-20261003/edit-lineage.json',{'recordedAt':now,'items':lineage})
m['updatedAt']=now
m['timing']['run']={'previewDefaultCycleMs':1200,'previewFrameMs':[75]*16,
 'weightedTiming':False,'timingFile':'run-timing.json','directions':profile['directions'],'clientFinalized':False}
m['groundingRevision']={'date':'2026-10-03','replacedFrames':len(selection),'selection':'grounding-selection.json',
 'footAxisReviewed':True,'uniformFrameMs':75,'offlinePreviewReviewed':True,'clientValidated':False,
 'poseReference':'09_bamboo_archer_girl current runtime; user-approved foot direction and limb mechanics'}
m['offlinePlaybackChecked']=True
m['offlineDynamicAcceptance']='foot-axis revision and uniform 1200ms loop reviewed offline; full game movement not certified'
m['deliveryStatus']='grounding_revision_exported_and_previewed'
m['reviewNotes']=[
 f'{len(selection)} run frames revised. E02/E04-10, NE08/09/16, N04/N11, all16 NW frames, S04/S12 and SW02/06/07.',
 'Compared all eight directions with the user-approved bamboo archer. NW lower-leg/ankle/boot perspective follows NW travel; SW06/07 forward-swing toes corrected from SE to SW. Prop hand ownership preserved.',
 'N11 final v6 support edge is within the projected contact band of its neighbors; previous early floating support corrected.',
 'E/NE hair and torso outlines retain small drawing differences; S12 late toe-off sits about11px above former contact pose.',
 'Browser normal/slow samples and128/256 views checked; no substitute for continuous-game sliding, direction/idle transitions and movement/event validation.'
]
for f in m['frames']:
    if f['slot'].startswith('run/'):
        _,d,n=f['slot'].split('/'); p=profile['directions'][d]
        f['previewDurationMs']=p['frameMs'][int(n)-1];f['phase']=p['phases'][int(n)-1]
        f['offlineFootDirectionReviewed']=True
    else:f['offlineCombatFootDirectionReviewed']=True
    write(ROOT/(f['file']+'.generation.json'),f)
write(ROOT/'manifest.json',m)
report={'reviewedAt':now,'scope':'offline foot-axis correction against bamboo archer and uniform 1200ms playback',
 'replacedSlots':list(selection),'runDirections':list(profile['directions']),
 'combatGroups':['hit/E','hit/W','attack/E','attack/W','cast/E','cast/W'],
 'checks':['All current run contact sheets and changed full-size images inspected','E16 frames independently inspected by a second reviewer','All six combat contact sheets checked for foot direction and prop hand ownership','Browser normal1x and0.25x sampled with128/256 canvases; all14 groups load current1024 images','1200ms uniform75ms arrays and cache-busted preview references validated'],
 'observationLimit':'Screenshots and phase samples are not continuous video or game movement capture.',
 'minorResiduals':[m['reviewNotes'][3]], 'clientValidated':False,
 'timingVerification':'provenance/preview-timing-verification.json',
 'bambooReviewDirectory':'provenance/bamboo-reference-20261003'}
write(ROOT/'provenance/grounding-20261003/review-result.json',report)
print(json.dumps({'replaced':len(selection),'lineageRecords':len(lineage),'frames':len(m['frames'])}))
