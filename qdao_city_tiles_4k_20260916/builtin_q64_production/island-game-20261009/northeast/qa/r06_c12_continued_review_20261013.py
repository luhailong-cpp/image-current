from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
from PIL import ImageChops
TID='r06_c12';NAME='r06_c12-continued-v1-20261013';QDIR=ZONE/'qa'/f'{NAME}-final';REVIEW=ZONE/'qa'/f'{NAME}-review.json'
s=read(ZONE/f'selection-{TID}.json');full=Path(s['candidatePath']);d=read(full.with_suffix('.png.derivation.json'));items=[]
def same(a,b):return a.size==b.size and ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
for r,row in enumerate(s['cores'],1):
 for c,i in enumerate(row,1):
  src=ZONE/'native'/f'{i}.png';q=read(ZONE/'qa'/f'{i}.joins.json');p=QDIR/f'core-{r}-{c}-100pct.png'
  assert q['nativeSha256']==sha(src) and q['status']=='passed_native_and_recorded_joins_at100pct'
  assert same(Image.open(p),Image.open(src).crop((115,115,1139,1139)))
  items.append({'file':p.as_posix(),'sha256':sha(p),'kind':'core','status':'passed_reused_exact_native_review','evidence':(ZONE/'qa'/f'{i}.joins.json').as_posix(),'note':q['reviewNote']})
for k in range(1,4):
 for j in range(1,5):
  for direction,i,crop in [('vertical',s['cores'][j-1][k],(128,0,384,1024)),('horizontal',s['cores'][k][j-1],(0,128,1024,384))]:
   p=QDIR/f'{direction}-{k}-segment-{j}-100pct.png';ev=ZONE/'qa'/f'{i}.{"left" if direction=="vertical" else "upper"}.png';q=read(ZONE/'qa'/f'{i}.joins.json')
   assert q['status']=='passed_native_and_recorded_joins_at100pct'
   for n in q['neighbors']:
    assert sha(n['file'])==n['sha256']
    if 'currentFullTileOverride' in n:assert sha(n['currentFullTileOverride']['file'])==n['currentFullTileOverride']['sha256']
   assert same(Image.open(p),Image.open(ev).crop(crop))
   items.append({'file':p.as_posix(),'sha256':sha(p),'kind':'seam','status':'passed_reused_exact_join_review','evidence':ev.as_posix(),'note':'Pixel-identical center crop from previously visually reviewed100pct native join; native hashes unchanged.'})
for r in range(1,4):
 for c in range(1,4):
  p=QDIR/f'cross-{r}-{c}-100pct.png';items.append({'file':p.as_posix(),'sha256':sha(p),'kind':'cross','status':'pending_visual_review'})
up=Path(read(ZONE/'selection-r05_c12.json')['candidatePath']);u=Image.open(up);f=Image.open(full);external=[]
for c,i in enumerate(s['cores'][0]):
 ev=ZONE/'qa'/f'{i}.upper.png';actual=Image.new('RGB',(1024,512));actual.paste(u.crop((c*1024,3840,(c+1)*1024,4096)),(0,0));actual.paste(f.crop((c*1024,0,(c+1)*1024,256)),(0,256));assert same(actual,Image.open(ev))
 external.append({'side':'top','segment':c+1,'status':'passed_reused_exact_boundary_review','evidence':ev.as_posix(),'neighbor':up.as_posix(),'neighborSha256':sha(up),'note':'Exact complete1024 segment from current4096 neighbor and assembled tile matches reviewed native join.'})
record={'tileId':TID,'candidatePath':full.as_posix(),'candidateSha256':sha(full),'sourceCount':16,'coverageSize':[4096,4096],'uncoveredPixels':0,'nativeCoreCount':16,'nativeScale':1,'qaCount':49,'passedCount':40,'pendingCount':9,'failedCount':0,'items':items,'externalBoundary':external,'externalPending':['left r06_c11 native tile unavailable','right r06_c13 native tile unavailable','bottom r07_c12 native tile unavailable'],'internalReview':'pending9cross_visual_review','formalAccepted':False,'actualModel':None,'updatedAtUtc':now()}
assert not REVIEW.exists();write(REVIEW,record);print(json.dumps({'review':REVIEW.as_posix(),'reusedPassed':40,'pending':9,'topSegmentsReused':4}))

