from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sources=[];gifs=[]
for p in sorted((ROOT/'preview/qa').glob('*-preview.sources.json')):
 d=json.loads(p.read_text(encoding='utf-8-sig'))
 assert d['complete'],str(p)
 for row in d['sources']:
  assert hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()==row['sha256'],row['file']
  sources.append(row['file'])
 name=p.name.replace('-preview.sources.json','');action=name.split('-')[0]
 count=16 if action in ['run','cast'] else 12 if action=='attack' else 6
 frameMs={'run':75,'cast':45,'attack':30,'hit':40}[action]
 for speed,mult in [('normal',1),('slow',4)]:
  gp=p.with_name(name+'-'+speed+('.apng' if action=='run' else '.gif'))
  with Image.open(gp) as im:
   durations=[]
   for i in range(im.n_frames):im.seek(i);durations.append(im.info['duration'])
   assert len(durations)==count and sum(durations)==count*frameMs*mult,(str(gp),durations)
  if action=='run':assert durations==[75*mult]*16,durations
  gifs.append({'file':gp.relative_to(ROOT).as_posix(),'frames':len(durations),'cycleMs':sum(durations)})
assert len(sources)==196 and len(set(sources))==196
overview=json.loads((ROOT/'preview/qa/run-eight-directions.sources.json').read_text())
for row in overview['sources']:assert hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()==row['sha256']
assert sum(overview['durationsMs'])==1200 and len(overview['sources'])==128
paired=0
for p in sorted((ROOT/'preview/qa').glob('*-paired-contact.sources.json')):
 rows=json.loads(p.read_text())['sources']
 assert len(rows)==16
 for row in rows:assert hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()==row['sha256']
 paired+=1
assert paired==8
out={'currentSourceReferences':196,'sourceHashMatches':True,'previewGifChecks':gifs,'eightDirectionOverviewCurrent':True,'dynamicVisualApproval':False}
(ROOT/'audit/preview-delivery-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'currentSourceReferences':196,'normalAndSlowAnimationsVerified':len(gifs),'eightDirectionOverviewCurrent':True,'dynamicVisualApproval':False}))
