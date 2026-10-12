from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(T/'colorpass-selected-finish-20261013-v1.json')
proof=[]; assembled=np.zeros((4096,4096,3),np.uint8)
for s,o in zip(m['sources'],m['outputRecords']):
 assert sha(s['file'])==s['sha256'] and sha(o['file'])==o['sha256']
 d=read(o['record']); e=d['correctionEvidence']; assert sha(e['file'])==e['sha256']
 a=np.array(Image.open(s['file']).convert('RGB'),dtype=np.float32)
 n=np.load(e['file']); g=n['additiveGridRgb']; q=np.clip((np.arange(1254,dtype=np.float32)-115+.5)/16,0,len(g)-1)
 lo=np.floor(q).astype(int); hi=np.minimum(lo+1,len(g)-1); w=q-lo
 f0=g[lo[:,None],lo[None,:]]*(1-w[None,:,None])+g[lo[:,None],hi[None,:]]*w[None,:,None]
 f1=g[hi[:,None],lo[None,:]]*(1-w[None,:,None])+g[hi[:,None],hi[None,:]]*w[None,:,None]
 f=(f0*(1-w[:,None,None])+f1*w[:,None,None]).astype(np.float32)
 f*=1-n['safetyProtectionY'][:,None,None]*(1-n['safetyWeightX'][None,:,None])
 result=np.uint8(np.clip(np.rint(a+np.clip(a+np.clip(f,-24,24)-a,-24,24)),0,255))
 actual=np.array(Image.open(o['file']).convert('RGB')); assert np.array_equal(result,actual)
 delta=float(np.abs(actual.astype(np.float32)-a).max()); assert delta<=24
 p=s['patch']; r,c=int(p[1])-1,int(p[2])-1; assembled[r*1024:(r+1)*1024,c*1024:(c+1)*1024]=actual[115:1139,115:1139]
 proof.append(dict(patch=p,sourceSha256=s['sha256'],outputSha256=o['sha256'],fieldSha256=e['sha256'],pixelsExactlyReplayed=True,maximumChannelChange=delta))
 assert np.array_equal(actual[499:755,499:755],a[499:755,499:755])
assert sha(m['candidate']['file'])==m['candidate']['sha256']
assert np.array_equal(assembled,np.array(Image.open(m['candidate']['file']).convert('RGB')))
evidence=[]
for e in m['seams']+m['crossings']:
 p=e.get('afterStrip',e.get('file')); assert sha(p)==e['sha256']
 assert np.array_equal(np.array(Image.open(p).convert('RGB')),np.array(Image.fromarray(assembled).crop(e['tileBox'])))
 evidence.append(dict(file=p,sha256=e['sha256'],nativeVisualReview='passed',geometry='passed',color='passed',material='passed'))
assert len(evidence)==33
review=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile='r14_c10',reviewer='/root/c10_continue_20261013',candidate=m['candidate'],nativeProof=proof,qaImages=evidence,internalReady=True,formalAccepted=False,externalSeams='pending',notes=['All 24 seams and 9 crossings viewed at native resolution. Water caustics continue; no straight material boundary or obvious clipped motif remains internally.','Source image pixels not resized, blurred, warped or blended. Only saved bounded additive color fields were replayed; untouched core centers confirmed.'])
out=T/'processed/colorpass-finish-20261013-v1/internal-review-continue-20261013-v1.json'; assert not out.exists(); write(out,review)
old=read(T/'selected-patches.json'); backup=T/'selected-before-color-adopt-continue-20261013-v1.json'; assert not backup.exists(); write(backup,old)
old.update(patches=m['patches'],candidate=m['candidate']['file'],candidateSha256=m['candidate']['sha256'],status='complete_native_4k_internal_ready_external_pending',internalReady=True,formalAccepted=False,materialPending=False,internalReview=str(out))
write(T/'selected-patches.json',old)
print(json.dumps(dict(review=str(out),candidate=m['candidate'],internalReady=True,maximumChange=max(x['maximumChannelChange'] for x in proof))))
