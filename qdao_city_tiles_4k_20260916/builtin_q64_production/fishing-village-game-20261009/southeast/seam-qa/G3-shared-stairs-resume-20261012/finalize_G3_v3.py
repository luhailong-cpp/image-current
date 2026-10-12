"""Package provisional exact native G3 v3 art without canonical writes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,importlib.util
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;BASE=D.parent.parent;STEM='G3-bottom-conditioned-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):
    assert not p.exists(),p
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
check=json.loads((D/(STEM+'.adoption-check.json')).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('native_core_sources',BASE/'review_external_seams.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources()
snapshots=[]
for tile in ['r12_c09','r12_c10']:
    current=BASE/tile/'selected-patches.json';dest=D/(STEM+'-'+tile+'-current-selection-snapshot.json')
    assert not dest.exists();shutil.copy2(current,dest)
    selection=json.loads(current.read_text(encoding='utf-8-sig'))
    snapshots.append({'tile':tile,'canonical':str(current),'canonicalSha256':sha(current),'snapshot':str(dest),
                      'snapshotSha256':sha(dest),
                      'wallEntriesPreservedAsRead':{p:selection['patches'][p] for p in ['p11','p21']} if tile=='r12_c09' else None})
final=np.asarray(Image.open(check['boundedPreview']).convert('RGB'))
replay=Image.open(D/'G3-bottom-conditioned-v1-guide-native1254.png').convert('RGB')
mask=Image.open(D/'G3-bottom-conditioned-v2-adopt-mask-native1254.png').convert('L')
replay.paste(Image.open(D/'G3-bottom-conditioned-v2-raw.png').convert('RGB'),(0,0),mask)
replay.paste(Image.open(D/'G3-bottom-conditioned-v3-raw.png').crop([925,680,1005,760]),(925,680))
assert np.array_equal(np.asarray(replay),final)
ids=np.load(check['nativeSourceReplay'])['sourceVersionIds']
base=np.asarray(Image.open(D/'G3-bottom-conditioned-v1-guide-native1254.png').convert('RGB'))
assert np.array_equal(base[ids==0],final[ids==0])
patches=[]
for rec in check['patches']:
    current,error=sources.source(rec['tile'],rec['patch']);assert not error,error
    assert current['file']==rec['source'],(current['file'],rec['source'])
    assert current['sha256']==rec['sourceSha256'],'Target patch current source changed externally'
    assert sha(rec['file'])==rec['sha256']
    before=np.asarray(Image.open(rec['source']).convert('RGB'));after=np.asarray(Image.open(rec['file']).convert('RGB'))
    out=dict(rec);out['totalChangedPixelsFromRecordedCurrentSource']=int(np.any(after!=before,axis=2).sum())
    out['totalCoreChangedPixelsFromRecordedCurrentSource']=int(np.any(after[115:1139,115:1139]!=before[115:1139,115:1139],axis=2).sum())
    out['currentSelectedSourceUnchanged']=True
    out['pasteAuthority']='Exact v2 native source under polygon mask plus exact v3 native rectangle; full native copy preferred.'
    patches.append(out)
for rec in patches:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
rebuilt,pieces,missing=sources.extract(check['frameWorld']);assert not missing
assert np.array_equal(np.asarray(rebuilt),final)
evidence=[]
for name,world in {'G3-core-cross':[36317,47019,37179,47419],
                   'internal-row-cross':[36360,46976,37065,47232],
                   'external-column-cross':[36736,47019,36992,47419]}.items():
    image,pieces,missing=sources.extract(world);assert not missing
    path=D/(STEM+'-'+name+'-native.png');assert not path.exists();image.save(path)
    evidence.append({'name':name,'worldBox':world,'file':str(path),'sha256':sha(path),
                     'dimensions':list(image.size),'sourcePieces':pieces,'resampling':False})
metrics=[]
for name,path in [('original',D/'G3-bottom-conditioned-v1-guide-native1254.png'),('v3',Path(check['boundedPreview']))]:
    a=np.asarray(Image.open(path).convert('RGB'));rows=[]
    for y in [626,627,764,765,766]:
        m=(a[y,:,0]<180)&(a[y,:,1]<112)&(a[y,:,2]<75)
        xs=np.flatnonzero(m&(np.arange(1254)>350));groups=np.split(xs,np.flatnonzero(np.diff(xs)>1)+1)
        rows.append({'guideY':y,'worldY':y+46592,'darkRunsGuideX':[[int(g[0]),int(g[-1])] for g in groups if len(g)>=3]})
    metrics.append({'source':name,'file':str(path),'sha256':sha(path),'rows':rows})
review={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'geometry_candidate_material_pending','formalAccepted':False,'internalReady':False,
 'agentViewed':['v3 full composition via native band crop','four main perimeter native crops','four v3 local perimeter native crops','G3 center native crop'],
 'rootIndependentReview':'Root viewed v3 G3-native and local-bottom-native: original y47219 and new bottom main outlines connect, no structural displacement found; root left/right/top review remains owner step.',
 'observations':{'G3':'Original horizontal plank-gap cliff at y47219 removed. Major diagonal groove row centers continue normally across y47218/47219.',
   'bottom':'Major grooves connect across y47357/47358; dark runs advance naturally by1..2px per row instead of hard lateral jump.',
   'left':'No new main plank gap is severed; existing wood texture meets generated wood with material density/tone transition.',
   'top':'Stone riser remains exact outside wood mask. New upper wood ends beneath its diagonal shadow; local grain/texture transition remains visible.',
   'right':'Major diagonal grooves remain connected. V3 removed prior abrupt thin groove at v2 right edge; faint grain termination and80-square material patch remain visible.',
   'v3LocalFourEdges':'No larger plank gap shifted; fine grain density/color changes remain visible.'},
 'materialPending':True,'materialPendingReason':'Fine linear grain/density and local RGB boundary remains; no color field applied in this G3 package.',
 'sourceReplayExact':True,'fourNativeCoreReplayExact':True,'outsideUnionChangedPixels':0,
 'canonicalSelectionsModifiedByThisAgent':False,'currentSelectionSnapshots':snapshots,
 'currentFourTargetPatchSourcesUnchanged':True,'allOriginalsAndRejectedV1Preserved':True,
 'nativePixelRowEvidence':metrics,'nativeCoreEvidence':evidence,
 'paidApiUsed':False,'imageResampling':False,'imageBlur':False,'syntheticGeometricRepair':False}
reviewpath=D/(STEM+'.native-review-v1.json');save(reviewpath,review)
instructions={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'provisional_geometry_candidate_material_pending','formalAccepted':False,'internalReady':False,
 'nativeSize':[1254,1254],'coreNativeBox':[115,115,1139,1139],
 'worldFrame':check['frameWorld'],'boundingWorldBox':[36360,47065,37065,47358],
 'v2NaturalAdoptionPolygonGuide':[[300,602],[970,473],[970,765],[300,765]],
 'v2NaturalAdoptionPolygonWorld':[[36360,47194],[37030,47065],[37030,47357],[36360,47357]],
 'v2Mask':check['v2AdoptMask'],'v2MaskSha256':sha(check['v2AdoptMask']),
 'maskRasterization':'Exact saved L-mode mask is authority; polygon includes boundary pixels. Bounding boxes are half-open.',
 'v3LocalAdoptionGuideBox':[925,680,1005,760],'v3LocalAdoptionWorldBox':[36985,47272,37065,47352],
 'nativeSourceReplay':check['nativeSourceReplay'],'nativeSourceReplaySha256':check['nativeSourceReplaySha256'],
 'patches':patches,'nativeReview':str(reviewpath),'adoptionCheck':str(D/(STEM+'.adoption-check.json')),
 'copyProcedure':[
  'Keep package provisional with materialpending=true/internalReady=false until owner perimeter/material review.',
  'Copy these four final native1254 PNGs to new versioned destinations, unchanged in size, and verify SHA256. Exact full native copy is safer than manually rasterizing the natural wood mask.',
  'Coordinate r12_c09 p24/p34 and r12_c10 p21/p31 together. All four selected cores have some changes under the diagonal wood mask; p24/p21 are not halo-only in v3.',
  'Preserve all other current selected entries, particularly root-adopted wall r12_c09 p11/p21 captured in the current selection snapshot.',
  'If using bounded paste, replay exact v2 raw under saved native mask then v3 raw crop [925,680,1005,760] at the same guide coordinates, and translate recorded intersections into each native patch. Do not paste generated whole frame.',
  'Adopt no whole old selection manifest. Update only these four patch entries after owner review; keep metadata/progress under root authority.'
 ],
 'sourceFilesStillCurrent':True,'currentSelections':snapshots,'outsideUnionChangedPixels':0,
 'pixelReplayExact':True,'fourCoreReplayExact':True,'materialPending':True,'canonicalModifiedByThisAgent':False,
 'generationReceipts':[str(D/f'G3-bottom-conditioned-v{v}.generation-receipt.json') for v in [1,2,3]],
 'paidApiUsed':False,'allFailedDraftsPreserved':True}
save(D/(STEM+'.adoption-instructions.json'),instructions)
print(json.dumps({'instructions':str(D/(STEM+'.adoption-instructions.json')),'review':str(reviewpath),
 'allFourCurrentSourcesUnchanged':True,'freshReplayExact':True,
 'coreChangedPixels':[{ 'tile':p['tile'],'patch':p['patch'],'pixels':p['totalCoreChangedPixelsFromRecordedCurrentSource']} for p in patches]}))
