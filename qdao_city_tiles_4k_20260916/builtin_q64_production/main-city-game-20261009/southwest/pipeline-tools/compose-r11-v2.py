from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
T=ROOT/'r11_c05/refinement-resume20261010'
D=T/'integrated-v2'
D.mkdir(exist_ok=True)
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
Apath=T/'group-a-geometry/output/assembly.json';Bpath=T/'B-repair/overlay-proposal.json';Cpath=ROOT/'pipeline-tools/c-repair/overlay-proposal.json'
A,B,C=map(rd,[Apath,Bpath,Cpath])
base=Path(A['sourceContext'])
assert sha(base)==A['requiredContextSha256']==B['baseFullContextSha256']==C['sourceSha256']
original=np.array(Image.open(base).convert('RGB'));out=original.copy()
used=np.zeros(out.shape[:2],np.uint8);entries=[]
for group,patches in [(1,A['patches']),(2,B['patches'])]:
 for item in patches:
  for field in ['nativeSource','patch','pasteMask']:assert sha(item[field]['path'])==item[field]['sha256']
  x0,y0,x1,y1=item['contextBox']
  patch=np.array(Image.open(item['patch']['path']).convert('RGB'))
  mask=np.array(Image.open(item['pasteMask']['path']).convert('L'))
  assert set(np.unique(mask)).issubset({0,255}) and patch.shape[:2]==mask.shape==(y1-y0,x1-x0)
  active=mask==255;ownership=used[y0:y1,x0:x1]
  assert not np.any(active & (ownership!=0) & (ownership!=group))
  out[y0:y1,x0:x1][active]=patch[active];ownership[active]=group
  entries.append({'group':group,'id':item['id'],'contextBox':item['contextBox'],'patch':item['patch'],'mask':item['pasteMask'],'nativeSource':item['nativeSource']})
c=C['patch'];assert sha(c['file'])==c['sha256']
x0,y0,x1,y1=c['contextBox'];assert not np.any(used[y0:y1,x0:x1])
out[y0:y1,x0:x1]=np.array(Image.open(c['file']).convert('RGB'));used[y0:y1,x0:x1]=3
entries.append({'group':3,'id':'G06','contextBox':c['contextBox'],'patch':c,'nativeSource':C['outputNative']})
assert np.array_equal(out[used==0],original[used==0])
context=D/'r11_c05.repaired-v2.candidate.context.png';core=D/'r11_c05.repaired-v2.candidate.png'
assert not context.exists() and not core.exists()
Image.fromarray(out).save(context);cropped=Image.fromarray(out).crop((115,115,4211,4211));cropped.save(core)
points={'G01':(930,2795),'G02':(1113,3158),'G03':(1100,3290),'G04':(975,3642),'G05':(1065,4000),'G06':(2118,2165),'G07':(930,2350)}
qa=[]
for name,(x,y) in points.items():
 box=(max(0,x-200),max(0,y-180),min(4096,x+200),min(4096,y+180))
 p=D/(name+'.qa.png');cropped.crop(box).save(p);qa.append({'id':name,'file':str(p),'coreBox':box})
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_full_visual_qa','formalAccepted':False,'sourceContext':{'file':str(base),'sha256':sha(base)},'proposals':[{'file':str(p),'sha256':sha(p)} for p in [Apath,Bpath,Cpath]],'patches':entries,'crossGroupMaskOverlap':0,'outsideMasksExact':True,'sourceResampling':False,'guidePixelsUsed':False,'newImageGeneration':False,'context':{'file':str(context),'sha256':sha(context),'pixels':[4326,4326]},'output':{'file':str(core),'sha256':sha(core),'pixels':[4096,4096]},'qa':qa,'actualModel':None,'actualQuality':None}
(D/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'context':record['context'],'output':record['output'],'manifest':str(D/'assembly.json')}))

