import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
import numpy as np
merge=read(ZONE/'qa/color-repairs-20261011-merge.json');results=[]
for tid in ['r03_c12','r03_c13']:
 p=ZONE/'tiles'/f'{tid}.png';q=read(p.with_suffix('.png.derivation.json'));old=Path(merge['histories'][tid])/f'{tid}.png';a=np.array(Image.open(old).convert('RGB'));b=np.array(Image.open(p).convert('RGB'));mask=np.zeros((4096,4096),dtype=bool)
 for box in ([[2560,2560,3584,3584],[3264,1536,4096,2560]] if tid=='r03_c12' else [[0,1536,1216,2560]]):
  x0,y0,x1,y1=box;mask[y0:y1,x0:x1]=True
 delta=np.any(a!=b,axis=2);assert int(np.count_nonzero(delta&~mask))==0
 replay=Image.new('RGB',(4096,4096))
 for s in q['sources']:
  assert sha(s['file'])==s['sha256'];replay.paste(Image.open(s['file']).crop(tuple(s['coreCrop'])),tuple(s['tileLocalPaste']))
 for s in q['requiredOverlays']:
  assert sha(s['source'])==s['sha256'];replay.paste(Image.open(s['source']).crop(tuple(s['coreCrop'])),tuple(s['tileLocalPaste']))
 assert np.array_equal(np.array(replay),b)
 q.update(status='native_complete_coverage_internal_passed',internalReview='passed: prior whole-tile inspections plus targeted native color repairs; unchanged pixels outside recorded repair rectangles verified',externalSeams='all unchanged tile perimeters retain prior evidence; updated r03_c12/r03_c13 shared edge reviewed at100pct',formalAccepted=False,reviewRecord=(ZONE/'qa'/f'{tid}-color-repairs-20261011-review.json').as_posix(),reviewedAtUtc=now());write(p.with_suffix('.png.derivation.json'),q)
 r={'tileId':tid,'status':'passed_internal_geometry_and_color','file':p.as_posix(),'sha256':sha(p),'size':[4096,4096],'oldFile':old.as_posix(),'oldSha256':sha(old),'historicalQA':merge['histories'][tid]+'/'+tid+'-final','newQA':q['inspectionCrops'],'sourceNativeReplayDifferentPixels':0,'differentPixelsOutsideAuthorizedRepairRectangles':0,'changedPixels':int(delta.sum()),'sourceCoreCount':len(q['sources']),'selectedOverlayCount':len(q['requiredOverlays']),'repairReviewEvidence':['bottle full-height context and4perimeters passed','gourd joint context,6outer perimeter strips,2inner boundaries and2horizontal strips passed'],'independentRootReview':'pending','actualModel':None,'actualQuality':None,'formalAccepted':False,'reviewedAtUtc':now()};write(ZONE/'qa'/f'{tid}-color-repairs-20261011-review.json',r);results.append(r)
out=ZONE/'qa/color-repairs-20261011';out.mkdir(exist_ok=True)
l=Image.open(ZONE/'tiles/r03_c12.png');r=Image.open(ZONE/'tiles/r03_c13.png')
for seg in range(4):
 strip=Image.new('RGB',(512,1024));strip.paste(l.crop((3840,seg*1024,4096,(seg+1)*1024)),(0,0));strip.paste(r.crop((0,seg*1024,256,(seg+1)*1024)),(256,0));strip.save(out/f'updated-shared-border-segment-{seg+1}-100pct.png')
merge.update(status='passed_internal_color_repairs_pending_root_independent_review',completedAtUtc=now(),tiles=results);write(ZONE/'qa/color-repairs-20261011-merge.json',merge)
p=ZONE/'qa/gourd-paint-pair-20261011/review.json';d=read(p);d.update(status='passed_geometry_color_perimeters_and_internal_boundaries',reviewedAtUtc=now(),reviewer='repair_prepare_local direct100pct inspection',formalAccepted=False);write(p,d)
print(json.dumps([{'tileId':x['tileId'],'sha256':x['sha256'],'outsideDifference':0,'replayDifference':0} for x in results]))
