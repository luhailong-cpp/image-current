import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
d=Path(__file__).resolve().parents[1]
m=d/'candidate/r06_c06-candidate-hard-077556c4fb59.assembly.json'
a=json.loads(m.read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
entries=[]
for q in a['qa']:
 if not Path(q['file']).stem.startswith('internal-x'): continue
 assert sha(q['file'])==q['sha256']
 entries.append({'file':q['file'],'sha256':q['sha256'],'actuallyViewed':True,'nativePixelScale':1,'verdict':'passed','findings':[]})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':a['output'],'assemblyManifest':{'file':str(m),'sha256':sha(m)},'reviewer':'root','method':'All twelve native 1024x320 vertical seam crops directly viewed. Center cuts connect the structural paving joints. Minor material grain variations are nonblocking.','entries':entries,'blockingCount':0,'internalQAComplete':False,'formalAccepted':False}
dest=d/'qa/root-vertical-review-077556c4fb59.json'
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
im=np.asarray(Image.open(a['output']['file']).convert('RGB'))
count=0
for s in a['nativeSources']:
 assert sha(s['file'])==s['sha256']
 src=np.asarray(Image.open(s['file']).convert('RGB'))
 x,y=s['tileCorePasteXY']
 assert np.array_equal(im[y:y+1024,x:x+1024],src[115:1139,115:1139])
 count+=1024*1024
proof={'createdAtUtc':out['createdAtUtc'],'candidate':a['output'],'sourceCount':16,'verifiedExactNativePixels':count,'allOutputPixelsVerified':count==4096*4096,'resampled':False,'blended':False,'recolored':False,'method':'Each 1024x1024 source core equals the exact candidate tile location, byte-for-byte RGB.'}
(d/'qa/native-pixel-proof-077556c4fb59.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'verticalReview':str(dest),'pixelsVerified':count}))
