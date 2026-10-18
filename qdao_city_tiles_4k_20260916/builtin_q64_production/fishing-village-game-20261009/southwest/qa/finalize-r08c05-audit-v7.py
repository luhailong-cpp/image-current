import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
def ref(p):p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):return np.asarray(Image.open(p).convert('RGB'))
def valid(r):assert ref(r['path'])['sha256']==r['sha256']
tpath=Q/'block2x2-r08r09c05c06-v7-trace.json';t=rd(tpath);v3=rd(Q/'block2x2-r08r09c05c06-v3-trace.json');v1=rd(Q/'block2x2-r08r09c05c06-v1-trace.json');qa=[]
fresh={('east-shared',1),('north-shared',5),('south-shared',1),('central-junction',None)}
for a in t['qa']:
 valid(a);key=(a['edge'],a['part']);prior=next(x for x in v3['qa'] if (x['edge'],x['part'])==key)
 same=a['sha256']==prior['sha256'];method='new native view v7' if key in fresh else 'reused exact v3 pixels'
 assert same or key in fresh
 old=next(x for x in v1['qa'] if (x['edge'],x.get('part'))==key)
 if same and a['sha256']==old['sha256']:method='reused exact v1 native view'
 qa.append(dict(a,result='pass',reviewMethod=method,previousNativeView=prior if same else None))
repairs=rd(Q/'block2x2-r08r09c05c06-v7-final-repair-checks.json')
for a in repairs:valid(a['finalCrop']);a['result']='pass';a['reviewMethod']='reused exact native crop' if a['identicalToAlreadyViewedNativeCrop'] else 'fresh 1254 native view'
boundaries=[]
for tid,source,sides in [('r08_c06','r08c06-south-final-v7-r08_c06-context-native.png',['east']),('r09_c05','pair-r09c05-c06-northupdate-v1-r09_c05-context-native.png',['south','west']),('r09_c06','r08c06-south-final-v7-r09_c06-context-native.png',['south','east'])]:
 tile=next(a for a in t['tiles'] if a['tile']==tid);new=arr(tile['context']['path']);old=arr(Q/source)
 for side in sides:
  box={'east':[3636,0,4326,4326],'south':[0,3636,4326,4326],'west':[0,0,115,4326]}[side];l,top,r,b=box;diff=np.any(new[top:b,l:r]!=old[top:b,l:r],axis=2)
  boundaries.append({'tile':tid,'side':side,'contextBox':box,'priorContext':ref(Q/source),'finalContext':tile['context'],'identical':not bool(diff.any()),'changedPixelCount':int(diff.sum())})
baseaudit=Q/'r08c05-internal-audit-v1.json';base=rd(baseaudit)
allnative=[]
for p in sorted((Q.parent/'native').glob('r08_c05_repair_*.png.generation.json')):
 a=rd(p);valid({'path':a['file'],'sha256':a['sha256']});assert a['width']==1254 and a['height']==1254;allnative.append({'generation':ref(p),'file':{'path':a['file'],'sha256':a['sha256']},'actualModel':a.get('actualModel'),'actualQuality':a.get('actualQuality')})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed_internal_and_four_block_shared_edges','trace':ref(tpath),'tiles':t['tiles'],'r08c05NativeCoverage':'16/16 source cores; all 4096 pixels exact native-source selection','baseInternalAudit':ref(baseaudit),'baseInternalNativeViews':39,'repairNativeChecks':repairs,'sharedEdgeNativeChecks':qa,'outerStableEdgePixelChecks':boundaries,'nativeRepairRecords':allnative,'resolvedDefects':base['knownDefects']+['three stair/parapet joints','water edge rectangle and east bank shade boundary','west wall/post/masonry cross-tile seams','central lamp gold rim and dark post','secondary stair edge and dark post cutoff','small paving zigzag next to central lantern'], 'selectedComposition':'v7 = v3 + s_pavejoint only; v4/v5/v6 mask experiments not selected','rejectedCompositionVersions':['v4: pavement cutoff','v5: red-side color cut','v6: thin silhouette artifacts'],'knownRemainingDefectsInReviewedScope':[],'nativePixelsResampled':False,'sourcePixelIdentity':True,'formalAcceptedCount':0,'runtimeClaims':False,'notYetClaimed':['north edge to row 7','west edge to r08_c04','full-map completion','runtime/navigation validation'],'exportOwnership':'root; this audit does not write index, ledger or progress'}
p=Q/'block2x2-r08r09c05c06-v7-art-audit.json'
with p.open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps({'audit':ref(p),'outerBoundaries':boundaries,'sharedViews':len(qa),'repairViews':len(repairs)}))
