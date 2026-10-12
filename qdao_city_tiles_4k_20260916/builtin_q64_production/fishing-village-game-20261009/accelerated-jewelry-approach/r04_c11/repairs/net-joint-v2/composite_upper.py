from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach')
T=R/'r04_c11';D=T/'repairs/net-joint-v2';Q=T/'qa/net-joint-v2';Q.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
rec=lambda p:{'file':str(p),'sha256':sha(p)}
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for dirname,used in [('net-rope-v1',False),('net-joint-v2',True)]:
 d=T/'repairs'/dirname;npth=d/'native-result.png';im=Image.open(npth);req=read(d/'request.json');receipt=read(d/'receipt.json')
 assert im.size==(1254,1254)
 record={'file':str(npth),'sha256':sha(npth),'nativeDimensions':list(im.size),'format':im.format,'nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Builtin tool receipt exposes no verified model or quality metadata.','sourcePath':receipt.get('originalFile'),'prompt':req['prompt'],'promptFile':str(d/'prompt.txt'),'requestFile':str(d/'request.json'),'receiptFile':str(d/'receipt.json'),'references':[{'file':p,'sha256':sha(p),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'receipt':receipt,'contributesFinalPixels':used,'status':'selected_for_local_alpha_composite_pending_lower_net_repair' if used else 'rejected_no_final_pixel_contribution','rejectionReason':None if used else 'Insufficient upper context; continued rope runs out of image upper edge and would introduce a new truncation.','recordedAt':datetime.now(timezone.utc).isoformat()}
 if used:record['targetDerivation']=rec(d/'target-derivation.json')
 write(d/'native-result.generation.json',record)
basepath=T/'candidate/r04_c11-4096-candidate-v1.png';out=T/'candidate/r04_c11-4096-candidate-v2.png'
assert not out.exists()
base=Image.open(basepath).convert('RGB');target=Image.open(D/'target-native.png').convert('RGB');source=Image.open(D/'native-result.png').convert('RGB');box=[640,2304,1894,3558]
assert base.crop(box).tobytes()==target.tobytes()
yy,xx=np.indices((1254,1254),dtype=np.float64)
def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
top=np.interp(xx,[115,250,499,960,1000],[1040,965,832,638,638])
alpha=smooth((xx-115)/24)*smooth((1000-xx)/24)*smooth((yy-top)/24)*smooth((1139-yy)/72)
mask=Image.fromarray(np.rint(alpha*255).astype(np.uint8),'L');mask.save(D/'native-alpha-mask.png')
local=Image.composite(source,target,mask);local.save(Q/'composited-native-1254.png')
result=base.copy();result.paste(local,(640,2304));result.save(out)
diff=np.any(np.asarray(result)!=np.asarray(base),axis=2);ys,xs=np.where(diff);changed=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
for edge in [(0,0,4096,115),(0,3981,4096,4096),(0,0,115,4096),(3981,0,4096,4096)]:assert result.crop(edge).tobytes()==base.crop(edge).tobytes()
assert result.crop((0,0,4096,2942)).tobytes()==base.crop((0,0,4096,2942)).tobytes()
for name,b in {'incoming-transition':[80,975,310,1170],'old-cut':[350,810,640,1070],'post-contact':[850,610,1030,870],'lower-transition':[350,1020,800,1200]}.items():local.crop(b).save(Q/(name+'-native.png'))
preview=result.copy();preview.thumbnail((1024,1024));preview.save(Q/'candidate-v2-preview-only.png')
manifest={'file':str(out),'sha256':sha(out),'dimensions':[4096,4096],'classification':'unscaled native local alpha composite over existing 4096 core assembly','baseCandidate':rec(basepath),'nativeRepair':{**rec(D/'native-result.png'),'nativeDimensions':[1254,1254],'generationRecord':rec(D/'native-result.generation.json'),'actualModel':None,'actualQuality':None,'unknownReason':'Builtin tool did not disclose verified model/quality.'},'target':rec(D/'target-native.png'),'targetDerivation':rec(D/'target-derivation.json'),'prompt':rec(D/'prompt.txt'),'request':rec(D/'request.json'),'receipt':rec(D/'receipt.json'),'compositing':{'script':rec(Path(__file__)),'mask':rec(D/'native-alpha-mask.png'),'maskDimensions':[1254,1254],'cropBoxTileXYXY':box,'maskFormula':'round(255*smooth((x-115)/24)*smooth((1000-x)/24)*smooth((y-top(x))/24)*smooth((1139-y)/72)); smooth(t)=clip(t,0,1)^2*(3-2*clip(t,0,1)); top(x) piecewise linear through recorded points','topBoundaryPoints':[[115,1040],[250,965],[499,832],[960,638],[1000,638]],'operation':'Image.composite(native_result,target,L_mask), then unscaled paste at tile(640,2304)','nativePixelsResized':False,'painting':False,'geometryTransform':None,'actualChangedBoxTileXYXY':changed},'outer115PixelTileBorderByteIdentical':True,'topUnrelatedPixelsThroughTileY2942ByteIdentical':True,'rejectedAlternative':{'file':str(T/'repairs/net-rope-v1/native-result.png'),'sha256':sha(T/'repairs/net-rope-v1/native-result.png'),'contributesFinalPixels':False,'generationRecord':rec(T/'repairs/net-rope-v1/native-result.generation.json')},'formalAccepted':False,'status':'upper rope repair pending native visual review; lower vertical net artifact unresolved','remainingIssue':'Pre-existing vertical net splice at tile x1139 continues beneath the crop; root preparing lower native repair.','createdAt':datetime.now(timezone.utc).isoformat()}
write(out.with_suffix('.manifest.json'),manifest)
print(json.dumps({'candidate':str(out),'sha256':sha(out),'changedBox':changed}))

