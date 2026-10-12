from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image

out=Path(__file__).parent
qa=out.parent/'current-v10-native-20261013'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'file':str(p),'sha256':sha(p)}
def verify(r): assert sha(r['file'])==r['sha256'],r
reuse=read(qa/'reuse-and-required-review.json')
west=read(qa/'west-proposed-pair-inputs.json')
verify(reuse['candidate'])
candidate=Image.open(reuse['candidate']['file']).convert('RGB')
oldfile=Path(reuse['reusedChecks'][0]['evidence']['file'])
verify(reuse['reusedChecks'][0]['evidence'])
old=read(oldfile)
entries={r['name']:r for r in old['entries']}
reused=[]
for r in reuse['reusedChecks']:
    verify(r); verify(r['evidence'])
    prev=entries[r['name']]
    assert r['sha256']==prev['sha256'] and r['verdict']==prev['verdict']
    reused.append({'name':r['name'],'sha256':r['sha256'],'verdict':r['verdict'],'priorEvidence':r['evidence'],'status':'reused_hash_identical_not_reviewed_again'})

findings={
 'internal-x3072-segment01':('needs_repair','The repaired grout graph is continuous, including the short offset connector. The inherited straight pavement-grain/material division across the c3/c4 boundary remains visible. Geometry alone passed_local_scope; the seam as a whole remains needs_repair.'),
 'internal-y1024-segment03':('passed_local_scope','Blue paving, pale curb borders and the adjoining brown grout lines remain connected across the seam. No new open tip, detached stroke, or hard rectangular material cutoff is confirmed in this current native crop.'),
 'internal-y1024-segment04':('passed_local_scope','The brown diagonal grout network and stone-field texture continue through the reviewed horizontal seam without a confirmed new cut or disconnected contour.'),
 'internal-y3072-segment01':('passed_local_scope','Diagonal floor boundaries and the small closure at the left edge remain continuous. No newly open gap or rectangular patch edge is confirmed in the current crop.'),
 'junction-x3072-y1024':('passed_local_scope','All grout arms at the two visible gold nodes remain connected, and the central material transition follows the stone fields without a confirmed new cut line in this junction crop.')}
changed=[]
for r in reuse['changedChecks']:
    verify(r)
    prev=entries[r['name']]
    expected=candidate.crop(prev['cropLTRB'])
    if prev.get('rotationCCW90'): expected=expected.transpose(Image.Transpose.ROTATE_90)
    assert np.array_equal(np.array(expected),np.array(Image.open(r['file']).convert('RGB'))),r['name']
    verdict,finding=findings[r['name']]
    changed.append({**r,'verdict':verdict,'finding':finding,'actuallyViewed':True,'viewDetail':'original','nativePixelScale':1,'candidateCropPixelMatch':True,'formalAccepted':False})

for key in ['westBase','candidate','westMicroSource']: verify(west[key])
w=Image.open(west['westBase']['file']).convert('RGB')
n=Image.open(west['westMicroSource']['file']).convert('RGB')
band=Image.new('RGB',(640,4096));band.paste(w.crop((3776,0,4096,4096)),(0,0));band.paste(candidate.crop((0,0,320,4096)),(320,0))
for l,t,r,b in west['westMicroROIs']: band.paste(n.crop((l,t,r,b)),(l-627+320,t+2200))
westfindings={
 'west-segment01':('passed_local_scope','Main grout contours meet across the proposed pair without a confirmed gap, duplicate edge, or hard material cutoff.'),
 'west-segment02':('needs_repair','The triangular cap closes geometrically, but its upper edge still cuts the stone grain in a straight material boundary near tile y1139.'),
 'west-segment03':('needs_repair','The newly adopted micro closures remain continuous. Two separate older failures remain: tile y2415 has a small break and hard material cutoff; tile y2927..2956 has a larger offset grout interruption and hard material cutoff. Both are confirmed in additional native crops.'),
 'west-segment04':('passed_local_scope','The proposed micro closure and the remaining main grout lattice are continuous; no new rectangular source boundary is visible in this strip.'),
 'west-junction-1024':('needs_repair','The inherited triangular cap is geometrically closed but has a clear horizontal material cutoff near the bottom-right of this native junction view.'),
 'west-junction-2048':('passed_local_scope','The large grout crossing and surrounding paving continue through the junction without a confirmed open tip or cut material edge.'),
 'west-junction-3072':('passed_local_scope','The narrow vertical grout connector meets both diagonal boundaries. No new source rectangle or detached tip is visible in this local junction.')}
westentries=[]
for r in west['crops']:
    verify(r);name=Path(r['file']).stem
    if 'segment' in name:
        i=int(name[-2:])-1
        expected=band.crop((0,i*1024,640,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90)
    else:
        y=int(name.split('-')[-1]);expected=band.crop((160,y-160,480,y+160))
    assert np.array_equal(np.array(expected),np.array(Image.open(r['file']).convert('RGB'))),name
    verdict,finding=westfindings[name]
    westentries.append({**r,'name':name,'verdict':verdict,'finding':finding,'actuallyViewed':True,'viewDetail':'original','nativePixelScale':1,'proposedPairCropPixelMatch':True,'formalAccepted':False})

details=read(out/'v10-west-known-point-crops.json')
for r in details: verify(r)
report={
 'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/resume_r07_c06_oct13/review_saved_local',
 'candidate':reuse['candidate'],'status':'needs_repair','formalAccepted':False,'internalAccepted':False,'wholeTileAccepted':False,
 'method':'Five changed internal crops and seven west proposed-pair crops actually viewed with view_image detail=original; two additional native crops inspected for the known west defects. The 28 byte-identical prior internal findings were hash-verified and reused, not visually re-reviewed.',
 'metadataInputs':[ref(qa/'reuse-and-required-review.json'),ref(qa/'west-proposed-pair-inputs.json'),ref(out/'local-saved-independent-review.json')],
 'changedInternal':changed,'reusedInternal':reused,
 'internalCounts':{'total':33,'reused':28,'actuallyReviewedChanged':5,'passedOrPassedLocalScope':31,'needsRepair':2},
 'westProposedPair':{'inputs':west,'entries':westentries,'passedLocalScope':4,'needsRepair':3,'westFileModified':False,'acceptanceScope':'Proposed west-half micro selection paired with v10; this does not assert that the approved west tile has been replaced.'},
 'additionalNativeViews':[{**r,'actuallyViewed':True,'viewDetail':'original'} for r in details],
 'remainingIndependentDefectGroups':[
  {'id':'c3c4_inherited_vertical_material','tileRegionApprox':[3057,0,3087,1024],'status':'needs_repair','geometry':'passed_local_scope'},
  {'id':'west_cap_material_cutoff','tileRegionApprox':[0,1024,175,1155],'status':'needs_repair','seenIn':['west-segment02','west-junction-1024'],'internalReusedFailure':'internal-y1024-segment01'},
  {'id':'west_frame_y215','tileEdgeYApprox':2415,'nativeFrameY':215,'status':'needs_repair','finding':'Small grout interruption and hard transverse texture cutoff confirmed in native detail.'},
  {'id':'west_frame_y727_to756','tileEdgeYApprox':[2927,2956],'nativeFrameY':[727,756],'status':'needs_repair','finding':'Offset grout interruption and hard transverse texture cutoff confirmed in native detail.'}
 ],
 'generationPerformed':False,'candidateFilesModified':False,'gitModified':False}
target=out/'v10-changed-independent-review.json';assert not target.exists()
target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':ref(target),'internalCounts':report['internalCounts'],'westCounts':{'passedLocalScope':4,'needsRepair':3}},indent=2))
