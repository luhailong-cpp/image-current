"""Finalize an explicitly reviewed 196-frame snapshot and preserve evidence."""
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
import json,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def scoped(p):
 p=Path(p).resolve()
 if not p.is_relative_to(ROOT) or p==ROOT:raise ValueError('Out of character scope')
 return p
review=read(ROOT/'review/final-visual-review.json')
assert review['offlineAccepted'] is True
m=read(ROOT/'manifest.json')
assert len(m['frames'])==196 and not m['formalAccepted']
before=read(ROOT/'preview/structure-report.json')
assert before['passed'] and before['totalFrames']==196
# Require the accepted snapshot, including late repairs, to match.
assert {f['id']:f['sha256'] for f in m['frames']}==review['acceptedSHA256']
for f in m['frames']:
 assert sha(ROOT/f['path'])==f['sha256'] and sha(ROOT/f['nativePath'])==f['nativeSha256']
write(ROOT/'review/pre-cleanup-structure-report.json',before)
source=scoped(ROOT/'candidate');destination=scoped(ROOT/'frames')
assert source.is_dir() and not destination.exists()
source.rename(destination)
timing=[39,64,64,39,38,38,39,39]*2
assert sum(timing)==720
phases=read(ROOT/'review/run-phase-review.json')['phases']
for f in m['frames']:
 oldNative=ROOT/f['nativePath']
 nativeRec=read(ROOT/f['sourceRecord'].replace('candidate/','frames/',1))['derivedFrom']['generationRecord']
 n=read(nativeRec)
 f['path']=f['path'].replace('candidate/','frames/',1)
 f['sourceRecord']=f['sourceRecord'].replace('candidate/','frames/',1)
 f['nativeProvenance']={'historicalPath':f.pop('nativePath'),'sha256':f.pop('nativeSha256'),'width':1254,'height':1254,'mode':'RGBA','generationRecord':Path(nativeRec).relative_to(ROOT).as_posix(),'disposition':'retained_until_cleanup','verifiedBeforeCleanup':True}
 f['status']='exported';f['visualApproved']=True
 f['visualReviewScope']='offline native/static phases and browser preview; client not tested'
 if f['action']=='run':
  f['durationMs']=timing[f['index']] if f['direction']=='E' else 45
  f['phase']=phases[f['direction']][f['index']]
  f['events']=[f['phase']] if any(x in f['phase'] for x in ('contact','absorb','toe_off')) else []
 rec=read(ROOT/f['sourceRecord'])
 rec['file']=str(ROOT/f['path'])
 rec['derivedFrom']['historicalPath']=rec['derivedFrom'].pop('path')
 rec['derivedFrom']['dimensions']=[1254,1254]
 rec['derivedFrom']['historicalSource']=True
 rec['visualApproved']=True;rec['status']='exported'
 write(ROOT/f['sourceRecord'],rec)
m['updatedAt']=datetime.now(timezone.utc).isoformat()
m['registration'].update({'rootAnchor':[512,968],'rootMeaning':'fixed virtual near-ground origin, manually reviewed with planted-boot regions; perspective feet need not share one y; no pixels repositioned','calibrationRecord':'review/ground-root-review.json','clientCalibration':'not_performed'})
m['timing']={'runCycleMs':720,'E':timing,'otherRunDirections':[45]*16,'hit':40,'attack':30,'cast':45,'scope':'offline delivery proposal; client unmodified','oldRun480Ms':'comparison only'}
m['formalAccepted']=True
m['acceptanceScope']='offline art delivery; not client integration or world-speed sliding acceptance'
m['note']='196 actual independently sourced frames, whole-canvas1254 to1024 export; offline review complete. See MERGE_HANDOFF.md for client limits.'
write(ROOT/'manifest.json',m)
groups=defaultdict(list)
for f in m['frames']:groups[(f['action'],f['direction'])].append(f)
artifacts=[]
for (a,d),group in groups.items():
 group.sort(key=lambda f:f['index']);thumbs=[]
 sheet=Image.new('RGB',(1200,((len(group)+3)//4)*326),'#e5e7eb');draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(group):
  im=Image.open(ROOT/f['path']).resize((300,300),Image.Resampling.LANCZOS)
  bg=Image.new('RGBA',(300,300),'#e5e7eb');bg.alpha_composite(im);thumbs.append(bg.convert('RGB'))
  sheet.paste(thumbs[-1],(i%4*300,i//4*326))
  draw.text((i%4*300+8,i//4*326+302),f"{a}/{d}/{i+1:02}  {f['durationMs']}ms",fill='black')
 sources=[{'path':f['path'],'sha256':f['sha256']} for f in group]
 contact=ROOT/f'preview/{a}-{d}-contact.jpg';sheet.save(contact,quality=90)
 artifacts.append({'path':contact.relative_to(ROOT).as_posix(),'sha256':sha(contact),'sources':sources,'operation':'inspection thumbnails only'})
 for label,mult in [('normal',1),('slow',4)]:
  path=ROOT/f'preview/{a}-{d}-{label}.png'
  durations=[f['durationMs']*mult for f in group]
  thumbs[0].save(path,save_all=True,append_images=thumbs[1:],duration=durations,loop=0)
  artifacts.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'sources':sources,'operation':'300px APNG preview, not game frame','durationsMs':durations})
write(ROOT/'preview/derivations.json',{'artifacts':artifacts})
write(ROOT/'preview/progress.json',{'frames':196,'offlineAccepted':196,'clientIntegrated':0})
(ROOT/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in m['frames']),encoding='utf-8')
print('Finalized196 frames; native images still retained for cleanup gate.')

