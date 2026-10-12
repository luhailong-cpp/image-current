"""Inspect generated runtime frames and build delivery manifests/contact sheets/previews."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, math
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent
SPECS={'hit':(6,40),'attack':(12,30),'cast':(16,45)}
PHASES={'hit':['ready','impact','recoil-peak','brake','recover','ready-return'],
 'attack':['ready','fold','head-retract','charge','wing-turn','accelerate','impact','follow-through','retract','reopen','rebound','ready-return'],
 'cast':['ready','gather','fold','raise','glimmer','raise-high','arc','charge-peak','press','release','follow-through','fade','lower','head-return','settle','ready-return']}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
groups=[];frames=[];missing=[];problems=[];hashes={};pixels={}
qa=ROOT/'qa'; qa.mkdir(exist_ok=True)
review_path=qa/'visual-review.json'
review=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
reviewed={f['file']:f for f in review.get('frames',[])}
for action,(count,ms) in SPECS.items():
 for direction in ('E','W'):
  group={'action':action,'direction':direction,'durationMs':ms,'expectedFrames':count,'totalDurationMs':count*ms,'frames':[]}
  for index in range(1,count+1):
   rel=f'runtime/{action}/{direction}/{index:02}.png'; p=ROOT/rel
   if not p.exists(): missing.append(rel);continue
   im=Image.open(p); a=im.getchannel('A') if im.mode=='RGBA' else None
   record_path=p.with_suffix('.png.generation.json')
   if not record_path.exists(): record_path=ROOT/f'records/{action}/{direction}/{index:02}.generation.json'
   record=json.loads(record_path.read_text(encoding='utf-8-sig')) if record_path.exists() else {}
   sha=digest(p); ph=hashlib.sha256(im.tobytes()).hexdigest()
   hashes.setdefault(sha,[]).append(rel);pixels.setdefault(ph,[]).append(rel)
   if im.size!=(1024,1024) or im.mode!='RGBA': problems.append({'file':rel,'issue':'size or mode'})
   if a is None or a.getextrema()!=(0,255): problems.append({'file':rel,'issue':'alpha range'})
   if not record: problems.append({'file':rel,'issue':'missing generation record'})
   if record and record.get('sha256')!=sha: problems.append({'file':rel,'issue':'record SHA mismatch'})
   if record and (ROOT/record.get('file','__missing__')).resolve()!=p.resolve(): problems.append({'file':rel,'issue':'record file mismatch'})
   if record and not (ROOT/record.get('prompt','__missing__')).is_file(): problems.append({'file':rel,'issue':'prompt file missing'})
   bbox=a.getbbox() if a else None
   if bbox and (bbox[0]==0 or bbox[1]==0 or bbox[2]==1024 or bbox[3]==1024): problems.append({'file':rel,'issue':'alpha touches canvas edge'})
   source=record.get('derivedFrom') or record.get('source') or record.get('native')
   if isinstance(source,dict) and not (source.get('file') or source.get('path')) and record.get('sourcePath'):
    source={**source,'file':record['sourcePath']}
   reviewed_frame=reviewed.get(rel,{})
   visual_status=reviewed_frame.get('status') if reviewed_frame.get('sha256')==sha else 'requires review of current SHA'
   event=('impact' if action=='attack' and index==7 else 'release' if action=='cast' and index==10 else None)
   frame={'file':rel,'frame':index,'direction':direction,'action':action,'width':im.width,'height':im.height,'durationMs':ms,
    'pivot':[0.5,0.08],'anchorTopLeftPx':[512,942],'anchorType':'virtual hover anchor; not per-frame claw registration',
    'event':event,'phase':PHASES[action][index-1],'sha256':sha,'pixelSHA256':ph,'alphaRange':list(a.getextrema()) if a else None,'alphaBBox':bbox,
    'generationRecord':record_path.relative_to(ROOT).as_posix() if record_path.exists() else None,
    'targetModel':record.get('configSnapshot',{}).get('model'),'actualModel':record.get('actualModel'),'actualQuality':record.get('actualQuality'),
    'source':source,'visualStatus':visual_status,'visualReview':'qa/visual-review.json'}
   frames.append(frame);group['frames'].append(frame)
  groups.append(group)
  # Contact sheets retain every frame at 320px, four columns and up to two rows per page.
  for offset in range(0,len(group['frames']),8):
   chunk=group['frames'][offset:offset+8]; sheet=Image.new('RGB',(1280,math.ceil(len(chunk)/4)*354),(30,43,45));draw=ImageDraw.Draw(sheet)
   for k,f in enumerate(chunk):
    x=(k%4)*320;y=(k//4)*354
    for cy in range(y,y+320,20):
     for cx in range(x,x+320,20):
      draw.rectangle((cx,cy,cx+19,cy+19),fill=(57,68,69) if ((cx-x)//20+(cy-y)//20)%2 else (45,56,57))
    thumb=Image.open(ROOT/f['file']).resize((320,320),Image.Resampling.LANCZOS)
    sheet.paste(thumb,(x,y),thumb)
    draw.text((x+10,y+326),f"{action} {direction} {f['frame']:02} / {count}  {f['phase']}",fill=(240,227,193))
   sheet.save(qa/f'{action}-{direction}-frames-{offset+1:02}-{offset+len(chunk):02}.jpg',quality=94)
duplicates=[v for v in hashes.values() if len(v)>1]; pixel_duplicates=[v for v in pixels.values() if len(v)>1]
review_current=len(frames)==68 and all(reviewed.get(f['file'],{}).get('sha256')==f['sha256'] for f in frames)
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'expected':68,'present':len(frames),'missing':missing,'problems':problems,'duplicateFiles':duplicates,'duplicatePixels':pixel_duplicates,
 'technicalStatus':'passed' if len(frames)==68 and not problems and not duplicates and not pixel_duplicates else 'incomplete-or-failed',
 'artAndMotionStatus':review.get('status') if review_current else 'requires visual review of current files',
 'visualReviewMatchesCurrentSHA':review_current,'visualReview':'qa/visual-review.json',
 'clientStatus':'not read, not integrated, not tested'}
manifest={'schemaVersion':1,'pet':'烛翎','petId':'01-zhuling','createdAt':report['checkedAt'],'expectedFrameCount':68,'presentFrameCount':len(frames),
 'coordinateSystem':'top-left origin image pixels; bottom-left normalized pivot','exportTransform':{'wholeCanvasResize':[820,820],'offset':[102,102],'output':[1024,1024],'perFrameAlignment':False},
 'groups':groups,'frames':frames,'validation':'validation.json','visualQA':'qa/visual-review.json','clientStatus':'not integrated'}
write(ROOT/'manifest.json',manifest);write(ROOT/'validation.json',report)
(ROOT/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['file']}\n" for f in frames),encoding='utf-8')
template=(ROOT/'preview.template.html').read_text(encoding='utf-8')
preview=ROOT/'preview';preview.mkdir(exist_ok=True)
(preview/'index.html').write_text(template.replace('__MANIFEST__',json.dumps(manifest,ensure_ascii=False)),encoding='utf-8')
print(json.dumps({'present':len(frames),'expected':68,'technicalStatus':report['technicalStatus'],'problems':problems},ensure_ascii=False))
