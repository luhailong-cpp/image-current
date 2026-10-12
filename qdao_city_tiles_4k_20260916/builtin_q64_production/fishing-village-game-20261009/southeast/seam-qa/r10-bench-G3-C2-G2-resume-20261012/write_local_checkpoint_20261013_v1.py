from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib,importlib.util
D=Path(__file__).resolve().parent;QA=D.parent;BASE=QA.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,obj):
 assert not p.exists(),p;p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
dirs=[QA/'repair-resume-20261012',QA/'G3-shared-stairs-resume-20261012',D]
receipts=[];errors=[];unique={}
for folder in dirs:
 for rp in sorted(folder.glob('*.generation-receipt.json')):
  r=read(rp);raw=Path(r['savedOutput']);orig=Path(r['originalBuiltinOutput']);request=Path(r['request'])
  checks={'savedOutputExists':raw.is_file(),'originalOutputExists':orig.is_file(),'requestExists':request.is_file()}
  if raw.is_file():checks['savedOutputHashMatches']=sha(raw)==r['savedOutputSha256'];checks['native1254']=Image.open(raw).size==(1254,1254)
  if raw.is_file() and orig.is_file():checks['savedOutputByteExactToBuiltinOriginal']=sha(raw)==sha(orig)
  if request.is_file() and r.get('requestSha256'):checks['requestHashMatches']=sha(request)==r['requestSha256']
  refchecks=[]
  for ref in r.get('actualReferences',[]):
   p=Path(ref['file']);ok=p.is_file() and sha(p)==ref['sha256'];refchecks.append({'file':str(p),'hashMatches':ok})
   if not ok:errors.append({'receipt':str(rp),'reference':str(p),'error':'reference hash mismatch/missing'})
  if not all(checks.values()):errors.append({'receipt':str(rp),'checks':checks})
  entry={'receipt':str(rp),'receiptSha256':sha(rp),'originalBuiltinOutput':str(orig),'savedOutput':str(raw),'savedOutputSha256':r['savedOutputSha256'],'actualModel':r.get('actualModel'),'modelEvidence':'Tool did not return actual model metadata','checks':checks,'actualReferences':refchecks}
  receipts.append(entry);unique[str(orig).replace('\\','/').lower()]=entry
audit={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'receiptCount':len(receipts),'uniqueBuiltinReturnedImages':len(unique),'derivedReceiptsReuseExistingImage':len(receipts)-len(unique),'allReturnedImagesSavedByteExact':not errors,'inFlightRequests':[],'unsavedReturnedImages':[],'errors':errors,'receipts':receipts,'paidApiUsed':False,'canonicalSelectionsModifiedByThisAgent':False}
ap=D/'returned-image-archive-audit-20261013-v1.json';save(ap,audit)
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);sources=helper.Sources()
items=[
 {'id':'eastG2','package':D/'eastdeck-G2-final-v5.adoption-instructions.json','geometry':'Root independently reviewed main gaps, shallow parallel curves and final sides; geometry candidate passes. Not selected pending final material package.','material':'PENDING: strong rectangular tone and woodgrain-density differences remain at main and five endpoint adoption boundaries.','overallWorldBox':[32581,38135,33056,39025],'selectedByRoot':False,'internalReady':False,'formalAccepted':False},
 {'id':'C2','package':D/'bench-C2-final-v6.adoption-instructions.json','geometry':'Local main floor gaps and gold-rim silhouette show no new adopted discontinuities. Original small upper crossbar step at x32371 is untouched and still open; root independent review pending.','material':'PENDING: floor and gold-face shadow cut softened/removed; local tone/density boundaries remain.','overallWorldBox':[32290,40556,32633,41015],'selectedByRoot':False,'internalReady':False,'formalAccepted':False},
 {'id':'benchG3','package':None,'latestRejectedReceipt':D/'bench-G3-left-conditioned-v8.generation-receipt.json','latestRejectedReview':D/'bench-G3-left-conditioned-v8.native-review-v1.json','geometry':'OPEN: v1..v8 rejected. Latest single upper contour v8 has15px right endpoint step at worldx31165 (insidegoldy40589 versus outsidey40604). No bench replacement approved.','material':'PENDING, subordinate to geometry repair; rectangular tone/woodgrain differences also persist.','latestAttemptWorldBox':[31070,40544,31165,40635],'selectedByRoot':False,'internalReady':False,'formalAccepted':False},
 {'id':'wallG4G5','package':QA/'repair-resume-20261012/r12c08-wall-rock-rail-color-finish-v1.adoption-instructions.json','rootAdoption':QA/'repair-resume-20261012/root-wall-joint-adoption-20261012.json','geometry':'Root independently accepted repaired wall courses/rock notch and adopted four exact native candidates; approved rail preserved.','material':'PENDING: stone-face texture-density frames remain. Prior bounded additive RGB field maximum cumulative channel24; no new RGB field in this checkpoint.','overallWorldBox':[32500,45530,33100,46080],'approvedRailWorldBox':[32470,45066,32800,45491],'selectedByRoot':True,'internalReady':False,'formalAccepted':False},
 {'id':'stairsG3','package':QA/'G3-shared-stairs-resume-20261012/G3-bottom-conditioned-v3.adoption-instructions.json','rootAdoption':QA/'G3-shared-stairs-resume-20261012/root-G3-joint-adoption-20261012.json','geometry':'Root independently accepted major plank grooves and four main/local boundaries; adopted all four exact native candidates.','material':'PENDING: small woodgrain endpoint and density rectangles remain.','overallWorldBox':[36360,47065,37065,47358],'selectedByRoot':True,'internalReady':False,'formalAccepted':False}
]
for item in items:
 p=item.get('package')
 if p:
  item['package']=str(p);item['packageSha256']=sha(p);pkg=read(p);ps=[]
  for r in pkg['patches']:
   f=Path(r['file']);assert f.exists() and sha(f)==r['sha256'];cur,error=sources.source(r['tile'],r['patch']);assert not error
   ps.append({'tile':r['tile'],'patch':r['patch'],'file':str(f),'sha256':r['sha256'],'packageNativeDimensions':list(Image.open(f).size),'currentSelectedSource':cur['file'],'currentSelectedSourceSha256':cur['sha256'],'currentCoreMatchesCandidate':bool(np.array_equal(np.asarray(Image.open(cur['file']).convert('RGB'))[115:1139,115:1139],np.asarray(Image.open(f).convert('RGB'))[115:1139,115:1139]))})
  item['patches']=ps
  npz=pkg.get('nativeSourceReplay') or pkg.get('replayNpz')
  if npz:
   npz=Path(npz);item['replayNpz']=str(npz);item['replayNpzSha256']=sha(npz);item['replayNpzKeys']=list(np.load(npz).files)
  for key in ['nativeSourceReplayExact','nativeCoreReplayExact','pixelReplayExact','fourCoreReplayExact','outsideUnionChangedPixels']: 
   if key in pkg:item[key]=pkg[key]
 if item.get('rootAdoption'):
  p=item['rootAdoption'];item['rootAdoption']=str(p);item['rootAdoptionSha256']=sha(p)
 for key in ['latestRejectedReceipt','latestRejectedReview']:
  if key in item:p=item[key];item[key]=str(p);item[key+'Sha256']=sha(p)
modeldocs=[]
for p in [Path('D:/work/image/AGENTS.md'),Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')]:
 modeldocs.append({'file':str(p),'sha256':sha(p),'readAtUtc':datetime.now(timezone.utc).isoformat(),'currentMeaning':'2026-10-13 clarification: free/existing2.5 preferred; existingbuiltin2.0 permitted, unknown actual model not relabelled'})
checkpoint={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'local_checkpoint_only_no_new_generation','parentLatestTask':'Only local archival/QA/checkpoint; no generation, Git, payment, installation or route investigation.','currentModelDocuments':modeldocs,'modelRouteActuallyUsed':'builtin image_gen.imagegen','actualModelEvidence':'All saved calls report actualModel=null; no model identity inferred.','inFlightRequests':[],'unsavedReturnedImages':[],'archiveAudit':str(ap),'archiveAuditSha256':sha(ap),'uniqueReturnedImageCount':len(unique),'archivePassed':not errors,'items':items,'newRgbFieldApplied':False,'rgbDecision':'No further RGB field applied because open issues include grain-density frames and/or contour faults; color cannot finish them. Existing approved wall RGB24 package preserved unchanged.','canonicalSelectionsModifiedByThisAgent':False,'gitOperations':False,'paidApiUsed':False,'installationPerformed':False}
cp=D/'joint-repair-checkpoint-20261013-v1.json';save(cp,checkpoint)
lines=['Local repair checkpoint 2026-10-13','No generation in flight; no returned image unsaved. '+str(len(unique))+' unique builtin returned images verified byte-exact; '+str(len(receipts))+' receipts including2 mechanical reuse variants.','Actual model metadata unavailable for all calls; no image labelled2.5/2.0.','No new RGB field: density and geometry faults remain open. Existing wall bounded RGB24 preserved unchanged.','']
for item in items:
 lines += [item['id']+': '+item['geometry'],'Material: '+item['material'],'Package: '+str(item.get('package') or item.get('latestRejectedReview')),'']
lines += ['No canonical/Git/paid/installation changes by this agent. Root model documents now permit existing builtin fallback, but current parent task remained local-only.']
tp=D/'joint-repair-checkpoint-20261013-v1.txt';assert not tp.exists();tp.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'checkpoint':str(cp),'audit':str(ap),'uniqueImages':len(unique),'receipts':len(receipts),'errors':errors,'itemPatchCoreMatches':{i['id']:[{'tile':r['tile'],'patch':r['patch'],'currentCoreMatchesCandidate':r['currentCoreMatchesCandidate']} for r in i.get('patches',[])] for i in items}}))

