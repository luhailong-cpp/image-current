import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];Q=Z/'qa'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def arr(p):return np.array(Image.open(p).convert('RGB'))
t=rd(Q/'r08c06-south-final-v7-trace.json');p=rd(Q/'r08c06-south-final-v6-trace.json')
ims={k:arr(Path(t[k]['context']['path'])) for k in ['r08_c06','r09_c05','r09_c06','r09_c07']}
assert np.array_equal(ims['r08_c06'][-230:],ims['r09_c06'][:230])
assert np.array_equal(ims['r09_c05'][:,-230:],ims['r09_c06'][:,:230])
assert np.array_equal(ims['r09_c06'][:,-230:],ims['r09_c07'][:,:230])
qa=[]
for a in p['affectedInternalQa']:
 x1,y1,x2,y2=a['coreBox'];cur=ims[a['tile']][y1+115:y2+115,x1+115:x2+115]
 assert np.array_equal(cur,arr(Path(a['path'])))
 qa.append(dict(a,result='passed_native_100pct_visual',samePixelsInFinalV7=True))
joint=np.concatenate([ims['r08_c06'][:4096],ims['r09_c06']])
for i,a in enumerate(p['qa'][:4]):
 x1,y1,x2,y2=a['contextBox'];assert np.array_equal(joint[y1:y2,x1:x2],arr(Path(a['path'])))
 qa.append(dict(a,result='passed_native_100pct_visual_or_exact_inherited_from_south_v5',samePixelsInFinalV7=True))
for a in t['qa']:qa.append(dict(a,result='passed_native_100pct_visual',notes='Lantern ribs, gold cloud ornament, collar, tassel, wall and wood edges continuous; constrained corner seam removes v6 start-row mismatch.'))
base5=arr(Q/'block2x2-r09r10c05c06-v1-r09_c05-context-native.png')
base6=arr(Q/'block2x2-r09r10c06c07-v2-r09_c06-context-native.png')
base7=arr(Q/'block2x2-r09r10c06c07-v2-r09_c07-context-native.png')
assert np.array_equal(ims['r09_c05'][115:4211,115:4211],base5[115:4211,115:4211])
for k,b in [('r09_c05',base5),('r09_c06',base6),('r09_c07',base7)]:assert np.array_equal(ims[k][751:],b[751:])
side=[]
for name,left,right,bl,br in [('west','r09_c05','r09_c06',base5,base6),('east','r09_c06','r09_c07',base6,base7)]:
 cur=np.concatenate([ims[left][:,:4096],ims[right]],axis=1);base=np.concatenate([bl[:,:4096],br],axis=1)
 for y in [915,1715,2515,3311]:
  assert np.array_equal(cur[y:y+900,3866:4556],base[y:y+900,3866:4556]);side.append({'side':name,'contextBox':[3866,y,4556,y+900],'exactLatestApprovedBasePixels':True,'result':'inherited_pass'})
# Revalidate every selected pixel from the recorded source contexts.
l=arr(Q/'r08c06-south-v5-rebased-r09_c06-context-native.png');w=arr(Path(p['r09_c06']['context']['path']));l[:,:230]=w[:,:230]
r=base7;seam=np.array(t['hardSeamPath']);m=np.arange(230)[None,:]<seam[:,None]
over=np.where(m[:,:,None],l[:,-230:],r[:,:230]);expectedL=l.copy();expectedL[:,-230:]=over;expectedR=r.copy();expectedR[:,:230]=over
assert np.array_equal(ims['r09_c06'],expectedL);assert np.array_equal(ims['r09_c07'],expectedR)
north=arr(Q/'pair-r08c06-r09c06-v5-r08_c06-context-native.png');north[4096:]=expectedL[:230];assert np.array_equal(ims['r08_c06'],north)
report={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'art_internal_and_neighbor_seams_passed_pending_root_review_export','tile':'r08_c06','internalBaseQa':ref(Q/'repair-r08_c06-internal-v5-internal-qa.json'),'finalTrace':ref(Q/'r08c06-south-final-v7-trace.json'),'nativeSourcePixelIdentityReverified':True,'noResamplingFeatherPaintingOrColorCorrection':True,'allThree230pxNeighborOverlapsExact':True,'allExistingNeighborsRows751DownExactUnchanged':True,'r09c05CoreExactUnchanged':True,'r09c07ChangedTopLeftCorePixels':int(np.any(ims['r09_c07'][115:4211,115:4211]!=base7[115:4211,115:4211],axis=2).sum()),'visualQa':qa,'sideQaInheritance':side,'westSidePart01':{'file':ref(Q/'pair-r09c05-c06-northupdate-v1-shared-part01-100pct.png'),'result':'passed_native_100pct_visual_prior_to_compaction_exact_unchanged'},'rejectedIntermediate':'final-v6 north corner hard start produced short red lantern rib mismatch; retained as audit only. final-v7 constrained seam passed.','scope':'Artwork and seams only; no runtime/gameplay/capacity certification.','delivery':{k:t[k] for k in ['r08_c06','r09_c05','r09_c06','r09_c07']}}
f=Q/'r08c06-south-final-v7-art-qa.json';assert not f.exists();f.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
h={'createdAtUtc':report['createdAtUtc'],'status':report['status'],'tile':'r08_c06','artQa':ref(f),'finalTrace':report['finalTrace'],'delivery':report['delivery'],'rootAction':'Independently review and versioned export r08_c06 plus revised northern cores of r09_c06 and r09_c07; r09_c05 context halo only. No southern changes.','nextOwnedTile':'r08_c05','nextEastAnchor':t['r08_c06']['context'],'nextSouthAnchor':t['r09_c05']['context']}
f2=Q/'r08c06-south-final-v7-handoff.json';assert not f2.exists();f2.write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8');print(json.dumps({'qa':ref(f),'handoff':ref(f2),'c07ChangedCorePixels':report['r09c07ChangedTopLeftCorePixels']}))

