from native_work import *
import numpy as np,subprocess,sys
ident='r04_c12_cross_01_02_jar_paint_repair_v4';up='r03_c12_cross_04_02_jar_paint_bridge_v4'
assert read(ZONE/'qa'/f'{ident}.independent-east-audit.json')['status'].startswith('passed')
for oid in [ident,up]:
 p=ZONE/'qa'/f'{oid}.overlay.json';q=read(p);assert sha(q['source'])==q['sha256']
 q.update(review='passed_geometry_color_five_perimeters_root_and_independent',reviewedAtUtc=now(),independentAudit=(ZONE/'qa'/f'{ident}.independent-east-audit.json').as_posix());write(p,q)
p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='usable_native_with_paired_coverage',internalSeams='passed_root_and_independent',externalSeams='five_perimeters_passed',pairedOverlays=[ident,up]);write(p,q)
for old in ['r04_c12_cross_01_02_jar_paint_repair_v2','r04_c12_cross_01_02_jar_paint_repair_v3']:
 p=ZONE/'native'/f'{old}.png.generation.json';q=read(p);q.update(status='rejected_perimeter_color_shift_superseded_v4');write(p,q)
results=[]
for tid,newid,oldid,rect in [('r03_c12',up,'r03_c12_cross_04_02_jar_paint_bridge',[1536,3840,2560,4096]),('r04_c12',ident,'r04_c12_cross_01_02_jar_paint_repair_v2',[1536,0,2560,768])]:
 p=ZONE/'tiles'/f'{tid}.png';oldhash=sha(p);d=read(p.with_suffix('.png.derivation.json'));hist=ZONE/'qa/history'/f'{oldhash[:12]}-{tid}-before-v4';hist.mkdir(exist_ok=True)
 for src in [p,p.with_suffix('.png.derivation.json'),ZONE/f'selection-{tid}.json']:
  dst=hist/src.name
  if not dst.exists():shutil.copy2(src,dst)
 qadir=ZONE/'qa'/f'{tid}-final'
 if not (hist/'final-crops').exists():shutil.copytree(qadir,hist/'final-crops')
 before=np.array(Image.open(p));s=read(ZONE/f'selection-{tid}.json');assert oldid in s['overlays'];s['overlays']=[newid if o==oldid else o for o in s['overlays']];s['updatedAtUtc']=now()
 if 'pendingIssues' in s:
  for issue in s['pendingIssues']:
   if 'paint' in issue.get('subject',''):issue['status']='resolved_by_v4_paired_bridge'
 write(ZONE/f'selection-{tid}.json',s);subprocess.run([sys.executable,str(ZONE/'assemble_tile.py'),tid],check=True)
 n=read(p.with_suffix('.png.derivation.json'));after=np.array(Image.open(p));mask=np.zeros((4096,4096),bool);x0,y0,x1,y1=rect;mask[y0:y1,x0:x1]=True;assert not np.any(np.any(before!=after,axis=2)&~mask)
 replay=Image.new('RGB',(4096,4096))
 for r in n['sources']:
  assert sha(r['file'])==r['sha256'];replay.paste(Image.open(r['file']).crop(r['coreCrop']),r['tileLocalPaste'])
 for r in n['requiredOverlays']:
  assert sha(r['source'])==r['sha256'];replay.paste(Image.open(r['source']).crop(r['coreCrop']),r['tileLocalPaste'])
 assert np.array_equal(np.array(replay),after)
 qa={'tileId':tid,'sha256':sha(p),'size':[4096,4096],'status':'passed_native_replay_pending_final_changed_crop_review','changedRectangle':rect,'pixelDifferenceOutsideChangedRectangle':0,'nativeRebuildDifferencePixels':0,'priorRevision':{'sha256':oldhash,'archive':hist.as_posix()},'newOverlay':newid,'rootAndIndependentPerimeterAudit':(ZONE/'qa'/f'{ident}.independent-east-audit.json').as_posix(),'priorWholeTileEvidence':[(ZONE/'qa/r04_c12-final-seams-source-review.json').as_posix(),(ZONE/'qa/r04_c12-independent-core-cross-review.json').as_posix()] if tid=='r04_c12' else [(ZONE/'qa/history/0405a72d05a7-r03_c12.png.derivation.json').as_posix()],'reviewedAtUtc':now(),'formalAccepted':False,'actualModel':None,'actualQuality':None}
 write(ZONE/'qa'/f'{tid}-v4-bridge-final-review.json',qa);results.append(qa)
print(json.dumps([{'tileId':r['tileId'],'sha256':r['sha256'],'outsideDifference':0,'nativeRebuildDifference':0} for r in results]))

