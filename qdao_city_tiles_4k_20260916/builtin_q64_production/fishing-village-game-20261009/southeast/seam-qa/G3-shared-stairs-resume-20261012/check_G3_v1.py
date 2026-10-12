"""Save successful builtin output and bounded provisional adoption only."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,importlib.util
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;BASE=D.parent.parent
STEM='G3-bottom-conditioned-v1';FRAME=[36060,46592,37314,47846]
BOX=[250,597,970,725];WORLD=[36310,47189,37030,47317]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
orig=Path('C:/Users/luyua/.codex/generated_images/01a13003-bb39-7e00-ae6d-ced8fbe4df6b/exec-c3f89e46-b371-4ae2-bbae-b496e4708291.png')
raw=D/(STEM+'-raw.png');assert not raw.exists();shutil.copy2(orig,raw)
im=Image.open(raw);assert im.size==(1254,1254);assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
request=D/(STEM+'.request.json');req=json.loads(request.read_text(encoding='utf-8'))['actualToolInput']
inv=json.loads((D/(STEM+'.invocation.json')).read_text(encoding='utf-8'))
receipt={'schemaVersion':1,'tool':'builtin image_gen.imagegen','status':'returned_image_success',
 'startedAtUtc':inv['startedAtUtc'],'endedAtUtc':inv['endedAtUtc'],
 'request':str(request),'requestSha256':sha(request),'actualToolInput':req,
 'actualReferences':[{'file':p,'sha256':sha(p)} for p in req['referenced_image_paths']],
 'originalBuiltinOutput':str(orig),'originalBuiltinOutputSha256':sha(orig),
 'savedOutput':str(raw),'savedOutputSha256':sha(raw),'dimensions':list(im.size),'opaque':True,
 'actualModel':None,'actualQuality':None,'paidApiUsed':False,'canonicalSelectionsModified':False}
save(D/(STEM+'.generation-receipt.json'),receipt)
provenance=json.loads((D/(STEM+'-guide-provenance.json')).read_text(encoding='utf-8'))
guide=Image.open(provenance['guide']).convert('RGB')
bounded=guide.copy();bounded.paste(im.crop(BOX),BOX[:2])
preview=D/(STEM+'-bounded-preview-native1254.png');assert not preview.exists();bounded.save(preview)
aa=np.asarray(guide);bb=np.asarray(bounded)
mask=np.zeros((1254,1254),bool);mask[BOX[1]:BOX[3],BOX[0]:BOX[2]]=True
assert np.array_equal(aa[~mask],bb[~mask])
patches=[]
for src in provenance['nativePatchSources']:
    assert sha(src['file'])==src['sha256']
    art=Image.open(src['file']).convert('RGB');old=np.asarray(art).copy();nb=src['nativeBoxGlobal']
    inter=[max(nb[0],WORLD[0]),max(nb[1],WORLD[1]),min(nb[2],WORLD[2]),min(nb[3],WORLD[3])]
    assert inter[0]<inter[2] and inter[1]<inter[3]
    sourcebox=[inter[0]-FRAME[0],inter[1]-FRAME[1],inter[2]-FRAME[0],inter[3]-FRAME[1]]
    dest=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]]
    art.paste(im.crop(sourcebox),dest[:2]);array=np.asarray(art)
    pmask=np.zeros((1254,1254),bool);pmask[dest[1]:dest[3],dest[0]:dest[2]]=True
    assert np.array_equal(array[~pmask],old[~pmask])
    path=D/(STEM+'-'+src['tile']+'-'+src['patch']+'-provisional-native1254.png');assert not path.exists();art.save(path)
    cb=src['coreBoxGlobal'];coreinter=[max(cb[0],WORLD[0]),max(cb[1],WORLD[1]),min(cb[2],WORLD[2]),min(cb[3],WORLD[3])]
    if coreinter[0]>=coreinter[2] or coreinter[1]>=coreinter[3]:coreinter=None
    patches.append({'tile':src['tile'],'patch':src['patch'],'file':str(path),'sha256':sha(path),
                    'source':src['file'],'sourceSha256':src['sha256'],'nativeFrameWorld':nb,
                    'worldAdoptBox':inter,'nativeAdoptBox':dest,'rawSourceBox':sourcebox,'coreAdoptWorldBox':coreinter,
                    'changedPixels':int(np.any(array!=old,axis=2).sum()),
                    'coreChangedPixels':int(np.any(array[115:1139,115:1139]!=old[115:1139,115:1139],axis=2).sum()),
                    'outsideAdoptPixelChanges':0,'formalAccepted':False,'selected':False})
spec=importlib.util.spec_from_file_location('native_core_sources',BASE/'review_external_seams.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources()
for rec in patches:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
rebuilt,pieces,missing=sources.extract(FRAME);assert not missing,missing
assert np.array_equal(np.asarray(rebuilt),bb)
evidence=[]
for name,box in {'left':[186,533,314,789],'top':[250,533,970,661],
                 'right':[906,533,1034,789],'bottom':[250,661,970,789],
                 'G3':[257,427,1119,827],'band':[186,533,1034,789]}.items():
    path=D/(STEM+'-'+name+'-native.png');assert not path.exists();bounded.crop(box).save(path)
    evidence.append({'name':name,'file':str(path),'sha256':sha(path),'guideBox':box,
                     'worldBox':[box[0]+FRAME[0],box[1]+FRAME[1],box[2]+FRAME[0],box[3]+FRAME[1]],
                     'dimensions':[box[2]-box[0],box[3]-box[1]],'resampling':False})
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'bounded_candidate_pending_native_geometry_review','frameWorld':FRAME,
 'adoptGuideBox':BOX,'adoptWorldBox':WORLD,'guide':provenance['guide'],'guideSha256':provenance['guideSha256'],
 'raw':str(raw),'rawSha256':sha(raw),'boundedPreview':str(preview),'boundedPreviewSha256':sha(preview),
 'outsideAdoptionChangedPixels':0,'fourNativeCoreReplayExact':True,'patches':patches,'evidence':evidence,
 'generationReceipt':str(D/(STEM+'.generation-receipt.json')),
 'canonicalSelectionsModified':False,'resampling':False,'syntheticGeometry':False,'paidApiUsed':False,'formalAccepted':False}
save(D/(STEM+'.adoption-check.json'),report)
print(json.dumps({'report':str(D/(STEM+'.adoption-check.json')),'fourNativeCoreReplayExact':True,'patches':patches}))
