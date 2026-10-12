from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,importlib.util
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
R=Q.parent
P='capacity-gate-r10c05'
G=R.parents[1]/'capacity-layout-gate-20261010.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj):
 p=Q/(P+name)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return p
def save(name,a):
 p=Q/(P+name);Image.fromarray(a).save(p)
 assert np.array_equal(np.asarray(Image.open(p)),a)
 return {'path':p.as_posix(),'sha256':sha(p),'dimensions':[a.shape[1],a.shape[0]]}
records=[];selected={};errors=[];refchecks=0
for gp in sorted((R/'native').glob('r10_c05_*.png.generation.json')):
 rec=read(gp);p=Path(rec['file'])
 mat=re.fullmatch(r'r10_c05_p(\d+)_(\d+)_v(\d+)\.png',p.name)
 assert mat
 row,col,v=map(int,mat.groups());actual=sha(p);im=Image.open(p)
 checks={'imageHashMatches':actual==rec['sha256'],'nativeDimensions1254':im.size==(1254,1254),'actualModelNull':rec['actualModel'] is None,'actualQualityNull':rec['actualQuality'] is None,'submittedSelectorsNull':rec['submittedParameters']['model'] is None and rec['submittedParameters']['quality'] is None,'promptExists':Path(rec['prompt']).exists(),'receiptExists':Path(rec['evidence']['receipt']).exists(),'referenceHashesMatch':all(Path(x['path']).exists() and sha(x['path'])==x['sha256'] for x in rec['references'])}
 refchecks+=len(rec['references'])
 if not all(checks.values()):errors.append({'file':p.name,'checks':checks})
 item={'slot':f'p{row:02d}_{col:02d}','row':row,'column':col,'version':v,'path':p.as_posix(),'sha256':actual,'size':list(im.size),'record':gp.as_posix(),'recordSha256':sha(gp),'status':rec['status'],'globalCoreBox':rec['coordinates']['globalCoreBox'],'globalContextBox':rec['coordinates']['globalContextBox'],'checks':checks}
 records.append(item)
 if rec['status'] not in ('rejected','superseded','frozen_upstream_geometry_repair') and (row,col) not in selected or (rec['status'] not in ('rejected','superseded','frozen_upstream_geometry_repair') and v>selected[(row,col)]['version']):
  selected[(row,col)]=item
assert sorted(selected)==[(r,c) for r in range(1,4) for c in range(1,5)]
helper=Path(__file__).resolve()
class HardSeam:
 @staticmethod
 def _minimum_vertical_seam(left,right):
  cost=((left.astype(np.float64)-right.astype(np.float64))**2).sum(axis=2)
  height,width=cost.shape;prev=np.zeros((height,width),dtype=np.int16)
  total=cost[0].copy()
  for y in range(1,height):
   choices=np.stack([np.r_[np.inf,total[:-1]],total,np.r_[total[1:],np.inf]])
   choice=choices.argmin(axis=0)
   prev[y]=np.arange(width)+choice-1
   total=cost[y]+choices[choice,np.arange(width)]
  seam=np.zeros(height,dtype=np.int16);seam[-1]=total.argmin()
  for y in range(height-1,0,-1):seam[y-1]=prev[y,seam[y]]
  return seam
h=HardSeam()
rows=[];seams=[]
for r in range(1,4):
 strips=[np.asarray(Image.open(selected[(r,c)]['path']).convert('RGB')) for c in range(1,5)]
 a=strips[0]
 for c,b in enumerate(strips[1:],1):
  s=h._minimum_vertical_seam(a[:,-230:],b[:,:230])
  a=np.concatenate([a[:,:-230],np.where((np.arange(230)[None,:]>=s[:,None])[:,:,None],b[:,:230],a[:,-230:]),b[:,230:]],axis=1)
  seams.append({'row':r,'columnBoundary':c,'axis':'vertical','path':s.tolist()})
 rows.append(a)
a=rows[0]
for r,b in enumerate(rows[1:],1):
 s=h._minimum_vertical_seam(np.transpose(a[-230:],(1,0,2)),np.transpose(b[:230],(1,0,2)))
 a=np.concatenate([a[:-230],np.where((np.arange(230)[:,None]>=s[None,:])[:,:,None],b[:230],a[-230:]),b[230:]],axis=0)
 seams.append({'rowBoundary':r,'axis':'horizontal','path':s.tolist()})
core=a[115:3187,115:4211]
assert core.shape==(3072,4096,3)
out=save('-rows123-native.png',core)
qa=[]
for r in range(3):
 for x in (1024,2048,3072):
  box=[x-320,r*1024,x+320,(r+1)*1024]
  item=save(f'-v{x}-row{r+1}-100pct.png',core[box[1]:box[3],box[0]:box[2]])
  item['coreBox']=box;qa.append(item)
for y in (1024,2048):
 for c in range(4):
  box=[c*1024,y-320,(c+1)*1024,y+320]
  item=save(f'-h{y}-col{c+1}-100pct.png',core[box[1]:box[3],box[0]:box[2]])
  item['coreBox']=box;qa.append(item)
for y in (1024,2048):
 for x in (1024,2048,3072):
  box=[x-384,y-384,x+384,y+384]
  item=save(f'-intersection-{x}-{y}-100pct.png',core[box[1]:box[3],box[0]:box[2]])
  item['coreBox']=box;qa.append(item)
missing=[]
for r in range(1,5):
 for c in range(1,5):
  if (r,c) not in selected:
   stem=f'r10_c05_p{r:02d}_{c:02d}_v1'
   missing.append({'slot':f'p{r:02d}_{c:02d}','requestExists':(R/'native'/(stem+'.request.json')).exists(),'promptExists':(R/'native'/(stem+'.prompt.txt')).exists(),'receiptExists':(R/'native'/(stem+'.receipt.json')).exists(),'pngExists':(R/'native'/(stem+'.png')).exists(),'invocationState':'not_invoked_no_inflight_call'})
unchanged=all(sha(i['path'])==i['sha256'] and sha(i['record'])==i['recordSha256'] for i in records)
audit={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'gate':{'path':G.as_posix(),'sha256':sha(G),'contents':read(G)},'tile':'r10_c05','status':'partial_existing_artwork_capacity_gate_audit_pending_visual_review','counts':{'plannedSlots':16,'slotsWithCurrentCandidate':12,'savedPngAttempts':len(records),'rejectedAttempts':2,'missingSlots':4,'inflightCalls':0,'completeTiles':0},'coverage':{'tileCoreBox':[16384,36864,20480,40960],'existingCoreBox':[16384,36864,20480,39936],'existingCorePixels':4096*3072,'fraction':0.75,'missingCoreBox':[16384,39936,20480,40960],'missingNotFilled':True},'p04_01State':'Only pre-existing request/continuity guide; imagegen was never invoked. No prompt, receipt or PNG. Last completed result is p03_04_v1 and is already saved.','unresolvedInvokedCalls':[],'selectedSlots':[selected[k] for k in sorted(selected)],'allSavedAttempts':records,'missingSlots':missing,'provenance':{'attemptsVerified':len(records),'referenceHashesVerified':refchecks,'errors':errors,'nativeAndRecordHashesUnchanged':unchanged,'actualModel':None,'actualQuality':None},'mechanicalAssembly':{'output':out,'coordinateSpace':'r10_c05 core coordinates; no missing fourth row in output','method':'Minimum squared RGB seam; hard choice of original source pixel only; row-first then top-to-bottom','nativePixelsResampled':False,'noDrawing':True,'noFeather':True,'seams':seams,'helper':{'path':helper.as_posix(),'sha256':sha(helper)},'qa':qa},'findings':[],'capacity5000Validated':False,'acceptance':'Not accepted; capacity gate remains active; fourth row and lower stall are absent; no final game tile exported.'}
write('-audit.json',audit)
print(json.dumps({'output':out,'qaCount':len(qa),'selected':len(selected),'attempts':len(records),'referencesChecked':refchecks,'errors':errors,'unchanged':unchanged}))

