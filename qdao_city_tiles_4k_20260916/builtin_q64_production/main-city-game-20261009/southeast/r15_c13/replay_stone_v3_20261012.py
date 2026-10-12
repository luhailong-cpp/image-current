from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((T/'candidate/r15_c13-stone-only-v3-20261012-manifest.json').read_text(encoding='utf-8'));b=m['baseAssembly'];assert 'photometricStitching' not in m
assert sha(b['candidate']['path'])==b['candidate']['sha256'];a=np.asarray(Image.open(b['candidate']['path']).convert('RGB')).copy();orig=a.copy()
for op in m['repairOperations']:
 assert sha(op['source']['path'])==op['source']['sha256'];assert sha(op['mask']['path'])==op['mask']['sha256'];assert Image.open(op['source']['path']).size==(1254,1254)
 src=np.asarray(Image.open(op['source']['path']).convert('RGB').crop(op['sourceCrop'])).astype(np.uint32);mask=np.asarray(Image.open(op['mask']['path'])).astype(np.uint32);h,w=mask.shape;x,y=op['targetXY']
 a[y:y+h,x:x+w]=((src*mask[:,:,None]+a[y:y+h,x:x+w].astype(np.uint32)*(255-mask[:,:,None])+127)//255).astype('uint8')
assert sha(m['candidate']['path'])==m['candidate']['sha256'];assert np.array_equal(a,np.asarray(Image.open(m['candidate']['path']).convert('RGB')));assert np.array_equal(a[:3000],orig[:3000])
assert sha(b['context']['path'])==b['context']['sha256'];ctx=np.asarray(Image.open(b['context']['path']).convert('RGB')).copy();ctx[115:4211,115:4211]=a
assert sha(m['context']['path'])==m['context']['sha256'];assert np.array_equal(ctx,np.asarray(Image.open(m['context']['path']).convert('RGB')))
assert sha(m['immutableNorth']['path'])==m['immutableNorth']['sha256']
print(json.dumps({'status':'pass','nativeIntegerCropAndSavedAlphaOnly':True,'replayCorePixelExact':True,'replayContextPixelExact':True,'northStripExactlyBaseline':True,'immutableNorthUnchanged':True,'candidateSha256':m['candidate']['sha256'],'contextSha256':m['context']['sha256'],'writesPerformed':False},indent=2))
