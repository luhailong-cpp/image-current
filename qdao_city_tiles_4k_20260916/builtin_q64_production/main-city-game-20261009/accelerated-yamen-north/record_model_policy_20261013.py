import sys,json,hashlib,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import pipeline as p
project=Path('D:/work/image')
docs=project/'docs/IMAGE_MODEL_REQUIREMENT.md'
agents=project/'AGENTS.md'
now=datetime.now(timezone.utc).isoformat()
policyfile=ROOT/'model-policy-20261013.json'
state=p.read(ROOT/'production-resume-20261012.json')
boundary=p.read(ROOT/'finish-20261012/final-records/boundary-review.json')
policy={
 'schemaVersion':1,'recordedAtUTC':now,'effectiveFor':'All image-generation and AI edit/repair calls after receipt of the latest project requirement',
 'requestedExactImageModel':'GPT Image 2.5',
 'projectInstructions':[{'file':str(f),'sha256':p.sha(f),'readInFull':True} for f in (docs,agents)],
 'verifiedAvailableImageRoute':None,
 'newGenerationPaused':True,
 'pauseReason':'The available builtin image tool exposes no explicit image-model selector or verified actual-model metadata. It cannot satisfy the new GPT Image 2.5 verification requirement.',
 'unverifiedBuiltinNewCallsAllowed':False,'fallbackToImage2Allowed':False,'paidApiAuthorized':False,
 'modelTestCallsPerformed':0,'newGenerationCallsAfterPolicyReceipt':0,
 'existingImagesPreserved':True,'existingImagesRelabeledAs25':False,'existingDeliveredTiles':4,
 'existingActualImageModel':'unconfirmed; historic source records retain actualModel null',
 'assignedMissingTiles':[],'assignedMissingCoreCount':0,'assignedGenerationWorkPausedByNewPolicy':[],
 'pendingWork':[{'kind':'formal_external_boundary_acceptance','neighborTiles':boundary['missingNeighborTiles'],'segmentCount':len(boundary['missingOuterBoundarySegments']),'ownership':'Outside assigned production coordinates; pending input, not completed and not newly generated here'},{'kind':'formal_south_current_neighbor_baseline_verification','status':'pending'}],
 'localAssemblyReviewAndOrganizationAllowed':True,
 'inFlightRequests':0,'unsavedSuccessfulOutputs':0,
 'previousFourTileDeliveryUnmodified':True,
 'gitOperations':0,'uploadOrCaptureInterrupted':False,
 'resumeCondition':'Only resume new generation after an explicitly selectable, verifiable GPT Image 2.5 route is available within existing no-paid-API authorization. Re-read project AGENTS.md before each new image or AI edit call.'
}
p.put_json(policyfile,policy)
for file in [ROOT/'progress.json',ROOT/'production-resume-20261012.json']:
 d=p.read(file)
 d.update({'updatedAt':now,'imageModelPolicyRecord':str(policyfile),'requestedExactImageModel':'GPT Image 2.5','verifiedImageGenerationRoute':None,'newImageGenerationPausedByModelRequirement':True,'unverifiedBuiltinNewCallsAllowed':False,'paidApiAllowed':False,'imageModelRequirementFile':str(docs),'rootProjectInstructionsFile':str(agents),'generationStopped':True,'generationHoldReason':policy['pauseReason'],'assignedGenerationWorkPausedByModelRequirement':[],'generationAuthorizationCondition':'Verified GPT Image 2.5 route only; no paid API authorization','inFlightRequests':0,'unsavedSuccessfulOutputs':0})
 if file.name=='progress.json':p.replace_json(file,d)
 else:
  tmp=ROOT/'model-policy-resume-writing-20261013.json';p.put_json(tmp,d);os.replace(tmp,file)
summary={'policyRecord':str(policyfile),'requestedModel':'GPT Image 2.5','newCallsAfterReceipt':0,'assignedDelivered':4,'assignedMissing':0,'pendingOuterNeighbors':len(boundary['missingNeighborTiles']),'formalAccepted':0,'originalDeliveryAndImagesUnmodified':True}
print(json.dumps(summary))

