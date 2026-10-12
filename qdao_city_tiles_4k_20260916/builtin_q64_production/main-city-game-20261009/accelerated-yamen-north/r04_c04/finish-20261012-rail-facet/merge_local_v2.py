from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).parent
m=json.loads((D/'derivation.json').read_text())
a=np.array(Image.open(m['baseContext']['file']).convert('RGB'));b=np.array(Image.open(m['raw']['file']).convert('RGB'))
y,x=np.indices((1254,1254))
def s(v,l,r):
 t=np.clip((v-l)/(r-l),0,1);return t*t*(3-2*t)
w=s(x,591,607)*(1-s(x,651,661))*s(y,497,551)*(1-s(y,597,651))
al=np.rint(w*255).astype(np.uint8);mask=al>0
out=((a.astype(np.uint32)*(255-al[:,:,None])+b.astype(np.uint32)*al[:,:,None]+127)//255).astype(np.uint8)
assert np.array_equal(out[~mask],a[~mask])
for n,v in [('derived-context-native-v2.png',out),('source-alpha-u8-v2.png',al),('source-support-v2.png',mask.astype(np.uint8)*255)]:Image.fromarray(v).save(D/n)
Image.fromarray(out[475:675,525:725]).save(D/'qa-after-native-v2.png')
Image.fromarray(out[505:645,565:685]).save(D/'qa-facet-close-native-v2.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
yy,xx=np.where(mask);box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
m.update({'derived':{'file':str(D/'derived-context-native-v2.png'),'sha256':sha(D/'derived-context-native-v2.png'),'pixels':[1254,1254],'tileBox':[300,2400,1554,3654]},'supportContextROI':box,'supportTileROI':[box[0]+300,box[1]+2400,box[2]+300,box[3]+2400],'supportPixels':int(mask.sum()),'changedPixels':int(np.any(out!=a,axis=2).sum()),'sourceSupport':{'file':str(D/'source-support-v2.png'),'sha256':sha(D/'source-support-v2.png')},'sourceAlpha':{'file':str(D/'source-alpha-u8-v2.png'),'sha256':sha(D/'source-alpha-u8-v2.png'),'denominator':255,'formula':'round(255*smoothstep(x,591,607)*(1-smoothstep(x,651,661))*smoothstep(y,497,551)*(1-smoothstep(y,597,651)))'},'supportRationale':'Narrow material-only transition surrounding the48x33 target to avoid creating a rectangular paste boundary; same-world native pixels, no geometry transform.','previousVersion':'derivation.json','QA':[{'file':str(D/n),'sha256':sha(D/n),'nativePixelScale':1,'actuallyViewed':False} for n in ['qa-before-native.png','qa-after-native-v2.png','qa-facet-close-native-v2.png']]})
(D/'derivation-v2.json').write_text(json.dumps(m,indent=2))
rec=json.loads((D/'derived-context-native.png.generation.json').read_text());rec.update(file=m['derived']['file'],sha256=m['derived']['sha256'],derivationManifest=str(D/'derivation-v2.json'))
(D/'derived-context-native-v2.png.generation.json').write_text(json.dumps(rec,indent=2))
print(json.dumps({'supportTileROI':m['supportTileROI'],'supportPixels':m['supportPixels'],'sha256':m['derived']['sha256']}))

