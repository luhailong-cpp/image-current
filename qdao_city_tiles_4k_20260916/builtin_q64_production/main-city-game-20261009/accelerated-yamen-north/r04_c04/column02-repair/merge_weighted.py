from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
D=Path(__file__).parent
sys.path.insert(0,str(D.parent.parent))
import pipeline
M=json.loads((D/'merged-three-v2/derivation.json').read_text(encoding='utf-8'))
O=D/'merged-three-v3';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources=M['sources'];arrays=[np.asarray(Image.open(s['path']).convert('RGB')) for s in sources]
H,W,N=3302,1254,len(sources)
fields=np.zeros((N,H,W,3),np.uint8)
weights=np.zeros((N,H,W),np.float32)
for i,(s,a) in enumerate(zip(sources,arrays)):
 y=s['worldBox'][1]-12173;fields[i,y:y+1254]=a
for y0,y1,i in [(0,1139,0),(1139,2163,1),(2163,3302,2)]:weights[i,y0:y1]=1
def render(w):return np.clip(np.rint(np.einsum('nhw,nhwc->hwc',w,fields,dtype=np.float64)),0,255).astype(np.uint8)
canvas=render(weights);joins=[]
for saved in M['joins']:
 idx=saved['sourceId']-1;offset=saved['offsetY'];old=canvas[offset:offset+1254].copy();repair=arrays[idx]
 top=np.asarray(saved['topPath']);bottom=np.asarray(saved['bottomPath']);ys=np.arange(1254)[:,None]
 binary=((ys>=top[None,:])&(ys<bottom[None,:])).astype(np.float32)
 def smooth(t):
  t=np.clip(t,0,1);return t*t*(3-2*t)
 soft=smooth((ys-top[None,:]+64)/128)*smooth((bottom[None,:]-ys+64)/128)
 xx=np.arange(1254)[None,:]
 interior=smooth((xx-355)/20)*smooth((754-xx)/20)
 # Only interpolate already aligned red lacquer; preserve structural boundary cuts.
 oldr=old.astype(float);newr=repair.astype(float)
 red=(oldr[:,:,0]>110)&(newr[:,:,0]>110)&(oldr[:,:,0]>oldr[:,:,1]*1.65)&(newr[:,:,0]>newr[:,:,1]*1.65)&(oldr[:,:,0]>oldr[:,:,2]*1.6)&(newr[:,:,0]>newr[:,:,2]*1.6)
 support=interior*red
 alpha=(binary*(1-support)+soft*support).astype(np.float32)
 weights[:,offset:offset+1254]*=(1-alpha)[None,:,:]
 weights[idx,offset:offset+1254]+=alpha
 canvas=render(weights)
 joins.append({**saved,'method':'binary min-error structural cut with 128px smoothstep transition only inside aligned red-lacquer shaft','featherHalfWidthNativePixels':64,'shaftXLimits':[355,754],'resampling':False})
# Quantize explicit source weightsto uint16 summing to 65535, then render exactly from those archived maps.
q=np.floor(weights*65535).astype(np.uint16)
remainder=65535-q.sum(axis=0,dtype=np.uint32)
dominant=np.argmax(weights,axis=0);yy,xx=np.indices((H,W))
q[dominant,yy,xx]+=remainder.astype(np.uint16)
assert np.all(q.sum(axis=0,dtype=np.uint32)==65535)
canvas=np.clip(np.rint(np.einsum('nhw,nhwc->hwc',q.astype(np.float64),fields,dtype=np.float64)/65535),0,255).astype(np.uint8)
for_i=[]
for i in range(N):
 p=O/f'source-{i+1}-weights-u16.png';Image.fromarray(q[i]).save(p)
 for_i.append({'sourceId':i+1,'path':str(p),'sha256':sha(p),'denominator':65535})
assert np.array_equal(canvas[:512],arrays[0][:512])
assert np.array_equal(canvas[-512:],arrays[2][-512:])
strip=O/'column02-context.png';Image.fromarray(canvas).save(strip)
idxp=O/'column02-dominant-source-index.png';Image.fromarray((dominant+1).astype(np.uint8)).save(idxp)
blend=np.count_nonzero(q,axis=0)>1
bp=O/'blended-pixel-mask.png';Image.fromarray((blend*255).astype(np.uint8)).save(bp)
qa=[]
for j in joins:
 for lab,cy,rad in [('entry',j['offsetY']+int(np.median(j['topPath'])),180),('center',j['offsetY']+627,230),('exit',j['offsetY']+int(np.median(j['bottomPath'])),180)]:
  p=O/f"repair-{j['sourceId']}-{lab}-QA.png";box=[0,cy-rad,1254,cy+rad];Image.fromarray(canvas[box[1]:box[3]]).save(p)
  qa.append({'file':str(p),'sha256':sha(p),'cropBox':box,'nativePixelScale':1,'actuallyViewed':False})
manifest={'recordType':'multi_source_native_resolution_weighted_derivation','nativeToolOutput':False,'worldBox':M['worldBox'],'pixels':[1254,3302],'file':str(strip),'sha256':sha(strip),'sources':sources,'sourceWeightMaps':for_i,'dominantSourceMap':str(idxp),'blendedPixelMask':str(bp),'blendedPixelCount':int(blend.sum()),'joins':joins,'resampled':False,'blended':True,'colorCorrected':False,'pixelReconstruction':'round(sum(source_native_RGB_at_same_world_coordinate * uint16_weight)/65535); weights sum to65535, all source and map hashes archived','north512PreservedFromWidthCorrectedNative':True,'south512PreservedFromOriginal':True,'formalAccepted':False,'QA':qa}
patches=[]
for row,y0 in [(1,0),(2,1024),(3,2048)]:
 p=O/f's{row:02d}_02-derived.png';Image.fromarray(canvas[y0:y0+1254]).save(p)
 rec={'recordType':'multi_source_native_resolution_weighted_derivation','nativeToolOutput':False,'tool':None,'route':'derived_from_builtin_native_pixels','file':str(p),'width':1254,'height':1254,'sha256':sha(p),'worldBoxWithHalo':[13197,12173+y0,14451,13427+y0],'resizedAfterGeneration':False,'finalArtUpscaled':False,'blended':True,'actualModel':None,'actualQuality':None,'formalAccepted':False,'sources':sources,'sourceWeightMaps':for_i,'weightMapCropBox':[0,y0,1254,y0+1254],'derivationManifest':str(O/'derivation.json'),'generationEvidence':'Native-resolution multi-source weighted assembly; original generation evidence retained. Not a single tool-native image; narrow shaft-only alpha transitions explicitly recorded.'}
 p.with_suffix('.png.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8');patches.append(rec)
a=[np.asarray(Image.open(p['file'])) for p in patches]
assert np.array_equal(a[0][-230:],a[1][:230]) and np.array_equal(a[1][-230:],a[2][:230])
manifest['overlaps230pxExact']=True;manifest['derivedPatches']=patches
(O/'derivation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'directory':str(O),'checks':[pipeline.native_info(p['file']) for p in patches],'blendPixels':int(blend.sum()),'overlaps230pxExact':True},indent=2))
