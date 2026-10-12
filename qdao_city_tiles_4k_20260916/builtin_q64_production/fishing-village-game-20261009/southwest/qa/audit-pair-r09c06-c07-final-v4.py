import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];Q=Z/'qa';pre='pair-r09c06-c07-final-v4'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
t=rd(Q/(pre+'-trace.json'));b=rd(Path(t['basePairTrace']['path']));out=rgb(Path(t['context']['path']));base=rgb(Path(b['context']['path']))
coverage=np.zeros(out.shape[:2],bool);final=[]
for i,box in [('upper',[3640,500,4894,1754]),('fish',[3620,1500,4874,2754]),('lower',[3650,2940,4904,4194]),('north-halo',[3866,0,4556,300]),('south-halo',[3866,4026,4556,4326])]:
 l,top,r,bottom=box;p=Q/(pre+'-'+i+'-finalcrop-100pct.png')
 if p.exists():assert np.array_equal(rgb(p),out[top:bottom,l:r])
 else:Image.fromarray(out[top:bottom,l:r]).save(p)
 final.append(dict(ref(p),contextBox=box,dimensions=[r-l,bottom-top]));coverage[top:bottom,l:r]=True
for a in t['qa']:
 l,top,r,bottom=a['contextBox'];coverage[top:bottom,l:r]=True
changed=np.any(out!=base,axis=2);assert not changed[~coverage].any()
edge=[]
for i,a in enumerate(t['tiles']):
 old=rgb(Path(t['inputs'][i]['context']['path']));new=rgb(Path(a['context']['path']));d=np.any(old!=new,axis=2);oldqa=np.zeros_like(d);offset=4096*i
 for q in t['qa']+final:
  l,top,r,bottom=q['contextBox'];l=max(l-offset,0);r=min(r-offset,4326)
  if l<r:oldqa[top:bottom,l:r]=True
 assert not d[~oldqa].any()
 ys,xs=np.where(d);edge.append({'tile':a['tile'],'context':a['context'],'changedVsInputPixels':int(d.sum()),'changedBounds':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'north230ChangedPixels':int(d[:230].sum()),'south230ChangedPixels':int(d[-230:].sum()),'west230ChangedPixels':int(d[:,:230].sum()),'east230ChangedPixels':int(d[:,-230:].sum()),'allChangedPixelsCoveredByNativeQA':True})
a={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'all_repair_targets_resolved_pending_root_independent_review','trace':ref(Q/(pre+'-trace.json')),'context':t['context'],'tiles':t['tiles'],'finalCrops':final,'sharedQa':t['qa'],'repairedFindings':[{'id':'upper-beam','result':'jagged vertical beam tone seam removed; polygon stops on beam silhouette'},{'id':'rear-plank','result':'rectangle and horizontal grain discontinuity removed; entire visible rear board area between foreground rail/post/tray/barrel uses native source'},{'id':'red-fish','result':'visible red tail/fin cut-off contours repaired; mutual overlap intact'},{'id':'lower-beam','result':'vertical rectangular fascia color band removed; polygon follows entire visible fascia, excluding foreground post'},{'id':'floor-corner','result':'dangling cut-off grout branch removed, leaving continuous two-way stone corner'}],'watch':[{'location':'shared part01, rear wood above horizontal beam near x400 y450','note':'small dark diagonal facet remains from original pair background outside target beam; no cut object contour, subtle shadow/material transition for independent review'}],'rejectedTrials':[{'prefix':'pair-r09c06-c07-repair-trial-v1','reason':'upper rectangular boundary leaked into rear wood; lower fascia band persisted'},{'prefix':'pair-r09c06-c07-repair-trial-v2','reason':'upper object masks passed, lower v1 fascia band persisted'},{'prefix':'pair-r09c06-c07-final-v3','reason':'new lower fascia native fixed band but rectangular mask nicked foreground post side; v4 object polygon excludes it'}],'edgeImpact':edge,'validation':dict(t['validation'],changedVsPairV1Pixels=int(changed.sum()),allChangedPixelsCoveredByNativeQA=True),'formalAcceptedCount':0,'scope':'internal native art and shared seam QA only'}
p=Q/(pre+'-visual-audit.json');assert not p.exists();p.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({'audit':ref(p),'edgeImpact':edge,'finalCrops':final}))

