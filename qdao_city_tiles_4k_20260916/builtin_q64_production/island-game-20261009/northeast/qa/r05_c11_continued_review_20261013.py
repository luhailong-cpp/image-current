from pathlib import Path
import sys
from PIL import ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
name=sys.argv[1];tid='r05_c11'
d=read(ZONE/'tiles'/f'{name}.png.derivation.json');s=read(ZONE/f'selection-{tid}.json')
assert d['tileId']==tid and sha(d['file'])==d['sha256']
entries=[];stable=read(ZONE/'qa/r05_c11-recovery-stable-crosses/provenance.json')
cross={Path(e['file']).name:e for e in stable['entries']}
for p in sorted(Path(d['inspectionCrops']).glob('*.png')):
 im=Image.open(p).convert('RGB');e={'file':p.as_posix(),'sha256':sha(p),'size':list(im.size),'resized':False,'status':'pending_visual_review'};parts=p.stem.split('-')
 if parts[0]=='core':
  r,c=map(int,parts[1:3]);ident=s['cores'][r-1][c-1];np=ZONE/'native'/f'{ident}.png';j=read(ZONE/'qa'/f'{ident}.joins.json')
  assert sha(np)==j['nativeSha256']
  exact=ImageChops.difference(im,Image.open(np).convert('RGB').crop((115,115,1139,1139))).getbbox() is None
  if exact and j['status'].startswith('passed_'):
   e.update(status='passed_reused_native_review',reuseEvidence={'review':(ZONE/'qa'/f'{ident}.joins.json').as_posix(),'sourceSha256':sha(np),'pixelIdentical':True})
 elif parts[0] in ('vertical','horizontal'):
  i,jj=int(parts[1]),int(parts[3])
  if parts[0]=='vertical':ident=s['cores'][jj-1][i-1];side='right';crop=(128,0,384,1024)
  else:ident=s['cores'][i][jj-1];side='up';crop=(0,128,1024,384)
  jp=ZONE/'qa'/f'{ident}.joins.json';q=read(jp);old=ZONE/'qa'/f'{ident}.{side}.png'
  exact=ImageChops.difference(im,Image.open(old).convert('RGB').crop(crop)).getbbox() is None
  if exact and q['status'].startswith('passed_'):
   e.update(status='passed_reused_identical_join',reuseEvidence={'review':jp.as_posix(),'inspectedImage':old.as_posix(),'inspectedImageSha256':sha(old),'pixelIdentical':True})
 elif p.name in cross:
  old=cross[p.name]
  if e['sha256']==old['sha256'] and old['status'].startswith('passed_'):
   e.update(status='passed_reused_identical_cross',reuseEvidence={'review':(ZONE/'qa/r05_c11-recovery-stable-crosses/provenance.json').as_posix(),'inspectedImage':old['file'],'pixelIdentical':True})
 if p.name=='core-1-4-100pct.png':e.update(status='requires_native_repair',issue='Lantern hard cutoff at tile local x3981 y0..600.')
 if p.name in ('core-3-4-100pct.png','core-4-4-100pct.png'):e.update(status='pending_visual_review',issue='Prior reviewer requested material transition check at tile x3981.')
 entries.append(e)
out=ZONE/'qa'/f'{name}-continued-review-draft.json';assert not out.exists()
write(out,{'tileId':tid,'candidatePath':d['file'],'sha256':d['sha256'],'reviewer':'repair_continued','createdAtUtc':now(),'entries':entries,'formalAccepted':False,'status':'inspection_in_progress'})
print(json.dumps({'file':out.as_posix(),'reused':sum(e['status'].startswith('passed_') for e in entries),'pending':[Path(e['file']).name for e in entries if not e['status'].startswith('passed_')]}))

