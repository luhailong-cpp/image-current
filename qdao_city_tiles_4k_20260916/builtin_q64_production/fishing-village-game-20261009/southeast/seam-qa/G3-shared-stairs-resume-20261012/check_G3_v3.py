"""Exact bounded v2 masked composition plus v3 local generated crop."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,importlib.util
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;BASE=D.parent.parent
STEM='G3-bottom-conditioned-v3';FRAME=[36060,46592,37314,47846]
LOCAL=[925,680,1005,760];WORLD=[36985,47272,37065,47352]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):
    assert not p.exists(),p
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
orig=Path('C:/Users/luyua/.codex/generated_images/01a13003-bb39-7e00-ae6d-ced8fbe4df6b/exec-094b2373-c457-4f35-a4f9-d6138ec273ad.png')
raw=D/(STEM+'-raw.png');assert not raw.exists();shutil.copy2(orig,raw)
im=Image.open(raw);assert im.size==(1254,1254)
assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
reqp=D/(STEM+'.request.json');req=json.loads(reqp.read_text(encoding='utf-8'))['actualToolInput']
inv=json.loads((D/(STEM+'.invocation.json')).read_text(encoding='utf-8'))
save(D/(STEM+'.generation-receipt.json'),{'schemaVersion':1,'tool':'builtin image_gen.imagegen',
 'status':'returned_image_success','startedAtUtc':inv['startedAtUtc'],'endedAtUtc':inv['endedAtUtc'],
 'actualToolInput':req,'request':str(reqp),'requestSha256':sha(reqp),
 'actualReferences':[{'file':p,'sha256':sha(p)} for p in req['referenced_image_paths']],
 'originalBuiltinOutput':str(orig),'originalBuiltinOutputSha256':sha(orig),'savedOutput':str(raw),
 'savedOutputSha256':sha(raw),'dimensions':[1254,1254],'opaque':True,'actualModel':None,'actualQuality':None,
 'paidApiUsed':False,'canonicalSelectionsModified':False})
old=json.loads((D/'G3-bottom-conditioned-v2.adoption-check.json').read_text(encoding='utf-8'))
before=Image.open(old['boundedPreview']).convert('RGB');after=before.copy();after.paste(im.crop(LOCAL),LOCAL[:2])
mask=np.zeros((1254,1254),bool);mask[680:760,925:1005]=True
assert np.array_equal(np.asarray(before)[~mask],np.asarray(after)[~mask])
preview=D/(STEM+'-bounded-preview-native1254.png');assert not preview.exists();after.save(preview)
patches=[]
for rec in old['patches']:
    assert sha(rec['file'])==rec['sha256']
    art=Image.open(rec['file']).convert('RGB');initial=np.asarray(art).copy();nb=rec['nativeFrameWorld']
    inter=[max(nb[0],WORLD[0]),max(nb[1],WORLD[1]),min(nb[2],WORLD[2]),min(nb[3],WORLD[3])]
    dest=None;sourcebox=None
    if inter[0]<inter[2] and inter[1]<inter[3]:
        sourcebox=[inter[0]-FRAME[0],inter[1]-FRAME[1],inter[2]-FRAME[0],inter[3]-FRAME[1]]
        dest=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]]
        art.paste(im.crop(sourcebox),dest[:2])
    else:inter=None
    path=D/(STEM+'-'+rec['tile']+'-'+rec['patch']+'-provisional-native1254.png');assert not path.exists();art.save(path)
    out=dict(rec);out.update(file=str(path),sha256=sha(path),v2Source=rec['file'],v2SourceSha256=rec['sha256'],
      v3LocalWorldAdoptBox=inter,v3LocalNativeAdoptBox=dest,v3RawSourceBox=sourcebox,
      v3LocalChangedPixels=int(np.any(np.asarray(art)!=initial,axis=2).sum()))
    patches.append(out)
authority=Image.open(D/'G3-bottom-conditioned-v1-guide-native1254.png').convert('RGB')
mask2=Image.open(D/'G3-bottom-conditioned-v2-adopt-mask-native1254.png').convert('L')
replay=authority.copy();replay.paste(Image.open(D/'G3-bottom-conditioned-v2-raw.png').convert('RGB'),(0,0),mask2)
replay.paste(im.crop(LOCAL),LOCAL[:2]);assert np.array_equal(np.asarray(replay),np.asarray(after))
ids=np.zeros((1254,1254),np.uint8);ids[np.asarray(mask2)>0]=2;ids[680:760,925:1005]=3
npz=D/(STEM+'-native-source-replay.npz');assert not npz.exists()
np.savez_compressed(npz,sourceVersionIds=ids,nativeAfter=np.asarray(after),frameWorld=np.array(FRAME),v3LocalBox=np.array(LOCAL))
assert np.array_equal(np.asarray(authority)[ids==0],np.asarray(after)[ids==0])
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources()
for rec in patches:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
rebuilt,pieces,missing=sources.extract(FRAME);assert not missing
assert np.array_equal(np.asarray(rebuilt),np.asarray(after))
boxes={'left':[236,473,364,830],'top':[300,409,971,666],'right':[906,409,1069,830],
       'bottom':[300,702,1005,830],'G3':[257,427,1119,827],'band':[236,409,1069,830],
       'local-left':[893,648,957,792],'local-top':[893,648,1037,712],
       'local-right':[973,648,1037,792],'local-bottom':[893,728,1037,792]}
evidence=[]
for name,box in boxes.items():
    path=D/(STEM+'-'+name+'-native.png');assert not path.exists();after.crop(box).save(path)
    evidence.append({'name':name,'file':str(path),'sha256':sha(path),'guideBox':box,
                     'worldBox':[box[0]+FRAME[0],box[1]+FRAME[1],box[2]+FRAME[0],box[3]+FRAME[1]],
                     'dimensions':[box[2]-box[0],box[3]-box[1]],'resampling':False})
save(D/(STEM+'.adoption-check.json'),{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'candidate_pending_native_perimeter_review','frameWorld':FRAME,'v2AdoptMask':str(D/'G3-bottom-conditioned-v2-adopt-mask-native1254.png'),
 'v3LocalGuideBox':LOCAL,'v3LocalWorldBox':WORLD,'boundingWorldBox':[36360,47065,37065,47358],
 'raw':str(raw),'rawSha256':sha(raw),'boundedPreview':str(preview),'boundedPreviewSha256':sha(preview),
 'exactNativeV2MaskV3LocalReplay':True,'nativeSourceReplay':str(npz),'nativeSourceReplaySha256':sha(npz),
 'fourNativeCoreReplayExact':True,'outsideUnionAdoptionChangedPixels':0,'outsideV3LocalChangedPixels':0,
 'patches':patches,'evidence':evidence,'canonicalSelectionsModified':False,'resampling':False,
 'syntheticGeometry':False,'paidApiUsed':False,'formalAccepted':False})
print(json.dumps({'report':str(D/(STEM+'.adoption-check.json')),'freshNativeReplayExact':True,
 'fourNativeCoreReplayExact':True,'outsideUnionPixelsChanged':0}))
