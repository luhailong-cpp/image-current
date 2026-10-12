"""Save builtin result and exact native bounded provisional cores."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil,importlib.util
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;BASE=D.parent.parent
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));STEM=job['stem'];FRAME=job['frameWorld'];BOX=job['adoptGuideBox'];WORLD=job['adoptWorldBox']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
orig=Path(job['originalBuiltinOutput']);raw=D/(STEM+'-raw.png');assert not raw.exists();shutil.copy2(orig,raw)
im=Image.open(raw);assert im.size==(1254,1254)
assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
reqp=D/(STEM+'.request.json');req=json.loads(reqp.read_text(encoding='utf-8'))['actualToolInput']
save(D/(STEM+'.generation-receipt.json'),{'schemaVersion':1,'tool':'builtin image_gen.imagegen','status':'returned_image_success',
 'startedAtUtc':job['startedAtUtc'],'endedAtUtc':job['endedAtUtc'],'request':str(reqp),'requestSha256':sha(reqp),
 'actualToolInput':req,'actualReferences':[{'file':p,'sha256':sha(p)} for p in req['referenced_image_paths']],
 'originalBuiltinOutput':str(orig),'originalBuiltinOutputSha256':sha(orig),'savedOutput':str(raw),
 'savedOutputSha256':sha(raw),'dimensions':[1254,1254],'opaque':True,'actualModel':None,'actualQuality':None,
 'paidApiUsed':False,'canonicalSelectionsModified':False})
before=Image.open(job['beforeGuide']).convert('RGB');after=before.copy();after.paste(im.crop(BOX),BOX[:2])
mask=np.zeros((1254,1254),bool);mask[BOX[1]:BOX[3],BOX[0]:BOX[2]]=True
assert np.array_equal(np.asarray(before)[~mask],np.asarray(after)[~mask])
preview=D/(STEM+'-bounded-preview-native1254.png');assert not preview.exists();after.save(preview)
man=json.loads((D/'current-native-guide-manifest-v1.json').read_text(encoding='utf-8'))
guide=next(r for r in man['guides'] if r['name']==job['case'])
records={(r['tile'],r['patch']):r for r in guide['sourcePieces']}
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources()
patches=[]
for key,rec in records.items():
    current,error=sources.source(*key);assert not error
    assert current['file']==rec['file'] and current['sha256']==rec['sha256'],'Current target source changed'
    nb=rec['nativeBoxGlobal'];inter=[max(nb[0],WORLD[0]),max(nb[1],WORLD[1]),min(nb[2],WORLD[2]),min(nb[3],WORLD[3])]
    if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
    art=Image.open(rec['file']).convert('RGB');old=np.asarray(art).copy()
    crop=[inter[0]-FRAME[0],inter[1]-FRAME[1],inter[2]-FRAME[0],inter[3]-FRAME[1]]
    dest=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]]
    art.paste(im.crop(crop),dest[:2]);aa=np.asarray(art)
    pmask=np.zeros((1254,1254),bool);pmask[dest[1]:dest[3],dest[0]:dest[2]]=True
    assert np.array_equal(aa[~pmask],old[~pmask])
    p=D/(STEM+'-'+key[0]+'-'+key[1]+'-provisional-native1254.png');assert not p.exists();art.save(p)
    patches.append({'tile':key[0],'patch':key[1],'file':str(p),'sha256':sha(p),'source':rec['file'],'sourceSha256':rec['sha256'],
                    'nativeFrameWorld':nb,'worldAdoptBox':inter,'nativeAdoptBox':dest,'rawSourceBox':crop,
                    'changedPixels':int(np.any(aa!=old,axis=2).sum()),
                    'coreChangedPixels':int(np.any(aa[115:1139,115:1139]!=old[115:1139,115:1139],axis=2).sum()),
                    'outsideAdoptPixelsChanged':0,'formalAccepted':False,'selected':False})
for rec in patches:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
rebuilt,pieces,missing=sources.extract(FRAME);assert not missing,missing
assert np.array_equal(np.asarray(rebuilt),np.asarray(after))
evidence=[]
for name,box in job['evidenceGuideBoxes'].items():
    p=D/(STEM+'-'+name+'-native.png');assert not p.exists();after.crop(box).save(p)
    evidence.append({'name':name,'file':str(p),'sha256':sha(p),'guideBox':box,
                     'worldBox':[box[0]+FRAME[0],box[1]+FRAME[1],box[2]+FRAME[0],box[3]+FRAME[1]],
                     'dimensions':[box[2]-box[0],box[3]-box[1]],'resampling':False})
save(D/(STEM+'.adoption-check.json'),{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'bounded_candidate_pending_native_perimeter_review','frameWorld':FRAME,'adoptGuideBox':BOX,'adoptWorldBox':WORLD,
 'beforeGuide':job['beforeGuide'],'beforeGuideSha256':sha(job['beforeGuide']),'raw':str(raw),'rawSha256':sha(raw),
 'boundedPreview':str(preview),'boundedPreviewSha256':sha(preview),'outsideAdoptionPixelsChanged':0,
 'nativeCoreReplayExact':True,'patches':patches,'evidence':evidence,'canonicalSelectionsModified':False,
 'resampling':False,'syntheticGeometricRepair':False,'paidApiUsed':False,'formalAccepted':False})
print(json.dumps({'report':str(D/(STEM+'.adoption-check.json')),'nativeCoreReplayExact':True,
                  'patches':[{ 'tile':r['tile'],'patch':r['patch'],'coreChangedPixels':r['coreChangedPixels']} for r in patches]}))
