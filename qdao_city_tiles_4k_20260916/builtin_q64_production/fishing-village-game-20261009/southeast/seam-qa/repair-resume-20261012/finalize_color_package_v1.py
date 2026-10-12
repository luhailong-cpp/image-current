"""Audit final provisional native art without canonical writes."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, importlib.util
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent; BASE=D.parent.parent
STEM='r12c08-wall-rock-rail-color-finish-v1'
FRAME=[32150,45250,33404,46504];RECT=[350,280,950,830]
WORLD=[32500,45530,33100,46080];RAIL=[32470,45066,32800,45491]
RING=[[350,280,950,344],[350,766,950,830],[350,344,414,766],[886,344,950,766]]
LOCAL=[[350,400,430,530],[840,280,950,390],[600,280,840,344]]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path,obj):
    assert not path.exists(),path
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
color=json.loads((D/(STEM+'.report.json')).read_text(encoding='utf-8'))
prior=json.loads((D/'coordinated-v1-native-evidence-and-review.json').read_text(encoding='utf-8'))
final=np.asarray(Image.open(color['guide']).convert('RGB'))
raw=np.asarray(Image.open(D/'r12c08-wall-rock-conditioned-v2-guide-native1254.png').convert('RGB')).copy()
ids=np.zeros((1254,1254),np.uint8)
for v,boxes in [(6,[RECT]),(7,RING),(8,LOCAL)]:
    art=np.asarray(Image.open(D/f'r12c08-wall-rock-conditioned-v{v}-raw.png').convert('RGB'))
    for x0,y0,x1,y1 in boxes:raw[y0:y1,x0:x1]=art[y0:y1,x0:x1];ids[y0:y1,x0:x1]=v
with np.load(color['combinedField']) as f:
    assert np.array_equal(ids,f['sourceVersionIds'])
    assert np.array_equal(raw,f['sourceNativeBefore'])
    replay=np.uint8(np.clip(np.rint(raw.astype(np.float32)+f['additiveRgb']),0,255))
assert np.array_equal(replay,final)
assert np.array_equal(raw[ids==0],final[ids==0])
assert int(np.max(np.abs(final.astype(np.int16)-raw.astype(np.int16))))==24
for rec in color['patches']:assert sha(rec['file'])==rec['sha256']
spec=importlib.util.spec_from_file_location('native_source_helper',BASE/'review_external_seams.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources();original=helper.Sources()
for rec in color['patches']:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
reconstructed,pieces,missing=sources.extract(FRAME);assert not missing,missing
assert np.array_equal(np.asarray(reconstructed),final)
invariants=[]
for rec in color['patches']:
    art=np.asarray(Image.open(rec['file']).convert('RGB'));source=np.asarray(Image.open(rec['source']).convert('RGB'))
    nb=rec['nativeColorBox'];mask=np.zeros((1254,1254),bool);mask[nb[1]:nb[3],nb[0]:nb[2]]=True
    assert np.array_equal(art[~mask],source[~mask])
    check={'tile':rec['tile'],'patch':rec['patch'],'outsideColorBoxExact':True}
    if rec['patch'] in ['p24','p21']:
        meta,error=original.source(rec['tile'],rec['patch']);assert not error,error
        old=np.asarray(Image.open(meta['file']).convert('RGB'))
        assert np.array_equal(art[115:1139,115:1139],old[115:1139,115:1139])
        check.update(selectedCorePixelsChanged=0,originalSelectedFile=meta['file'],originalSelectedSha256=meta['sha256'])
    invariants.append(check)
evidence=[]
for rec in prior['nativeEvidence']:
    image,pieces,missing=sources.extract(rec['globalBox']);assert not missing
    path=D/(STEM+'-'+rec['id']+'-native.png');assert not path.exists();image.save(path)
    evidence.append({'id':rec['id'],'globalBox':rec['globalBox'],'file':str(path),'sha256':sha(path),
                     'dimensions':list(image.size),'sourcePieces':pieces,'resampling':False})
safety=[]
for rec in prior['sourceSafetyVerification']:
    actual=sha(rec['file'])
    safety.append({'file':rec['file'],'expectedSha256':rec['expectedSha256'],'actualSha256':actual,
                   'unchangedAtPackageTime':actual==rec['expectedSha256']})
assert all(x['unchangedAtPackageTime'] for x in safety),'Canonical external state changed; refresh audit explicitly'
receipts=[]
for v in range(2,9):
    path=D/f'r12c08-wall-rock-conditioned-v{v}.generation-receipt.json'
    receipt=json.loads(path.read_text(encoding='utf-8'))
    assert receipt['status']=='returned_image_success'
    assert sha(receipt['savedOutput'])==receipt['savedOutputSha256']
    for ref in receipt['actualReferences']:assert sha(ref['file'])==ref['sha256']
    receipts.append({'version':v,'receipt':str(path),'receiptSha256':sha(path),
                     'actualReferences':receipt['actualReferences'],'output':receipt['savedOutput'],
                     'outputSha256':receipt['savedOutputSha256'],'status':receipt['status']})
observations={
 'left':'Stone outlines and mortar gaps connect. No clipped replacement rosette remains. A narrow surface density/tone change remains.',
 'top':'Coping face and diagonal stone joints connect; original small foliage tips connect. Rectangular density steps remain in the coping surface.',
 'right':'Coping and face outlines connect to fixed right core. Material boundary at world x33100 remains visible.',
 'bottom':'Rounded boulder and leaf outlines connect to selected lower cores. Horizontal rock texture/density transition at world y46080 remains visible.',
 'inner-left':'No displacement of masonry or plant silhouettes. Narrow material transition between source versions remains visible.',
 'inner-top':'Continuous coping geometry; surface texture zones expose the generated border-strip transition.',
 'inner-right':'Continuous masonry edge; vertical material density/tone boundary remains visible.',
 'inner-bottom':'Rock/leaf geometry connects; material texture transition remains visible.',
 'G4':'Original wall-course height mismatch removed by common generated source across world x32768.',
 'G5':'Original rectangular boulder notch at y46080 removed; outline rounds naturally into unchanged selected lower core.'
}
pixel={'maximumCumulativeRGBChannelChangeFromV6V7V8NativeCombination':24,'range':[-24,24],
       'geometryCoordinateChanges':0,'outsideAdoptionPixelChanges':0,'approvedRailPixelChanges':0,
       'rawNativeCompositionFreshReplayExact':True,'savedFieldFreshReplayExact':True,'fourNativeCoreFreshReplayExact':True}
review={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'geometry_repaired_material_pending','formalAccepted':False,'selected':False,
 'rootGeometryReview':'Root independently viewed native v8 full guide, four outer edges, four inner edges and G5 and accepted geometry before authorizing RGB finish.',
 'agentFinishedColorReview':'Viewed finish v1 full native1254 guide, all four outer and four inner native crops, G4, G5 and cross crop.',
 'edgeObservations':observations,'materialPending':True,
 'materialPendingReason':'Bounded low-frequency RGB correction reduced tone steps but cannot remove visible stone texture density differences. Do not mark material seams passed.',
 'pixelEvidence':pixel,'patchInvariantChecks':invariants,'nativeCoreEvidence':evidence,'sourceSafetyVerification':safety,
 'builtinGenerationReceipts':receipts,'builtinInvocationTimeLog':str(D/'builtin-invocation-times-v1.json'),
 'builtinInvocationTimeLogSha256':sha(D/'builtin-invocation-times-v1.json'),
 'paidApiUsed':False,'imageResampling':False,'imageBlur':False,'imageBlending':False,'syntheticGeometricRepair':False,
 'canonicalSelectionsModified':False,'zoneProgressModified':False,'historicalFreezeModified':False,
 'allOriginalsAndFailedDraftsPreserved':True,
 'nextOwnerStep':'Use as provisional evidence; resolve or explicitly record material density seam before formal coordinated adoption.'}
reviewpath=D/(STEM+'.native-review-v1.json');save(reviewpath,review)
instructions={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'provisional_geometry_repaired_material_pending','formalAccepted':False,
 'allBoxes':'Half-open integer pixel boxes [x0,y0,x1,y1], no resampling.',
 'nativeSize':[1254,1254],'nativeCoreBox':[115,115,1139,1139],
 'guideFrameWorld':FRAME,'guide':color['guide'],'guideSha256':color['guideSha256'],
 'combinedRgbField':color['combinedField'],'combinedRgbFieldSha256':color['combinedFieldSha256'],
 'nativeSourceReplay':color['sourceReplay'],'nativeSourceReplaySha256':color['sourceReplaySha256'],
 'colorReport':str(D/(STEM+'.report.json')),'nativeReview':str(reviewpath),
 'wallRockWorldBox':WORLD,'railWorldBox':RAIL,
 'requiredCoordinatedCoreCandidates':['r12_c08/p14','r12_c09/p11'],
 'haloOnlyCandidates':['r12_c08/p24','r12_c09/p21'],
 'copyProcedure':[
  'Preserve canonical files and selections. Package is provisional and not formally accepted.',
  'For owner-authorized adoption or review, copy four complete final native1254 PNGs to newly versioned destinations. Keep dimensions/core box exactly; verify SHA256.',
  'Coordinate p14 and p11 together: wall/rock and approved rail both cross x32768. p14-only paste recreates discontinuity.',
  'p24/p21 contain halo-only updates; their selected 1024-square cores are exactly unchanged.',
  'For bounded paste instead of complete candidate copies, use only listed native intersections with exact integer coordinates. Keep recorded base p14 source and approved rail.',
  'Do not adopt raw generation whole frames: raw v6/v7/v8 used only in recorded bounded rectangles, followed by saved additive RGB field.',
  'Record unresolved stone density seams as materialpending; geometry repair alone does not establish formal seam pass.'
 ],
 'patches':color['patches'],'nativePixelEvidence':pixel,'nativeCoreEvidence':evidence,'sourceSafetyVerification':safety,
 'selectionAuthority':'Root coordinator only; this subagent did not change canonical selection or progress.',
 'materialPending':True,'paidApiUsed':False}
save(D/(STEM+'.adoption-instructions.json'),instructions)
note=D/(STEM+'.handoff.txt');assert not note.exists()
note.write_text('Provisional G4/G5 geometry repair with bounded RGB finish.\n'
 'Original wall course mismatch and rectangular rock notch repaired. Texture density boundaries remain visible: materialpending=true; formalAccepted=false.\n'
 'Fresh raw source composition, RGB field and four native core replay all exact. Maximum cumulative channel delta=24; outside box and approved rail changes=0.\n'
 'Coordinate r12_c08/p14 and r12_c09/p11. p24/p21 are halo-only with unchanged selected cores.\n'
 'Wall/rock world [32500,45530,33100,46080]; approved rail world [32470,45066,32800,45491].\n'
 'See adoption-instructions.json for final files/hashes/native boxes. Canonical selection and old freeze hashes unchanged.\n',encoding='utf-8')
print(json.dumps({'review':str(reviewpath),'adoptionInstructions':str(D/(STEM+'.adoption-instructions.json')),
                  'freshReplayExact':True,'materialPending':True,'formalAccepted':False,'fourFinalPatches':len(color['patches'])}))
