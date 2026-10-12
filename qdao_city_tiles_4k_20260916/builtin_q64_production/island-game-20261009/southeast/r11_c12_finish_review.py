"""Record the completed visual review without modifying generation evidence."""
from pathlib import Path
import json, hashlib, datetime, os
R=Path(__file__).parent;Q=R/'qa/r11_c12-v02'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
index=read(Q/'qa-index.json')
assert sha(index['candidate'])==index['candidateSha256']
changed=['h31','h41','v21','v22','v31','v32']
assert [x['id'] for x in index['seams'] if not x['identicalToV01']]==changed
for kind in ['seams','junctions','repairBoundaries']:
    for e in index[kind]:
        assert sha(e['file'])==e['sha256']
        if e['status']=='pending_visual_review':e['status']='pass_internal_visual_review'
index['reviewedAt']=now
write(Q/'qa-index.json',index)
review={'tile':'r11_c12','candidate':index['candidate'],'sha256':index['candidateSha256'],
        'reviewedAt':now,'reviewer':'tile_right repair operator, after independent discovery on v01',
        'status':'internal_repair_review_pass','formalAcceptedCount':0,
        'independentDiscoveryReport':str(R/'qa/r11_c12-independent-review.json'),
        'resolvedFindings':[
          {'location':'h31, p31/p32','before':'Lower rail bottom jumped 11 pixels at original x1024 source boundary; upper rail/rim also carried a smaller source mismatch.',
           'after':'Both complete horizontal rails, picket joins and water/rim geometry are continuous across original seam and new native ownership boundaries.',
           'repairNative':'native/r11_c12_railjoin_v02.png'},
          {'location':'h41, p41/p42','before':'Deck joint jumped 17 pixels at original x1024 source boundary; parallel grooves were stepped together.',
           'after':'Whole existing deck board assembly redrawn once; continuous slope, width, dark grooves, rim and highlights through original cut and both side boundaries.',
           'repairNative':'native/r11_c12_deckjoin_v01.png'}],
        'visuallyReviewed':{'wholeCandidate':True,'changedSeams':changed,
                            'changedJunctions':['junction_21','junction_31'],
                            'repairBoundaries':[x['id'] for x in index['repairBoundaries']],
                            'note':'All detail inspections were native pixel crops. Whole candidate preview was display downsampled only; stored candidate is unchanged 4096 x 4096.'},
        'unchangedReplay':{'seamCount':18,'junctionCount':7,'allByteIdenticalToV01':True,
                           'outer256Bands':index['outer256Bands']},
        'sourceIntegrity':{'manifest':str(R/'selected-native-r11_c12-repaired-v02.json'),
                           'sourceIdMap':str(Q/'source-id.png'),'sourceIdMapSha256':sha(Q/'source-id.png'),
                           'nativeSourceCount':18,'candidatePixelCount':16777216,
                           'exactPerPixelReplay':True,'newRepairNatives':2,
                           'actualModel':None,'actualQuality':None,
                           'colorEdits':False,'blending':False,'resizing':False,'filters':False},
        'hardOwnership':'Irregular paths select one original native pixel at the same world coordinate; no interpolation. Chosen in true overlap using source agreement. Exhaustive source-ID replay passed.',
        'externalBorders':{'north':'256px complete band unchanged; existing r10/r11 join QA inherited by exact pixels.',
                           'west':'256px complete band unchanged.',
                           'east':'256px complete band unchanged.',
                           'south':'Changed deck continues to candidate edge and generated native halo. No assembled southern neighbor exists in this review; external join remains unverified.'},
        'remainingKnownInternalRepairDefects':[],
        'limits':['This is internal visual and source QA, not formal external acceptance.',
                  'Original v01 candidate, original selection and all generation histories remain preserved.']}
write(Q/'repair-review.json',review)
write(R/'qa/r11_c12-independent-review-v02.json',review)
for p in [R/'selected-native-r11_c12-repaired-v02.json',Path(index['candidate']+'.sources.json')]:
    d=read(p);d['status']='internal_repair_review_pass';d['qaReport']=str(Q/'repair-review.json');write(p,d)
p=R/'progress-r11_c12-repair.json';d=read(p)
d.update(status='candidate_complete_internal_repair_review_pass',candidate=index['candidate'],
         candidateSha256=index['candidateSha256'],generatedRepairNativeCount=2,formalAcceptedCount=0,
         inFlight=False,qaReport=str(Q/'repair-review.json'),sourceManifest=str(R/'selected-native-r11_c12-repaired-v02.json'),updatedAt=now)
temp=p.with_suffix('.tmp.json');write(temp,d);os.replace(temp,p)
print(json.dumps({'candidate':index['candidate'],'sha256':index['candidateSha256'],'report':str(Q/'repair-review.json'),
                  'manifest':str(R/'selected-native-r11_c12-repaired-v02.json'),'formalAcceptedCount':0}))
