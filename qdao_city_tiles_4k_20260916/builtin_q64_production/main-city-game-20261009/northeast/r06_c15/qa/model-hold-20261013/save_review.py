from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib
Q=Path(__file__).resolve().parent;T=Q.parent.parent;Z=T.parent;ROOT=Path('D:/work/image')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ev(p):return {'file':str(p),'sha256':sha(p)}
def save(p,d):
 assert p.resolve().is_relative_to(Z.resolve())
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();agent=ev(ROOT/'AGENTS.md');model=ev(ROOT/'docs/IMAGE_MODEL_REQUIREMENT.md')
A=T/'qa/core-baseline/96dc4ad4d4f5c5b82ba2';assembly=read(A/'assembly.json')
assert assembly['validSelectedNativeCount']==9 and not assembly['invalidSelectedSources']
issues=[{'id':'P2-01','priority':'P2','window':'horizontal-p31-p41-join-100pct.png','tilePixelRegion':[300,2850,1000,3180],'finding':'Upper decorative facade panel was redrawn with reversed rail slope; at the horizontal core boundary y3072, panel framing cuts abruptly into the inherited lower panel and cream wall. Requires a bounded native candidate repair after verified GPT Image2.5 is available.'},
{'id':'P2-02','priority':'P2','window':'vertical-p41-p42-join-100pct.png','tilePixelRegion':[1080,3400,1310,3930],'finding':'The new facade at the mixed-guide x230 transition, tile x1139, drops the pale ledge, gold fascia and redwood backing with an abrupt geometric step; needs coherent facade/roof transition repair.'},
{'id':'P2-03','priority':'P2','window':'intersection-r3-c3-100pct.png','tilePixelRegion':[2980,2960,3520,3220],'finding':'The blue roof-tile phase/linework jumps across the lower-right corner boundary; diagonal ribs do not all continue cleanly through y3072. Requires local roof continuation repair.'}]
seams=[]
for s in assembly['seams']:
 if not s['ready']:continue
 name=f"{s['axis']}-{'-'.join(s['sourceIds'])}-join-100pct.png";linked=[i['id'] for i in issues if i['window']==name]
 seams.append({**ev(A/name),'sourceIds':s['sourceIds'],'viewedNativeScale':True,'status':'P2-repair-pending-model-route' if linked else 'no-additional-P2-at-core-boundary','issueIds':linked})
corners=[{**ev(A/f'intersection-r3-c{c}-100pct.png'),'viewedNativeScale':True,'status':'P2-repair-pending-model-route' if c in (1,3) else 'no-additional-P2-at-core-boundary'} for c in range(1,4)]
report={'tile':T.name,'createdAt':now,'status':'partial-saved-cores-reviewed-P2-pending','assembly':ev(A/'assembly.json'),'validSelectedNativeCount':9,'nativeSourceValidation':'9/9 size1254x1254, opaque PNG, source bytes and reference hashes verified by assemble.py','reviewedReadySeamCount':len(seams),'expectedFullTileSeamCount':24,'reviewedCompleteIntersections':corners,'expectedFullTileIntersections':9,'incompleteCornerWindowsAlsoInspected':['intersection-r1-c1-100pct.png','intersection-r2-c1-100pct.png','intersection-r2-c2-100pct.png','intersection-r2-c3-100pct.png'],'incompleteCornerAcceptance':False,'seams':seams,'issues':issues,'internalPassed4kCount':0,'complete4kCandidateCount':0,'formalAcceptedCount':0,'requestedFutureImageModel':'GPT Image 2.5','actualHistoricalModel':None,'actualHistoricalQuality':None,'newGenerationAllowed':False,'reason':'Current built-in image generator exposes no verified explicit GPT Image 2.5 route; paid API not authorized.','authority':[agent,model],'manualPainting':False,'feathering':False,'nativeResampling':False}
save(Q/'partial-native-review.json',report)
image=Image.open(A/'partial-core-baseline.rgba.png');image.thumbnail((1280,1280));image.save(Q/'partial-preview-only.png')
for tid in ['r06_c15','r07_c16','r08_c15','r08_c16']:
 tile=Z/tid;f=tile/'tile-progress.json';d=read(f) if f.exists() else {};sf=tile/'selected-native.json';sel=read(sf) if sf.exists() else {};missing=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in sel]
 audit=[]
 for rec in (tile/'receipts').glob('*.receipt.json'):
  rr=read(rec);src=rr.get('sourceOutputPath');v=rec.name.removesuffix('.receipt.json')
  if src and Path(src).exists():
   local=tile/'native'/(v+'.png');assert local.exists(),f'Un-ingested success: {rec}';assert sha(local)==sha(Path(src));audit.append(ev(local))
 d.update(updatedAt=now,status='new-generation-paused-required-verified-GPT-Image-2.5',selectedCoreCount=len(sel),remainingCoreCount=len(missing),missingSelectedIds=missing,inflightRequests=[],inflightGeneration=None,unsavedSuccessfulOutputs=[],requestedFutureImageModel='GPT Image 2.5',actualModel=None,actualQuality=None,modelRouteVerified=False,builtinOnlyHistorical=True,paidApiAllowed=False,modelRequirementAuthority=[agent,model],lastSuccessfulOutputAudit={'allReceiptSourcesIngested':True,'count':len(audit)},nextStep='Preserve all images and resume missing cores/finite native repairs only after verified GPT Image2.5 route is available without unapproved spending.')
 if tid==T.name:d.update(localPartialReview=str(Q/'partial-native-review.json'),pendingP2Count=len(issues),partialAssemblyManifest=str(A/'assembly.json'),complete4kCandidateCount=0,internalPassed4kCount=0,formalAcceptedCount=0)
 save(f,d)
save(Q/'east-lane-model-hold.json',{'createdAt':now,'owner':'/root/east_finish_20261012','authority':[agent,model],'lastCall':{'tile':'r06_c15','patch':'p21-v20261012','sourceOutputPath':'C:/Users/luyua/.codex/generated_images/01a13318-db2a-7d80-91f8-e770b733098d/exec-6509bf66-2a7d-4d93-bfad-bc96dfc2c428.png','selectedNative':ev(T/'native/p21-v20261012.png')},'inflightRequests':[],'unsavedSuccessfulOutputs':[],'newImageCallsStopped':True,'localOnly':True,'laneSelectedCoreCounts':{'r06_c15':9,'r07_c16':4,'r08_c15':4,'r08_c16':0},'r07_c15':'root-owned; not modified','sharedZoneProgressModified':False,'rootAgRestrictionAcknowledged':True,'paidApiUsed':False,'gitMutations':False})
print(json.dumps({'review':str(Q/'partial-native-review.json'),'hold':str(Q/'east-lane-model-hold.json'),'readySeamsReviewed':len(seams),'completeIntersectionsReviewed':len(corners),'pendingP2':len(issues),'allSuccessfulOutputsSaved':True}))
