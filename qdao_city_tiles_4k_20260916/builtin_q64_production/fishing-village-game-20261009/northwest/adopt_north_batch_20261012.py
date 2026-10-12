from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,os,time
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent
O=B/'delivery-2x2/resume-20261012/north-batch-v1';O.mkdir(parents=True,exist_ok=True)
D3=B/'work-r02_c03/resume-20261012-v1/final-v2-verified'
D4=B/'work-r02_c04/resume-20261012-v03'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return {'file':str(p),'sha256':sha(p)}
def checked(rec):
 p=Path(rec['file']);assert sha(p)==rec['sha256'],p
 return p
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
idx=read(B/'current-artifacts.json')
h3=read(D3/'handoff.json');h4=read(D4/'handoff.json')
plans={}
for h in [h3,h4]:
 tile=h['tile'];plans[tile]={'candidate':h['candidate'],'assembly':h['assembly'],'agentQA':ref(D3/'qa-full-internal/coverage-reviewed.json') if tile=='r02_c03' else h4['qa']}
for d in h3['deltas']:
 plans[d['tile']]={'candidate':d['proposal'],'assembly':d['proposalAssembly'],'delta':d['record'],'baseCandidate':d['baseCandidate'],'baseAssembly':d['baseAssembly'],'agentQA':h3['qa']}
d=h4['neighborDelta']
plans['r03_c04']={'candidate':{'file':d['candidate'],'sha256':d['candidateSHA256']},'assembly':{'file':d['assembly'],'sha256':d['assemblySHA256']},'delta':{'file':d['descriptor'],'sha256':d['descriptorSHA256']},'baseCandidate':{'file':str(B/idx['r03_c04']['candidate']),'sha256':d['baseCandidateSHA256']},'agentQA':ref(B/'work-r02_c04/resume-20261012-v02/qa.json')}
if len(sys.argv)>1 and sys.argv[1]=='adopt':
 v=read(O/'verified.json')
 assert read(O/'joint-visual.json')['result']=='pass'
 assert sha(B/'current-artifacts.json')==v['baseIndex']['sha256'],'Index changed since verification'
 wr(O/'current-artifacts.before.json',idx)
 for tile,e in v['tiles'].items():
  checked(e['candidate']);checked(e['normalizedAssembly']);checked(e['agentQA'])
  qa={'coordinate':tile,'candidate':e['candidate'],'internalAccepted':True,'formalAccepted':False,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceProof':e['proof'],'agentEvidence':e['agentQA'],'rootReview':v['rootReview'],'newCombinedJointReview':ref(O/'joint-visual.json'),'priorAcceptedRegionPreserved':e.get('deltaValidation'),'remaining':'unmade exterior neighbors and formal acceptance'}
  qp=O/(tile+'.root-qa.json');wr(qp,qa)
  idx[tile]={'candidate':Path(e['candidate']['file']).relative_to(B).as_posix(),'assembly':Path(e['normalizedAssembly']['file']).relative_to(B).as_posix(),'qa':qp.relative_to(B).as_posix(),'status':'internally-accepted-resume-candidate','formalAccepted':False}
 for tile in ['r02_c02','r02_c05','r06_c04']:
  work='work-'+tile
  if work not in idx['adjacentWork']:idx['adjacentWork'].append(work)
 tmp=O/'current-artifacts.next.json';wr(tmp,idx)
 for attempt in range(5):
  try:os.replace(tmp,B/'current-artifacts.json');break
  except OSError:
   if attempt==4:raise
   time.sleep(.3)
 r=read(B/'production-resume-20261012.json')
 r.update(adopted4kCandidates=10,internallyPassed4kCandidates=10,complete4kCandidatesOnDisk=10,latestAdoption={'batch':str(O/'verified.json'),'tiles':list(v['tiles'])},updatedAtUtc=datetime.now(timezone.utc).isoformat())
 r['completedThisResume']+=['r02_c03 full QA and adoption','r02_c04 full QA and adoption','r03_c02/r03_c03/r03_c04 independent native deltas adopted']
 wr(B/'production-resume-20261012.json',r)
 print(json.dumps({'adopted':list(v['tiles']),'candidates':10,'internal':10,'formal':0}))
 sys.exit()
arrays={};out={}
for tile,e in plans.items():
 cp=checked(e['candidate']);ap=checked(e['assembly']);checked(e['agentQA']);a=read(ap)
 arr=rgb(cp);assert arr.shape==(4096,4096,3)
 mp=checked(a['sourceIdMap']);ids=np.asarray(Image.open(mp));assert ids.shape==(4096,4096)
 sources=list(a['sources'].values()) if isinstance(a['sources'],dict) else a['sources']
 bb=a['globalCoreBox'];covered=np.zeros(ids.shape,bool)
 for s in sources:
  if 'jointSourceId' in s and 'sourceId' in s:s['historicalJointSourceId']=s.pop('jointSourceId')
  sid=s.get('sourceId',s.get('jointSourceId'));s['sourceId']=sid
  yy,xx=np.where(ids==sid)
  if not len(xx):continue
  im=rgb(checked(s));g=s['globalNativeBox'];sx=xx+bb[0]-g[0];sy=yy+bb[1]-g[1]
  assert sx.min()>=0 and sy.min()>=0 and sx.max()<im.shape[1] and sy.max()<im.shape[0]
  assert np.array_equal(arr[yy,xx],im[sy,sx]),(tile,sid)
  covered[yy,xx]=True
 assert covered.all(),tile
 norm={**a,'sources':sources,'metadataNormalization':{'originalAssembly':ref(ap),'changes':'sources dictionary converted to list; any legacy jointSourceId retained as historical metadata; pixel maps and artwork unchanged'},'proof':{'pixels':ids.size,'mismatches':0,'uncovered':0}}
 npth=O/(tile+'.assembly.json');wr(npth,norm)
 rec={**e,'normalizedAssembly':ref(npth),'proof':{'pixels':ids.size,'mismatches':0,'uncovered':0}}
 if 'delta' in e:
  d=read(checked(e['delta']));base=checked(e['baseCandidate'])
  assert sha(B/idx[tile]['candidate'])==e['baseCandidate']['sha256'],tile
  if e.get('baseAssembly'):
   checked(e['baseAssembly']);assert sha(B/idx[tile]['assembly'])==e['baseAssembly']['sha256']
  before=rgb(base);maskrec=d.get('mask',d.get('hardMask'));m=np.asarray(Image.open(checked(maskrec)))==255
  box=d.get('tileDeltaBox',d.get('tileCropBox'));x0,y0,x1,y1=box
  fullmask=np.zeros(ids.shape,bool);fullmask[y0:y1,x0:x1]=m
  diff=np.any(arr!=before,axis=2);assert not (diff & ~fullmask).any()
  payload=rgb(checked(d.get('payload',d.get('rgb'))))
  assert np.array_equal(arr[y0:y1,x0:x1][m],payload[m])
  rec['deltaValidation']={'changedPixels':int(diff.sum()),'outsideMaskChangedPixels':0,'payloadMismatches':0,'base':e['baseCandidate'],'priorQA':ref(B/idx[tile]['qa'])}
 arrays[tile]=arr;out[tile]=rec
# Exact native crops of newly combined proposals, no resizing.
left,right=arrays['r03_c03'],arrays['r03_c04']
Image.fromarray(np.concatenate([left[:1254,-300:],right[:1254,:300]],axis=1)).save(O/'r03-new-deltas-join.100pct.png')
corner=np.concatenate([np.concatenate([arrays['r02_c03'][-300:,-300:],arrays['r02_c04'][-300:,:300]],axis=1),np.concatenate([left[:300,-300:],right[:300,:300]],axis=1)],axis=0)
Image.fromarray(corner).save(O/'four-tile-corner.100pct.png')
wr(O/'verified.json',{'verifiedAtUtc':datetime.now(timezone.utc).isoformat(),'baseIndex':ref(B/'current-artifacts.json'),'tiles':out,'rootReview':{'r02_c03':'Changed wood/paving/roof cores and south roof interface; both neighbor delta boundaries and shared roof circle reviewed at native size. Full internal agent coverage recorded.','r02_c04':'Both paving repairs; four complete south bands and four complete neighbor delta top bands; two foliage repairs and their junctions reviewed at native size. Full internal agent coverage recorded.'},'jointImages':[ref(O/'r03-new-deltas-join.100pct.png'),ref(O/'four-tile-corner.100pct.png')]})
print(json.dumps({'verifiedTiles':list(out),'pixels':len(out)*4096*4096,'mismatches':0,'jointImages':str(O)}))
