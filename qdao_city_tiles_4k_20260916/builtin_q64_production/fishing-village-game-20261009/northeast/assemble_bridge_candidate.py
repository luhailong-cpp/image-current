"""Native-only temporary seam candidate and unscaled QA strips. No blending."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,hashlib,shutil,datetime
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
p=Z/'native/r06_c12_p11-p12-bridge-v1.png'
src=Path('C:/Users/luyua/.codex/generated_images/01a1216d-31f1-7d92-879a-4d63c0e554c3/exec-2465fca5-0aa4-45ab-8033-7c915e7cacf2.png')
shutil.copyfile(src,p)
im=Image.open(p);assert im.size==(1254,1254)
receipt=Z/'records/r06_c12_p11-p12-bridge-v1.receipt.json'
r=read(receipt)
roles=['authoritative layout','close-up materials only','primary Q Daoist style only','native 1:1 splice edit target']
refs=[dict(path=x,sha256=sha(Path(x)),role=roles[i]) for i,x in enumerate(r['request']['referenced_image_paths'])]
save(Path(str(p)+'.generation.json'),dict(file=str(p),sha256=sha(p),generatedAt=r['observedAtUtc'],width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',
 configSnapshot=read(Path('D:/work/image/config/image-generation.json')),submittedParameters=dict(model=None,quality=None),actualModel=None,actualQuality=None,
 unverifiedReason='Host-managed tool exposes no selectors and result/PNG metadata disclose no actual model/quality.',references=refs,prompt=str(Z/r['request']['promptPath']),
 evidence=dict(receipt=str(receipt),pngMetadataKeys=list(im.info)),nativeGlobalBox=[45453,20365,46707,21619],usableNative=False,status='candidate_awaiting_outer_boundary_QA'))
a=Z/'native/r06_c12_p11-v2.png';b=Z/'native/r06_c12_p12-v6.png'
ia=Image.open(a);ib=Image.open(b)
joined=Image.new('RGB',(2278,1254))
joined.paste(ia.crop((0,0,512,1254)),(0,0));joined.paste(im,(512,0));joined.paste(ib.crop((742,0,1254,1254)),(1766,0))
sources=[dict(path=str(q),sha256=sha(q),generationRecord=str(q)+'.generation.json') for q in [a,p,b]]
for name,box,globalbox in [('r06_c12_p11-bridge-candidate',(0,0,1254,1254),[44941,20365,46195,21619]),('r06_c12_p12-bridge-candidate',(1024,0,2278,1254),[45965,20365,47219,21619])]:
    dest=Z/'native'/f'{name}.png';joined.crop(box).save(dest)
    save(Path(str(dest)+'.derived.json'),dict(file=str(dest),sha256=sha(dest),pixels=[1254,1254],nativeGlobalBox=globalbox,
        derivedFrom=sources,operation='1:1 native crop and opaque paste; no resize, no blend, no feather',
        bridgeReplacementGlobalBox=[45453,20365,46707,21619],combinedNativeGlobalBox=[44941,20365,47219,21619],cropFromCombined=box,status='candidate_awaiting_QA',formalAccepted=False))
qa=[]
for name,x in [('bridge-left-boundary',512),('bridge-right-boundary',1766),('patch-core-boundary',1139)]:
    dest=Z/'qa'/f'{name}.png';box=(x-128,0,x+128,1254);joined.crop(box).save(dest)
    qa.append(dict(file=str(dest),sha256=sha(dest),boxInCombined=box,nativePixels=[256,1254],scale=1,seamLocalX=128))
metrics={}
target=Image.open(Z/'guides/r06_c12_p11-p12.bridge-edit-target.png')
for side,box in [('left180',(0,0,180,1254)),('right180',(1074,0,1254,1254))]:
    d=ImageChops.difference(im.crop(box).convert('RGB'),target.crop(box).convert('RGB'))
    metrics[side]={'rgbMeanAbsoluteDifference':ImageStat.Stat(d).mean,'exactEqual':d.getbbox() is None,'allPixelsCompared':True}
save(Z/'qa/bridge-candidate-check.json',dict(sources=sources,strips=qa,outerContextMetrics=metrics,visualQA='pending; numeric difference is not geometry acceptance',formalAccepted=False))
s=read(Z/'progress.json');s.update(generatedNativeCount=9,usableNativeCount=1,status='checking_bridge_candidate',currentPatch='p11-p12-seam',nextStep='Inspect all three 1:1 QA strips; accept only if outer boundaries and core boundary are continuous.',updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(Z/'progress.json',s)
print(json.dumps(metrics))
