from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent;R=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):return np.array(Image.open(p).convert('RGB'))
def save(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
direct=['p01_01','p01_02.edge-v2','p01_03','p01_04.edge-v2','p01_04.groove-v3']
records=[]
for rp in sorted((D/'native').glob('*.png.generation.json')):
 r=read(rp);assert sha(r['file'])==r['sha256'];assert sha(r['prompt'])==r['promptSha256'];assert Image.open(r['file']).size==(1254,1254)
 for ref in r['references']:assert sha(ref['file'])==ref['sha256']
 assert read(r['receipt'])['status']=='returned_image';assert r['actualModel'] is None and r['actualQuality'] is None
 records.append({'id':r['id'],'record':str(rp),'recordSha256':sha(rp),'native':r['file'],'nativeSha256':r['sha256'],'prompt':r['prompt'],'promptSha256':r['promptSha256'],'receipt':r['receipt'],'receiptSha256':sha(r['receipt']),'directContributorToFinalCandidate':r['id'] in direct})
assert len(records)==8
failure=read(D/'receipts/p01_02.attempt-1.too-many-references.json')
assert sha(D/'prompts/p01_02.attempt-1.prompt.txt')==failure['requestSnapshot']['promptSha256']
original_sources=[]
for c in range(1,5):
 p=T/'native'/f'p01_{c:02d}.png';r=read(p.with_suffix('.png.generation.json'));assert sha(p)==r['sha256'];original_sources.append({'file':str(p),'sha256':sha(p)})
cp=D/'output/v5/r11-p01.repaired.context.png';core=D/'output/v5/r11-p01.repaired.core.png';orig=T/'borders/r11-p01.original.context.png';north=T/'borders/r10-south-native-overlap.png'
a=arr(cp);o=arr(orig);b=arr(north);assert a.shape==(1254,4326,3);assert np.array_equal(a[:116],b[:116]);assert np.array_equal(a[1024:],o[1024:]);assert np.array_equal(arr(core),a[115:1139,115:4211])
r10=R/'r10_c05/repairs/output/r10_c05.repaired.candidate.png';assert sha(r10)=='f228d0e07c4ed329bdcce87a46abb0ddeb48c9688dab1d86b33456051797ecad'
candidate={'context':{'file':str(cp),'sha256':sha(cp),'pixels':[4326,1254]},'core':{'file':str(core),'sha256':sha(core),'pixels':[4096,1024]},'contextWorldBox':[16269,40845,20595,42099],'coveredCoreWorldBox':[16384,40960,20480,41984]}
integration={'method':'override assembled first-row context; do not switch raw native selection alone','optionA':'Use candidate context as the first native row strip before vertical joining with the lower rows. Its bottom230 exactly matches the prior first-row strip, so existing lower-row overlap ownership remains compatible.','optionB':'If the existing full native context was assembled using the unchanged original first-row sources, replace only context box [0,0,4326,1024] from candidate context. Keep rows y>=1024 from the existing full context, including the existing row1/row2 blend. Then crop the full context normally.','doNotOverlayFull4096x1024CoreOntoAlreadyAssembledFullTile':True,'reason':'The last115 pixels of the 1024px row core overlap the next-row blend. Overwriting a full core strip could replace that established join.','originalFirstRowContext':{'file':str(orig),'sha256':sha(orig)},'northAnchor':{'file':str(north),'sha256':sha(north)},'bottom230Exact':True}
qa={'status':'internally_reviewed_candidate_ready_for_parent_integration','formalAccepted':False,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':candidate,'reviewedVisuals':['all four north-boundary crops at native scale','three internal vertical seam crops at native scale','full first-row candidate','full-width restored groove and enlarged-area pixel crop','lower native overlap and transition'], 'findings':{'northLeafContinuity':'passed: no leaf break at actual tile boundary','northStoneContinuity':'passed: previous irregular tonal band removed; broad stone shading remains natural','internalColorSeams':'passed: obvious warm/cool polygon joins at x1024 and x3072 removed; x2048 joins cleanly','stairGeometry':'passed after final native groove correction; no visible 3px notch in the repaired groove','bottomCompatibility':'passed: bottom230 pixel-exact to old row strip','globalLayout':'preserved: red flag, leaves, parapet and stair count retained'},'limitations':['Only the first native row has been reviewed here; this is not a full 4096x4096 tile.','East/west external tile neighbors remain for the owning parent review.','Actual tool model and quality were not disclosed; recorded null.'],'mechanicalProof':{'nativeEightOutputsAre1254Square':True,'r10Sha256Unchanged':sha(r10),'allOriginalFirstRowNativeHashesUnchanged':True,'north116EqualsNativeNeighbor':True,'bottom230EqualsOriginalRow':True,'resampling':False,'colorAdjustment':False,'geometryWarping':False},'integration':integration,'counts':{'successfulBuiltinImageOutputs':8,'preflightReferenceCountErrors':1,'quotaErrors':0,'directNewNativeContributorsToCandidate':5,'intermediateOrReferenceOnlyNativeOutputs':3,'spatialCorePatchesNewlyCovered':0,'firstRowSpatialCorePatchesRepaired':4},'records':records,'originalSources':original_sources,'rejectedComposites':[{'version':'v3','reason':'local patch repair moved the notch to its right edge'},{'version':'v4','reason':'old native groove still contained a small notch and a color stripe'}],'selectedOfficially':False,'writesToOfficialSelection':False,'writesToProgress':False}
save(D/'qa/final-visual-review.json',qa)
save(D/'selection-proposed-final.json',{'status':'recommended_composite_pending_parent_integration','candidate':candidate,'integration':integration,'directNativeContributors':direct,'evidence':str(D/'qa/final-visual-review.json'),'formalAccepted':False,'changesAlreadyAppliedToOfficialSelection':False})
save(D/'production-result.json',{'status':qa['status'],'candidate':candidate,'counts':qa['counts'],'review':str(D/'qa/final-visual-review.json'),'selectionProposal':str(D/'selection-proposed-final.json'),'actualModel':None,'actualQuality':None,'r10Unchanged':True,'currentOfficialSelectionUnmodifiedByThisWorker':True})
print(json.dumps({'status':qa['status'],'candidate':candidate,'counts':qa['counts'],'review':str(D/'qa/final-visual-review.json')},ensure_ascii=False,indent=2))
