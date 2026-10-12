import sys,os,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));import pipeline as p
project=Path('D:/work/image');now=p.now()
out=ROOT/'model-policy-20261013-clarified.json'
historical=ROOT/'model-policy-20261013.json'
evidence=sorted((ROOT/'continuation-20261013').glob('neighbor-recheck-*.json'))
policy={
 'schemaVersion':1,'recordedAtUTC':now,
 'userClarification':'免费/现有内置2.5可用就优先，否则允许用回2.0继续。此前强制2.5/禁止2.0/因型号不明停工是误解，现撤销。',
 'projectInstructions':[{'file':str(f),'sha256':p.sha(f),'readInFull':True} for f in [project/'AGENTS.md',project/'docs/IMAGE_MODEL_REQUIREMENT.md']],
 'supersedes':{'file':str(historical),'sha256':p.sha(historical),'previousRecordKeptForHistory':True},
 'preferredImageModelWhenFreeOrIncluded':'GPT Image 2.5',
 'allowedFallbackImageModel':'GPT Image 2.0',
 'existingBuiltinImageRouteAllowed':True,
 'missing25SelectorOrMetadataBlocksProduction':False,
 'newGenerationPausedByModelRequirement':False,
 'paidApiAuthorized':False,'newSubscriptionOrCredentialChangesAuthorized':False,
 'actualModelMetadataPolicy':'Record actual returned metadata honestly; unreturned model remains null, do not relabel unknown or historic images as2.5.',
 'modelTestCallsPerformed':0,'newGenerationCallsForThisPolicyUpdate':0,
 'scope':['r03_c04','r03_c05','r04_c04','r04_c05'],
 'assignedDeliveredTileCount':4,'assignedMissingCoreCount':0,'knownOpenInternalDefects':[],
 'needlesslyRegenerateCompletedTiles':False,'expandProductionCoordinates':False,
 'formalAcceptedCount':0,
 'remainingWork':'External acceptance requires missing neighboring artwork and current adopted south-neighbor baseline. No assigned native deficit or AI repair is currently identified.',
 'latestNeighborRecheck':{'file':str(evidence[-1]),'sha256':p.sha(evidence[-1])} if evidence else None,
 'existingArtworkDeliveryAndFreezeRecordsUnmodified':True,'gitOperations':0,
 'uploadOrCaptureInterrupted':False
}
p.put_json(out,policy)
for name in ['progress.json','production-resume-20261012.json']:
 file=ROOT/name;d=p.read(file)
 d.update({
  'updatedAt':now,
  'imageModelPolicyRecord':str(out),
  'requestedExactImageModel':None,
  'preferredImageModelWhenFreeOrIncluded':'GPT Image 2.5',
  'allowedFallbackImageModel':'GPT Image 2.0',
  'verifiedImageGenerationRoute':None,
  'existingBuiltinImageGenerationRouteAllowed':True,
  'newImageGenerationPausedByModelRequirement':False,
  'unverifiedBuiltinNewCallsAllowed':True,
  'paidApiAllowed':False,
  'generationAuthorizationCondition':'Existing builtin route authorized; prefer free/included2.5 when available,otherwise2.0 permitted. No paid API; actual metadata recorded honestly.',
  'generationHoldReason':None,
  'generationHoldActive':False,
  'generationAuthorizedByUser':True,
  'generationStopped':True,
  'generationStoppedReason':'All4 assigned tiles locally reviewed and delivered; no assigned missing core or known internal AI repair remains. This is not a model hold.',
  'assignedGenerationWorkPausedByModelRequirement':[],
  'assignedGenerationWorkPausedByNewPolicy':[],
  'currentToolError':None,
  'inFlightRequests':0,
  'unsavedSuccessfulOutputs':0,
  'nextStep':'Continue permitted local boundary acceptance when neighboring artwork becomes available; keep existing4 delivered tiles and exclusive coordinates. No model-verification pause.',
  'modelRequirementClarificationApplied':True
 })
 if evidence:d['latestNeighborRecheck']=str(evidence[-1])
 if name=='progress.json':p.replace_json(file,d)
 else:
  tmp=ROOT/'model-policy-resume-clarification-writing-20261013.json';p.put_json(tmp,d);os.replace(tmp,file)
for name in ['progress.json','production-resume-20261012.json']:
 d=p.read(ROOT/name);assert d['newImageGenerationPausedByModelRequirement'] is False and d['unverifiedBuiltinNewCallsAllowed'] is True and d['generationHoldReason'] is None
assert p.sha(historical)==policy['supersedes']['sha256']
print(json.dumps({'record':str(out),'modelHoldRevoked':True,'existingBuiltinAllowed':True,'paidAPIAllowed':False,'assignedDelivered':4,'assignedMissing':0,'formalAccepted':0,'newGenerationCalls':0}))

