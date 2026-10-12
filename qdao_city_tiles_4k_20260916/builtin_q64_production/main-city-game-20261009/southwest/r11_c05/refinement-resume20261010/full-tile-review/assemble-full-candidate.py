from pathlib import Path
from PIL import Image
import numpy as np
import hashlib,json
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
T=D.parent.parent;R=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def savej(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def saveim(p,a):Image.fromarray(a).save(p,optimize=True);return {'path':str(p),'sha256':sha(p),'pixels':[a.shape[1],a.shape[0]],'resampled':False}
src=T/'pipeline/output/ab61cdcad99521e3/r11_c05.candidate.context.png'
expected='46122d205fd7f331b249cdd74b7a84c8f11d851540d1ac70117f56773e1ec67b'
assert sha(src)==expected
original=np.array(Image.open(src).convert('RGB'));assert original.shape==(4326,4326,3)
row_path=D.parent/'second-row/output/tone-v1/r11-p01-p02.repaired.context.png'
assert sha(row_path)=='3149b7169983dffcbf232acbf77d349eb8822ebed9e7b3d61c716e40f05238c1'
row=np.array(Image.open(row_path).convert('RGB'));assert row.shape==(2278,4326,3)
patch_path=D.parent/'p04_02-local-joint/output/v2/p04_02.joint-fixed.overlay.patch.png'
assert sha(patch_path)=='b28060c26304f52e3f672fe42781e93a42c330b1f450c0112995bfc011ff7528'
patch=np.array(Image.open(patch_path).convert('RGB'));assert patch.shape==(455,530,3)
# Verify the current full context still contains the original isolated p04_02 interior.
source_native=T/'native/p04_02.png';assert sha(source_native)=='77dfdc3a9ab51b9e8a4c8ccfecc04c56302be0a137d4757881509b1f0849720c'
A=np.array(Image.open(source_native).convert('RGB'))
assert np.array_equal(original[3582:4037,1334:1864],A[510:965,310:840])
candidate=original.copy();candidate[:2048]=row[:2048];candidate[3582:4037,1334:1864]=patch
check=candidate.copy();check[:2048]=original[:2048];check[3582:4037,1334:1864]=original[3582:4037,1334:1864];assert np.array_equal(check,original)
assert np.array_equal(candidate[2048:2278],original[2048:2278])
O=D/'output';Q=D/'qa'
O.mkdir(parents=True,exist_ok=True);Q.mkdir(parents=True,exist_ok=True)
core=candidate[115:4211,115:4211]
outputs={'context':saveim(O/'r11_c05.repaired.candidate.context.png',candidate),'core':saveim(O/'r11_c05.repaired.candidate.png',core)}
# Native-size unannotated crops for visual review only.
crops={}
for rr in range(4):
 for cc in range(4):
  box=[cc*1024,rr*1024,(cc+1)*1024,(rr+1)*1024]
  crop=core[box[1]:box[3],box[0]:box[2]]
  name=f'core-r{rr+1}c{cc+1}.png';item=saveim(Q/name,crop);item['coreBox']=box;crops[name]=item
for y in (1024,2048,3072):
 box=[0,y-160,4096,y+160]
 name=f'horizontal-y{y}.png';item=saveim(Q/name,core[y-160:y+160]);item['coreBox']=box;crops[name]=item
for x in (1024,2048,3072):
 box=[x-160,0,x+160,4096]
 name=f'vertical-x{x}.png';item=saveim(Q/name,core[:,x-160:x+160]);item['coreBox']=box;crops[name]=item
# Parent-reported suspicious regions, large enough to follow neighboring complete joints.
for label,box in [('lower-left-joints',[560,2500,1600,3500]),('middle-horizontal',[0,1880,4096,2420]),('row3-left',[0,2048,1600,3072]),('row4-left',[0,3072,1800,4096])]:
 name=label+'.png';item=saveim(Q/name,core[box[1]:box[3],box[0]:box[2]]);item['coreBox']=box;crops[name]=item
inputs={'originalContext':{'path':str(src),'sha256':expected},'approvedTwoRows':{'path':str(row_path),'sha256':sha(row_path)},'jointPatch':{'path':str(patch_path),'sha256':sha(patch_path)}}
manifest={'status':'assembled-awaiting-whole-tile-visual-review','formalAccepted':False,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'inputs':inputs,'appliedOperations':[{'operation':'exact-source-row-copy','sourceContextBox':[0,0,4326,2048],'destinationContextBox':[0,0,4326,2048]},{'operation':'exact-RGB-patch-paste','destinationContextBox':[1334,3582,1864,4037],'sourcePixels':[530,455]}],'sourceDimensions':[4326,4326],'finalCoreBox':[115,115,4211,4211],'tileWorldOrigin':[16384,40960],'outsideTwoAppliedRegionsExact':True,'row2to3Overlap230Preserved':True,'originalSourcesUnmodified':True,'nativeSelectionProgressUnmodified':True,'resampling':False,'newImageGeneration':False,'outputs':outputs,'qaCrops':crops,'script':str(Path(__file__)),'scriptSha256':sha(Path(__file__))}
savej(O/'assembly.json',manifest)
print(json.dumps({'outputs':outputs,'qaDirectory':str(Q),'inputs':inputs},indent=2))

