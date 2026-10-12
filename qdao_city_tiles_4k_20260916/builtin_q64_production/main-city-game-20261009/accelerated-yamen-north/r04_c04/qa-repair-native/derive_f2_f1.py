from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ss(t):t=np.clip(t,0,1);return t*t*(3-2*t)
for name,outer,inner,detail in [('f2-rail-tone',[594,532,660,744],[604,584,649,692],[535,480,735,810]),('f1-door-groove',[565,450,690,830],[604,505,652,775],[555,410,705,870])]:
 O=D/name;prep=json.loads((O/'preparation.json').read_text());base=np.array(Image.open(O/'context-native.png').convert('RGB'),dtype=np.uint32);raw=np.array(Image.open(O/'generated.png').convert('RGB'),dtype=np.uint32);assert base.shape==raw.shape==(1254,1254,3)
 yy,xx=np.mgrid[:1254,:1254]+0.5
 w=ss((xx-outer[0])/(inner[0]-outer[0]))*(1-ss((xx-inner[2])/(outer[2]-inner[2])))*ss((yy-outer[1])/(inner[1]-outer[1]))*(1-ss((yy-inner[3])/(outer[3]-inner[3])))
 a=np.floor(w*255+0.5).astype(np.uint32);out=((base*(255-a[...,None])+raw*a[...,None]+127)//255).astype(np.uint8)
 assert np.array_equal(out[a==0],base[a==0]);Image.fromarray(a.astype(np.uint8)).save(O/'alpha.png');Image.fromarray(out).save(O/'derived-context.png')
 q=Image.new('RGB',((detail[2]-detail[0])*3,(detail[3]-detail[1])+20),(25,31,37));dr=ImageDraw.Draw(q)
 for i,(im,label) in enumerate([(base,'before'),(raw,'raw'),(out,'derived')]):q.paste(Image.fromarray(im.astype(np.uint8)).crop(detail),(i*(detail[2]-detail[0]),20));dr.text((i*(detail[2]-detail[0])+3,3),label,fill='white')
 q.save(O/'comparison-native.png');receipt=json.loads((O/'tool-result.json').read_text());host=Path(receipt['output_hint'].split(' as ')[1].split(' by default')[0]);assert sha(host)==sha(O/'generated.png')
 changed=np.any(out!=base,axis=2);ys,xs=np.where(changed);cb=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];tb=prep['contextTileBox'];changedtile=[cb[0]+tb[0],cb[1]+tb[1],cb[2]+tb[0],cb[3]+tb[1]]
 rec={'patchId':name,'status':'pending-visual-review','contextTileBox':tb,'contextWorldBox':prep['contextWorldBox'],'baseFile':prep['baseFile'],'baseHash':prep['baseSha256'],'sourceFile':str(O/'context-native.png'),'sourceHash':sha(O/'context-native.png'),'rawFile':str(O/'generated.png'),'rawHash':sha(O/'generated.png'),'rawHostFile':str(host),'rawDimensions':[1254,1254],'verifiedHostRawByteIdentical':True,
 'alphaFile':str(O/'alpha.png'),'alphaHash':sha(O/'alpha.png'),'alphaScale':255,'alphaOuterBox':outer,'alphaInnerBox':inner,'alphaFormula':'At pixel centers, product of smoothstep ramps from each outer boundary to corresponding inner boundary. S(t)=t*t*(3-2*t), clamp t to [0,1], alpha=floor(255*W+0.5).','blendFormula':'floor((base*(255-alpha)+raw*alpha+127)/255) in sRGB bytes, at identical coordinates; no resampling or image blur',
 'derivedFile':str(O/'derived-context.png'),'derivedHash':sha(O/'derived-context.png'),'derivationType':'Same-world-coordinate native base plus builtin generated repair with explicit narrow alpha; not a single-source native image','actualChangedContextBox':cb,'actualChangedTileBox':changedtile,'changedPixels':int(changed.sum()),'verifiedUnchangedOutsideAlpha':True,'actualModel':None,'actualQuality':None,
 'parametersFile':str(O/'parameters.json'),'parametersHash':sha(O/'parameters.json'),'receiptFile':str(O/'tool-result.json'),'receiptHash':sha(O/'tool-result.json'),'rawCopiedUnmodified':True,'resizedAfterGeneration':False,'visualReview':{'result':'pending'},'integrationInstructions':'Paste derived-context pixels only where alpha>0 at contextTileBox; do not apply alpha again.'}
 (O/'manifest.json').write_text(json.dumps(rec,indent=2),encoding='utf-8');print(json.dumps({'patch':name,'changedTileBox':changedtile,'pixels':int(changed.sum())}))
