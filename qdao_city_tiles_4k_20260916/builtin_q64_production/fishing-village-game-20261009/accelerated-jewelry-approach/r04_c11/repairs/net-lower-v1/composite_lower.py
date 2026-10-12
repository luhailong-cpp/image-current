from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach')
T=R/'r04_c11';D=T/'repairs/net-lower-v1';Q=T/'qa/net-lower-v1';Q.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=read(D/'request.json');receipt=read(D/'receipt.json');sourcepath=D/'native-result.png';source=Image.open(sourcepath).convert('RGB');target=Image.open(D/'target-native.png').convert('RGB')
assert source.size==target.size==(1254,1254)
g={'file':str(sourcepath),'sha256':sha(sourcepath),'nativeDimensions':[1254,1254],'format':'PNG','nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Builtin tool receipt does not disclose verified actual model or quality metadata.','sourcePath':receipt.get('originalFile'),'prompt':req['prompt'],'promptFile':str(D/'prompt.txt'),'requestFile':str(D/'request.json'),'receiptFile':str(D/'receipt.json'),'references':[{'file':p,'sha256':sha(p),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'receipt':receipt,'targetDerivation':rec(D/'target-derivation.json'),'contributesFinalPixels':True,'status':'selected_lower_mesh_repair_pending_composite_QA','recordedAt':datetime.now(timezone.utc).isoformat()}
write(D/'native-result.generation.json',g)
basepath=T/'candidate/r04_c11-4096-candidate-v2.png';base=Image.open(basepath).convert('RGB')
assert base.crop((512,2957,1766,4096)).tobytes()==target.crop((0,0,1254,1139)).tobytes()
deriv=read(D/'target-derivation.json')
rebuilt=Image.new('RGB',(1254,1254));rebuilt.paste(base.crop((512,2957,1766,4096)),(0,0))
for a in deriv['haloPlacements']:rebuilt.paste(Image.open(a['source']).convert('RGB').crop(a['crop']),a['paste'])
assert rebuilt.tobytes()==target.tobytes()
points=[[330,625],[400,540],[450,586],[500,586],[550,580],[600,568],[650,564],[700,560],[750,550],[800,545],[850,534],[900,523],[950,512],[1000,502],[1050,482],[1100,450],[1139,443],[1254,330]]
yy,xx=np.indices((1254,1254),dtype=np.float64)
left=np.interp(yy,[p[0] for p in points],[p[1] for p in points])
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
alpha=smooth((xx-left)/12)*smooth((1082-xx)/12)*smooth((yy-330)/32)
mask=Image.fromarray(np.rint(alpha*255).astype(np.uint8),'L');mask.save(D/'native-alpha-mask.png')
composited=Image.composite(source,target,mask)
crop=[0,0,1254,1139];result=base.copy();result.paste(composited.crop(crop),(512,2957))
trial=Q/'candidate-v3-trial.png';result.save(trial)
composited.crop(crop).save(Q/'after-native-1254x1139.png')
for name,b in {'top-transition':[460,300,1020,500],'left-fold-transition':[430,400,700,1100],'right-mesh-transition':[850,330,1120,1139],'bottom-boundary':[390,1000,1110,1139]}.items():composited.crop(b).save(Q/(name+'-native.png'))
a=np.asarray(base);b=np.asarray(result);changed=np.any(a!=b,axis=2);ys,xs=np.where(changed);cb=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
assert base.crop((0,0,4096,3287)).tobytes()==result.crop((0,0,4096,3287)).tobytes()
assert base.crop((1594,0,4096,4096)).tobytes()==result.crop((1594,0,4096,4096)).tobytes()
bottomx=np.where(changed[-1])[0].tolist()
write(D/'composite-plan.json',{'baseCandidate':rec(basepath),'nativeRepair':rec(sourcepath),'nativeDimensions':[1254,1254],'target':rec(D/'target-native.png'),'targetDerivation':rec(D/'target-derivation.json'),'mask':rec(D/'native-alpha-mask.png'),'tileTargetBox':[512,2957,1766,4211],'nativeCropContributingToTile':[0,0,1254,1139],'pasteXY':[512,2957],'leftBoundaryPointsYThenX':points,'maskFormula':'round(255*smooth((x-left(y))/12)*smooth((1082-x)/12)*smooth((y-330)/32)); smooth=clamped cubic smoothstep; no bottom fade; lower115 source rows are reference halo only','script':rec(Path(__file__)),'nativePixelsResized':False,'actualChangedBoxTile':cb,'bottomRowChangedXRangeInclusive':[min(bottomx),max(bottomx)] if bottomx else None,'changedPixelCount':int(changed.sum()),'targetPixelExactDerivationVerified':True,'upperPixelsBeforeY3287Unchanged':True,'rightPixelsX1594OnwardUnchanged':True,'externalBottomBoundaryReview':'affected bottom edge changed; neighbor outside assigned region must be checked later'})
print(json.dumps({'trial':str(trial),'changedBox':cb,'bottomChangedXRange':[min(bottomx),max(bottomx)] if bottomx else None}))

