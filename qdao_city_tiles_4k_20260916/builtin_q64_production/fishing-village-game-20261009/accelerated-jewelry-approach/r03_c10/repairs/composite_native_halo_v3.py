from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np, hashlib, json
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r03_c10')
D=R/'repairs'/'native-horizontal-halo-v1'; D.mkdir(parents=True,exist_ok=True)
Q=R/'qa'/'full-audit'/'halo-v3'; Q.mkdir(parents=True,exist_ok=True)
v1p=R/'candidate'/'r03_c10-4096-candidate-v1.png'
v2p=R/'candidate'/'r03_c10-4096-candidate-v2.png'
out=R/'candidate'/'r03_c10-4096-candidate-v3.png'
assert not out.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=Image.open(v1p).convert('RGB'); assert base.size==(4096,4096)
native_hashes={}; sources=[]; strips=[]
for row in [1,2]:
 strip=Image.new('RGB',(4096,230))
 for col in range(1,5):
  sp=R/'records'/f'p{row}{col}.selection.json'; sel=read(sp); src=Path(sel['file']); im=Image.open(src).convert('RGB')
  assert im.size==(1254,1254) and sha(src)==sel['sha256']
  crop=[115,1024,1139,1254] if row==1 else [115,0,1139,230]
  strip.paste(im.crop(crop),((col-1)*1024,0))
  native_hashes[str(src)]=sha(src)
  sources.append({'row':row,'column':col,**rec(src),'generationRecord':rec(Path(sel['generationRecord'])),'selection':rec(sp),'nativeDimensions':list(im.size),'sourceCropXYXY':crop,'pasteIntoOverlapXY':[(col-1)*1024,0],'nativePixelsResized':False})
 p=D/f'row{row}-overlap-native-4096x230.png'; strip.save(p);strips.append(strip)
# Actual source correspondence: row1 y1024..1254 and row2 y0..230 both map to tile y909..1139.
t=np.arange(230,dtype=np.float64)/229
wy=np.rint(255*(0.5-0.5*np.cos(np.pi*t))).astype(np.uint8)
bottom_mask=Image.fromarray(np.repeat(wy[:,None],4096,axis=1),'L')
bottom_mask_path=D/'bottom-source-cosine-weight-overlap-4096x230.png';bottom_mask.save(bottom_mask_path)
mixed=Image.composite(strips[1],strips[0],bottom_mask)
mixed.save(D/'mixed-overlap-native-4096x230.png')
xx=np.arange(4096); edge=np.minimum(xx-1300,3981-1-xx)
tx=np.clip(edge/32,0,1); ax=np.rint(255*(0.5-0.5*np.cos(np.pi*tx))).astype(np.uint8)
activation_arr=np.repeat(ax[None,:],230,axis=0)
activation=Image.fromarray(activation_arr,'L')
activation.save(D/'overlap-activation-local-4096x230.png')
stage=base.copy()
before=base.crop((0,909,4096,1139))
stage.paste(Image.composite(mixed,before,activation),(0,909))
full_activation=np.zeros((4096,4096),dtype=np.uint8);full_activation[909:1139]=activation_arr
activation_full_path=D/'overlap-activation-full-tile-4096.png';Image.fromarray(full_activation,'L').save(activation_full_path)
full_bottom=np.zeros((4096,4096),dtype=np.uint8);full_bottom[909:1139]=np.asarray(bottom_mask)
bottom_full_path=D/'bottom-source-cosine-weight-full-tile-4096.png';Image.fromarray(full_bottom,'L').save(bottom_full_path)
# Store full effective mathematical weights as float32; actual PIL operations use the exact 8-bit masks above with intermediate rounding.
af=full_activation.astype(np.float32)/255
bf=full_bottom.astype(np.float32)/255
weights_path=D/'full-effective-weights-before-intermediate-rounding.npz'
np.savez_compressed(weights_path,base=1-af,row1=af*(1-bf),row2=af*bf)
repair_dir=R/'repairs'/'umbrella-tint-v1'
repair=Image.open(repair_dir/'native-result.png').convert('RGB')
vertical_mask=Image.open(repair_dir/'blend-mask-local-1254.png').convert('L')
assert repair.size==vertical_mask.size==(1254,1254)
crop=[1421,128,2675,1382]
final=stage.copy(); final.paste(Image.composite(repair,stage.crop(crop),vertical_mask),(crop[0],crop[1]))
full_vertical=Image.new('L',(4096,4096),0);full_vertical.paste(vertical_mask,(crop[0],crop[1]))
full_vertical_path=D/'vertical-repair-alpha-full-tile-4096.png';full_vertical.save(full_vertical_path)
final.save(out)
a=np.asarray(base); prev=np.asarray(Image.open(v2p).convert('RGB')); b=np.asarray(final)
changed=np.any(prev!=b,axis=2); ys,xs=np.where(changed)
changed_box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
outside=np.ones((4096,4096),dtype=bool);outside[909:1139,1300:3981]=False
assert not np.any(changed[outside]), 'v3 must only differ from v2 within horizontal overlap.'
edges={}
for name,box in {'top':[0,0,4096,115],'bottom':[0,3981,4096,4096],'left':[0,0,115,4096],'right':[3981,0,4096,4096]}.items():
 p=base.crop(box).tobytes();q=final.crop(box).tobytes()
 assert p==q
 edges[name]={'byteIdentical':True,'v1RawRGBSha256':hashlib.sha256(p).hexdigest(),'v3RawRGBSha256':hashlib.sha256(q).hexdigest()}
for src,digest in native_hashes.items():assert sha(src)==digest
def hs(arr,y,x1,x2):
 z=arr.astype(np.float32);j=np.abs(z[y,x1:x2]-z[y-1,x1:x2])
 n=np.abs(np.diff(z[y-16:y+17,x1:x2],axis=0));n=np.concatenate([n[:15],n[16:]],axis=0)
 return {'meanAbsoluteRGBJump':float(j.mean()),'nearbyMeanAbsoluteRGBJump':float(n.mean()),'downMinusUpRGB':(z[y,x1:x2]-z[y-1,x1:x2]).mean(axis=0).tolist()}
def vs(arr,x,y1,y2):
 z=arr.astype(np.float32);return float(np.abs(z[y1:y2,x]-z[y1:y2,x-1]).mean())
metrics={'horizontalY1024':{},'verticalX2048Y384to1024':{'v2MeanAbsoluteRGBJump':vs(prev,2048,384,1024),'v3MeanAbsoluteRGBJump':vs(b,2048,384,1024)},'outer115PixelStrips':edges,'v3ChangesRelativeToV2Count':int(changed.sum()),'v3ChangesRelativeToV2Box':changed_box,'v3OutsideHorizontalOverlapByteIdenticalToV2':True,'sourceNativeHashesUnchanged':True}
for name,x1,x2 in [('left',1536,1811),('center_repaired',1950,2146),('right',2286,2675),('right_middle',2675,3072),('far_right',3072,3800)]:
 metrics['horizontalY1024'][name]={'xRangeHalfOpen':[x1,x2],'v2':hs(prev,1024,x1,x2),'v3':hs(b,1024,x1,x2)}
write(Q/'metrics.json',metrics)
for label,im in [('v2',Image.fromarray(prev)),('v3',final)]:
 for name,box in {'left-transition':[1240,832,1832,1216],'center':[1747,832,2350,1216],'right-middle':[2240,832,2784,1216],'right':[2816,832,3840,1216],'right-edge-transition':[3712,832,4096,1216],'vertical-seam':[1792,256,2304,1344]}.items():
  im.crop(box).save(Q/(label+'-'+name+'-native.png'))
pv=final.copy();pv.thumbnail((1024,1024));pv.save(Q/'candidate-v3-preview-only.png')
manifest={'file':str(out),'sha256':sha(out),'dimensions':[4096,4096],'classification':'native-source overlap composite, not a single native 4K image','previousCandidate':rec(v2p),'baseCandidate':rec(v1p),'sources':sources,'operation':{'sourceOverlapTileBoxXYXY':[0,909,4096,1139],'nativeScale':1,'resampling':False,'paintingOrColorFiltering':False,'nativeSourceCrops':'top row [115,1024,1139,1254]; bottom row [115,0,1139,230]; paste per selected column','rowCrossfade':'bottom alpha = round(255*(0.5-0.5*cos(pi*(y-909)/229)))','horizontalActivation':'x in [1300,3981), 32px cosine feather: round(255*(0.5-0.5*cos(pi*clip(min(x-1300,3980-x)/32,0,1))))','compositeSequence':'1) source-row Image.composite using bottom weight; 2) horizontal activation over original v1 crop; 3) native builtin vertical repair over intermediate candidate with identical recorded vertical mask','script':rec(Path(__file__))},'masksAndWeights':{'bottomSourceWeightLocal':rec(bottom_mask_path),'bottomSourceWeightFull':rec(bottom_full_path),'activationFull':rec(activation_full_path),'effectiveWeightsFull':rec(weights_path),'effectiveWeightCaveat':'Effective floating weights describe mathematical proportions; actual output uses intermediate 8-bit PIL alpha rounding, fully determined by script and exact masks.','verticalRepairAlphaFull':rec(full_vertical_path),'verticalRepairAlphaLocal':rec(repair_dir/'blend-mask-local-1254.png')},'verticalRepair':{'nativeResult':rec(repair_dir/'native-result.png'),'nativeDimensions':[1254,1254],'targetBoxTileXYXY':crop,'prompt':rec(repair_dir/'prompt.txt'),'request':rec(repair_dir/'request.json'),'receipt':rec(repair_dir/'receipt.json'),'actualModel':None,'actualQuality':None,'unknownReason':'Builtin metadata does not disclose these fields.'},'metrics':rec(Q/'metrics.json'),'formalAccepted':False,'externalSeamsChecked':False,'status':'pending original-scale ghosting and transitions review','untouchedIssue':'Bottom gold tips blur remains for root builtin localized correction.','createdAt':datetime.now(timezone.utc).isoformat()}
write(out.with_suffix('.manifest.json'),manifest)
print(json.dumps({'candidate':str(out),'sha256':sha(out),'metrics':metrics},indent=2))

