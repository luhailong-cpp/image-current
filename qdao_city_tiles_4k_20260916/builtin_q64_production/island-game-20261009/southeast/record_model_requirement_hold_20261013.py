from workflow import *
policy=Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')
assert policy.exists()
requirement={'requiredImageModel':'GPT Image 2.5','authorityFile':str(policy),'authoritySha256':sha(policy),'verifiedSelectableRouteAvailable':False,'builtinToolExplicitModelSelectionAvailable':False,'builtinActualModelDisclosed':False,'paidApiAuthorized':False,'newGenerationAllowed':False,'existingAssetsPreserved':True,'localInventoryAssemblyAndReviewAllowed':True,'reason':'No available approved route explicitly selects and verifies GPT Image 2.5. Do not silently fall back to an unspecified builtin model.','recordedAtUtc':now(),'scope':'All new image generation and image-edit/repair requests, including after computer migration.'}
resume=read(ROOT/'production-resume-20261012.json');counts=resume['counts']
missing=resume['remainingWithoutFullCandidate'];pending=resume.get('pendingCandidates',[])
queue={'updatedAtUtc':now(),'generationRequirement':requirement,'counts':counts,'missingFullCandidateTiles':missing,'fullCandidatesPendingRepairOrReview':pending,'activePartialTiles':{},'mapComplete':False,'formalAccepted':False,'previousNetworkError':'application network permission was revoked','newImageRequestsSubmittedAfterRequirement':0}
for tid in ['r13_c11','r13_c13','r14_c11','r14_c12','r14_c13','r08_c10','r09_c10']:
 f=ROOT/f'progress-{tid}.json'
 if not f.exists():continue
 d=read(f);selected=d.get('workingVersions',d.get('selectedVersions',{}));existing=[]
 for rc in sorted(selected):
  src=ROOT/'native'/f'{tid}_p{rc}_{selected[rc]}.png'
  if src.exists():existing.append({'coordinate':rc,'version':selected[rc],'file':str(src),'sha256':sha(src)})
 expected=[f'{r}{c}' for r in range(1,5) for c in range(1,5)]
 queue['activePartialTiles'][tid]={'selectedCoreCount':len(existing),'selectedOriginals':existing,'missingCoordinates':[rc for rc in expected if rc not in {e['coordinate'] for e in existing}],'status':'new_generation_on_hold_exact_model_requirement','historicalStatePreserved':str(f)}
write(ROOT/'model-requirement-hold-20261013.json',queue)
for fname in ['production-resume-20261012.json','progress.json','production-state.json']:
 d=read(ROOT/fname);d.update(generationModelRequirement=requirement,status='local_work_only_new_generation_on_hold_exact_model_requirement',generationStopped=True,inFlight=False,inFlightRequests=[],nextStep='Continue local inventory, exact native assembly and review of saved originals. Resume new images only through an authorized route explicitly selecting verified GPT Image 2.5; no paid API authorization.',modelHoldRecord=str(ROOT/'model-requirement-hold-20261013.json'))
 d['updatedAtUtc' if fname=='production-resume-20261012.json' else 'updatedAt']=now();write(ROOT/fname,d)
d=read(ROOT/'progress-r14_c12.json');d.update(status='new_generation_on_hold_exact_model_requirement',generationModelRequirement=requirement,nextStep='Existing14 native patches preserved; p33 and p43 require a verified authorized GPT Image 2.5 route. Local review may continue.',inFlight=False,inFlightRequests=[],updatedAt=now());write(ROOT/'progress-r14_c12.json',d)
q=read(ROOT/'current-zone-counts-20261013.json');q.update(updatedAtUtc=now(),status='local_work_only_new_generation_on_hold_exact_model_requirement',generationModelRequirement=requirement,modelHoldRecord=str(ROOT/'model-requirement-hold-20261013.json'));write(ROOT/'current-zone-counts-20261013.json',q)
print(json.dumps({'counts':counts,'model':requirement['requiredImageModel'],'newGenerationAllowed':False,'partialTiles':{k:{'selected':v['selectedCoreCount'],'missing':v['missingCoordinates']} for k,v in queue['activePartialTiles'].items()}}))
