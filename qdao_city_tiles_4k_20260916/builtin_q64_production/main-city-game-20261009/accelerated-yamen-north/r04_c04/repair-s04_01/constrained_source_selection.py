from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix08'
newfile=D/'generated.png';oldfile=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
new=np.array(Image.open(newfile).convert('RGB'));old=np.array(Image.open(oldfile).convert('RGB'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Only choose unmodified same-world source pixels. Cost smoothing never touches art.
diff=new[1024:1254].astype(np.float32)-old[:230].astype(np.float32)
cost=np.mean(diff*diff,axis=2)[:115]
pad=np.pad(cost,((3,3),(0,0)),mode='edge')
cost=np.mean(np.stack([pad[i:i+115] for i in range(7)]),axis=0)
step=16
blocks=[(x,min(x+step,1254)) for x in range(0,1254,step)]
bc=np.stack([cost[:,a:b].mean(axis=1) for a,b in blocks],axis=1)
typical=float(np.median(bc))+1
bc+=((np.arange(115)[:,None]-57)/57)**4*typical*.08
prev=bc[:,0].copy();back=np.zeros(bc.shape,dtype=np.int8)
for i in range(1,len(blocks)):
 options=[]
 for d in range(-3,4):
  v=np.full(115,np.inf,dtype=np.float32)
  for y in range(115):
   py=y+d
   if 0<=py<115:v[y]=prev[py]+typical*.12*abs(d)
  options.append(v)
 choices=np.stack(options)
 choice=choices.argmin(axis=0)
 back[:,i]=choice-3
 prev=bc[:,i]+np.take_along_axis(choices,choice[None,:],axis=0)[0]
path=np.empty(len(blocks),dtype=np.int32);path[-1]=int(prev.argmin())
for i in range(len(blocks)-1,0,-1):path[i-1]=path[i]+int(back[path[i],i])
centers=np.array([(a+b-1)/2 for a,b in blocks])
seam=np.rint(np.interp(np.arange(1254),centers,path)).astype(np.int32)
assert seam.min()>=0 and seam.max()<=114
choose=np.arange(230)[:,None]>=seam[None,:]
result=new.copy();result[1024:1254]=np.where(choose[...,None],old[:230],new[1024:1254])
assert np.all(np.all(result[1024:1254]==old[:230],axis=2)|np.all(result[1024:1254]==new[1024:1254],axis=2))
assert np.array_equal(result[1138:1254],old[114:230])
out=D/'s04_01_fix08_south-minerror-derived.png'
if out.exists():raise FileExistsError(out)
Image.fromarray(result).save(out)
mask=np.zeros((1254,1254),dtype=np.uint8);mask[1024:1254]=choose.astype(np.uint8)*255
Image.fromarray(mask).save(D/'south-minerror-source-mask.png')
hard=Image.new('RGB',(1254,640));hard.paste(Image.fromarray(result).crop((0,819,1254,1139)),(0,0));hard.paste(Image.fromarray(old).crop((0,115,1254,435)),(0,320))
hard.save(D/'south-minerror-derived-boundary-native.png')
hard.crop((600,100,1120,550)).save(D/'south-minerror-derived-rail-native.png')
refs=[{'file':str(x),'sha256':sha(x),'pixels':[1254,1254]} for x in [newfile,oldfile]]
record={'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','mode':'RGB','opaque':True,
        'kind':'native_pixel_source_selection_derivative','route':'native_pixel_source_selection','tool':None,
        'actualModel':None,'actualQuality':None,'generatedBySingleImageGenCall':False,
        'sources':refs,'sourceNorthWorldBox':[12173,15245,13427,16499],'sourceSouthWorldBox':[12173,16269,13427,17523],
        'worldBoxWithHalo':[12173,15245,13427,16499],'coreCrop':[115,115,1139,1139],
        'method':'Regularized blockwise minimum-error binary source selection;16pxcostblocks,7-rowcostsmoothing,maximum3pxpathmovementperblock; no artwork pixels filtered',
        'allowedSeamY':[1024,1138],'actualSeamYRange':[int(1024+seam.min()),int(1024+seam.max())],
        'seamYForEveryNativeX':(1024+seam).tolist(),'sourceMaskFile':str(D/'south-minerror-source-mask.png'),'sourceMaskSha256':sha(D/'south-minerror-source-mask.png'),
        'maskMeaning':'0=fix08generated native,255=real south native offset by1024worldpixels',
        'pixelsFromSouth':int(choose.sum()),'pixelsFromFix08':int(result.shape[0]*result.shape[1]-choose.sum()),
        'resizedAfterGeneration':False,'finalArtUpscaled':False,'pixelReplayMismatchCount':0,
        'lastNorthernCoreRowMatchesSouthNativeRow114':True,'sourceReplayVerified':True,
        'formalAccepted':False,'visualQA':'pending; must inspect internal derivative seam as well as formal boundary',
        'integration':'This is a derived source, never ingest as a single raw image_gen result. Sidecar records two native sources and source mask; parent may select only after QA.'}
(out.with_suffix('.png.derivation.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
# Compatibility sidecar for pipeline native_info; explicitly not a generation claim.
(out.with_suffix('.png.generation.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':record['sha256'],'seamYRange':record['actualSeamYRange'],'sourceReplayMismatchCount':0,'formalBoundaryNativePixelsMatch':True},indent=2))
