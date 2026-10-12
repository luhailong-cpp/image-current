from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ramp(v,lo,hi):
 t=np.clip((v-lo)/(hi-lo),0,1)
 return t*t*(3-2*t)

for name,inner,outer in [
 ('f3-stair-tone',[596,574,664,682],[550,542,712,714]),
 ('f4-stair-tone',[603,574,652,682],[555,542,700,714])]:
 out=ROOT/'qa-repair-native'/name
 p=json.loads((out/'parameters.json').read_text('utf-8'))
 receipt=json.loads((out/'receipt.json').read_text('utf-8'))
 basefile=Path(p['baseFile'])
 assert sha(basefile)==p['baseHash']
 rawfile=out/'raw-generated.png'
 assert sha(rawfile)==sha(receipt['hostSourceFile'])
 raw=Image.open(rawfile).convert('RGB')
 source=Image.open(out/'source-context.png').convert('RGB')
 assert raw.size==source.size==(1254,1254), 'No resampling allowed.'
 x=np.arange(1254,dtype=np.float64)[None,:]+0.5
 y=np.arange(1254,dtype=np.float64)[:,None]+0.5
 a=ramp(x,outer[0],inner[0])*(1-ramp(x,inner[2],outer[2]))*ramp(y,outer[1],inner[1])*(1-ramp(y,inner[3],outer[3]))
 au=np.floor(a*255+0.5).astype(np.uint8)
 Image.fromarray(au,mode='L').save(out/'alpha.png')
 b=np.asarray(source,dtype=np.uint32)
 g=np.asarray(raw,dtype=np.uint32)
 w=au.astype(np.uint32)[:,:,None]
 derived=((b*(255-w)+g*w+127)//255).astype(np.uint8)
 assert np.all(derived[au==0]==b[au==0])
 if name.startswith('f3'):
  assert np.max(au[:,:2048-p['contextTileBox'][0]])==0
 Image.fromarray(derived).save(out/'derived-context.png')
 q=[outer[0]-70,outer[1]-80,outer[2]+70,outer[3]+80]
 source.crop(q).save(out/'detail-before-native.png')
 raw.crop(q).save(out/'detail-raw-native.png')
 Image.fromarray(derived).crop(q).save(out/'detail-derived-native.png')
 montage=Image.new('RGB',((q[2]-q[0])*3,q[3]-q[1]))
 for i,img in enumerate([source,raw,Image.fromarray(derived)]): montage.paste(img.crop(q),(i*(q[2]-q[0]),0))
 montage.save(out/'comparison-before-raw-derived-native.png')
 nz=np.argwhere(au>0)
 changed=np.argwhere(np.any(derived!=b,axis=2))
 actual=[int(changed[:,1].min()),int(changed[:,0].min()),int(changed[:,1].max()+1),int(changed[:,0].max()+1)]
 cb=p['contextTileBox']
 actualtile=[actual[0]+cb[0],actual[1]+cb[1],actual[2]+cb[0],actual[3]+cb[1]]
 manifest={
 'patchId':name,'status':'pending-visual-review',
 'contextTileBox':p['contextTileBox'],'contextWorldBox':p['contextWorldBox'],
 'rawFile':str(rawfile),'rawHash':sha(rawfile),'rawHostFile':receipt['hostSourceFile'],'rawDimensions':list(raw.size),
 'baseFile':p['baseFile'],'baseHash':p['baseHash'],
 'sourceFile':str(out/'source-context.png'),'sourceHash':sha(out/'source-context.png'),
 'guideFile':p['guideFile'],'guideHash':p['guideHash'],
 'alphaFile':str(out/'alpha.png'),'alphaHash':sha(out/'alpha.png'),'alphaMode':'L','alphaDimensions':[1254,1254],'alphaScale':255,
 'alphaInnerBox':inner,'alphaOuterBox':outer,
 'alphaFormula':'At pixel centers X=x+0.5,Y=y+0.5: S(t)=3*t^2-2*t^3 with t clamped to [0,1]. W=S((X-outer.left)/(inner.left-outer.left)) * (1-S((X-inner.right)/(outer.right-inner.right))) * S((Y-outer.top)/(inner.top-outer.top)) * (1-S((Y-inner.bottom)/(outer.bottom-inner.bottom))). alpha= floor(255*W+0.5).',
 'blendFormula':'Per-channel sRGB byte arithmetic at identical coordinates: floor((base*(255-alpha)+raw*alpha+127)/255). No resampling, warp, blur, color correction or hand-painted content.',
 'derivedFile':str(out/'derived-context.png'),'derivedHash':sha(out/'derived-context.png'),'derivedDimensions':[1254,1254],
 'derivationType':'same-coordinate alpha composite of native base and native built-in generated repair; not a single-source native image',
 'actualChangedContextBox':actual,'actualChangedTileBox':actualtile,'changedPixels':int(changed.shape[0]),
 'verifiedUnchangedOutsideAlpha':True,'verifiedHostRawByteIdentical':True,
 'visualReview':None,
 'integrationInstructions':'Verify baseHash. Replace only pixels where alpha>0 in contextTileBox with already-composited derived-context pixels at the same coordinates; do not apply alpha again. Patches F3 and F4 have disjoint actual changed regions.'}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'patch':name,'rawSize':raw.size,'changedTileBox':actualtile,'changedPixels':changed.shape[0],'manifest':str(out/'manifest.json')},ensure_ascii=False))
