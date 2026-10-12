from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,runpy
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
runpy.run_path(str(T/'replay_stone_v3_20261012.py'),run_name='__main__')
m=read(T/'candidate/r15_c13-native-halo24-v4-20261012-manifest.json');p=m['haloProvenanceSnapshot'];base=m['baseAssembly'];op=m['nativeHaloOperation'];z=np.load(p['horizontalRowAlpha']['path']);assert sha(p['horizontalRowAlpha']['path'])==p['horizontalRowAlpha']['sha256'];strip=np.zeros((1254,4326,3),np.uint8)
for i,s in enumerate(p['nativeSources']):
 assert sha(s['native']['path'])==s['native']['sha256'];im=Image.open(s['native']['path']);assert im.size==(1254,1254);a=np.asarray(im.convert('RGB'))
 if i==0:strip[:,:1254]=a
 else:
  x=i*1024;alpha=z['row04_c%02d_c%02d_alpha'%(i,i+1)].astype(np.uint32);strip[:,x:x+230]=((strip[:,x:x+230].astype(np.uint32)*(255-alpha[:,:,None])+a[:,:230].astype(np.uint32)*alpha[:,:,None]+127)//255).astype('uint8');strip[:,x+230:x+1254]=a[:,230:]
halo=strip[1139:1254,115:4211];assert np.array_equal(halo,np.asarray(Image.open(op['source']['path']).convert('RGB').crop(op['sourceCrop'])))
assert sha(base['candidate']['path'])==base['candidate']['sha256'];a=np.asarray(Image.open(base['candidate']['path']).convert('RGB')).copy();old=a.copy();mask=np.asarray(Image.open(op['mask']['path'])).astype(np.uint32);assert sha(op['mask']['path'])==op['mask']['sha256'];a[:115]=((halo.astype(np.uint32)*mask[:,:,None]+a[:115].astype(np.uint32)*(255-mask[:,:,None])+127)//255).astype('uint8')
assert np.array_equal(a,np.asarray(Image.open(m['candidate']['path']).convert('RGB')));assert sha(m['candidate']['path'])==m['candidate']['sha256'];assert np.array_equal(a[24:],old[24:]);assert np.array_equal(a[:,3254:],old[:,3254:])
ctx=np.asarray(Image.open(base['context']['path']).convert('RGB')).copy();ctx[115:4211,115:4211]=a;assert np.array_equal(ctx,np.asarray(Image.open(m['context']['path']).convert('RGB')));assert sha(m['context']['path'])==m['context']['sha256'];assert sha(op['immutableNorth']['path'])==op['immutableNorth']['sha256']
print(json.dumps({'status':'pass','haloPixelsReplayedDirectlyFromFour1254NativeSources':True,'stoneBaseReplayPassed':True,'corePixelExact':True,'contextPixelExact':True,'outsideNorth24RowsUnchangedFromStoneV3':True,'immutableNorthUnchanged':True,'nativeCropAndSavedAlphaOnly':True,'sourceRGBModified':False,'resized':False,'writesPerformed':False},indent=2))
