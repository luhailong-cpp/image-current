from pathlib import Path
from PIL import Image
import json,hashlib,datetime
Z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p,role=None):
 d=dict(path=str(p),sha256=sha(p))
 if role:d['role']=role
 return d
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
proposed=Z/'records/r05_c12.roof_sol.proposed-selection-v3-plane-20261012.json'
proposal=read(proposed)
raw=[]
for version,status in [('v2','rejected_narrow_rectangle_new_boundary_tile_pitch'),('v3','native_source_for_proposed_consistent_lower_plane')]:
 name=f'r05_c12_p11-p21-loweredge-{version}'
 p=Z/f'native/{name}.png';im=Image.open(p)
 raw.append(dict(**rec(p),nativeSize=list(im.size),status=status,
  generation=rec(Path(str(p)+'.generation.json'),'complete native generation provenance'),
  prompt=rec(Z/f'records/{name}.prompt.txt','actual submitted prompt'),
  actualArguments=rec(Z/f'records/{name}.actual-arguments.json','actual submitted tool parameters and references'),
  receipt=rec(Z/f'records/{name}.receipt.json','actual returned keys/output_hint; PNG payload preserved in source copy')))
details=[]
for name,box in [('right-scroll-detail',[820,660,980,840]),('bottom-lantern-detail',[790,1020,1024,1180])]:
 p=Z/f'qa/r05_c12-loweredge-v3-plane-trial/{name}.native-1to1.png'
 details.append(dict(**rec(p),nativeSize=list(Image.open(p).size),contextCrop=box,operation='exact integer crop, no resize'))
handoff=dict(schemaVersion=1,agent='roof_sol',finishedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 scope='r05_c12 p11/p21 lower roofbridge seam only',status='local_repair_proposed_root_independent_review_pending',
 newBuiltinNativeOutputs=2,newNativeDerivedPatchOutputs=4,allOutputsPreserved=True,
 actualModel=None,actualQuality=None,builtinOnly=True,paidApiUsed=False,currentNetworkPermission='Both normal builtin calls succeeded; no permission-revoked error in this turn',
 rawGenerated=raw,selectionProposal=rec(proposed),selectionDelta=proposal['selectionDelta'],derived=proposal['derived'],
 nativeContribution=proposal['exactContribution'],qa=proposal['qa'],additionalNativeQA=details,
 generatorReview=rec(Z/'qa/r05_c12-loweredge-v3-plane-trial/roof_sol-self-review.json'),
 mechanicalProof=rec(Z/'qa/r05_c12-loweredge-v3-plane-trial/native-contribution-proof.json'),
 rejectionReviews=[rec(Z/'qa/r05_c12-loweredge-v2/roof_sol-self-review.json'),rec(Z/'qa/r05_c12-loweredge-v3/roof_sol-self-review.json')],
 knownLimitations=['Root independent verification of fixed gold right/bottom crop edges remains pending','External west seam cannot be accepted until c11 native neighbor exists; native contribution starts at existing frame edge and covers halo'],
 rawNativePixelsResized=False,artworkPainted=False,artworkFeathered=False,
 workingSelectionChanged=False,sharedProgressChanged=False,historicalFreezeChanged=False,configChanged=False,gitChanged=False,uploadPerformed=False,
 pendingImageGenerationRequests=0,unsavedSuccessfulOutputs=0,formalAccepted=False)
p=Z/'records/roof_sol-handoff-20261012-v1.json';assert not p.exists();p.write_text(json.dumps(handoff,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rec(p)))
