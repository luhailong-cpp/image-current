from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');R=T/'review/internal-repair-v4-20261012';R.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def checked(r):assert rec(r['path'])['sha256']==r['sha256'];return Path(r['path'])
manifests=[T/'repairs/internal-v1-20261012/composition.json',T/'repairs/internal-boundary-v2-20261012/composition.json',T/'repairs/internal-composite-v4-20261012/composition.json'];results=[];chain=None;count=0
for mp in manifests:
 m=read(mp);base=checked(m['base']);a=np.asarray(Image.open(base).convert('RGB')).copy()
 if chain is not None:assert np.array_equal(a,chain)
 for s in m['steps']:
  n=checked(s['native']);assert Image.open(n).size==(1254,1254);checked(s['receipt']);ap=checked(s['alpha']);x0,y0,x1,y1=s['placement'];new=np.asarray(Image.open(n).convert('RGB').crop(s['sourceCrop']),dtype='uint32');alpha=np.asarray(Image.open(ap),dtype='uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*alpha+old*(255-alpha)+127)//255).astype('uint8');count+=1
 assert np.array_equal(a,np.asarray(Image.open(checked(m['candidate'])).convert('RGB')))
 context=Image.open(checked(m['baseContext'])).convert('RGB');context.paste(Image.fromarray(a),(115,115));assert np.array_equal(np.asarray(context),np.asarray(Image.open(checked(m['context'])).convert('RGB')))
 chain=a;results.append({'composition':rec(mp),'candidate':m['candidate'],'exactPixelReplay':True,'contextExactPixelReplay':True})
current=read(manifests[-1]);images=[]
for id,box in [('I01',[610,1080,1864,2334]),('I02',[1510,1740,2764,2994]),('I03',[2842,430,4096,1684]),('closures',[1210,1950,2464,3204])]:
 p=R/f'{id}-current-native-1254.png';Image.fromarray(chain).crop(box).save(p);images.append({'id':id,'box':box,**rec(p),'native100pct':True})
Image.fromarray(chain).save(R/'overview-current-4096.png')
j={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':current['candidate'],'context':current['context'],'selectedRepairCompositions':results,'replayedAlphaSteps':count,'uniqueNewNativeOutputsUsed':6,'noResizeOrWarp':True,'noRGBColorCorrection':True,'neighborPixelsModified':False,'reviewImages':images,'formalAccepted':False}
(R/'replay-validation.json').write_text(json.dumps(j,indent=2));print(json.dumps({'steps':count,'report':rec(R/'replay-validation.json')}))

