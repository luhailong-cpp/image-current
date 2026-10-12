import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;mf=ROOT/'delivery-20261011-v2/delivery-manifest.json';m=p.read(mf)
checks=[]
for t in m['tiles']:
 assert p.sha(t['candidate'])==t['sha256']==p.sha(t['sourceCandidate'])
 assert Image.open(t['candidate']).size==(4096,4096)
 assert p.sha(t['review'])==t['reviewSHA256']
 for r in t['supplementaryReviews']:assert p.sha(r['file'])==r['sha256']
 for r in t['selectedNativeOrDerivedPatches']:assert p.sha(r['file'])==r['sha256']
 checks.append({'tile':t['tile'],'sha256':t['sha256'],'pixels':[4096,4096],'allReferencedHashesVerified':True})
p.put_json(HERE/'checkpoint-v2/delivery-verification.json',{'createdAt':p.now(),'deliveryManifest':str(mf),'manifestSHA256':p.sha(mf),'verifiedTiles':checks,'allPassed':True,'formalAcceptedCount':0,'noGitOperations':True})
roundstate=p.read(ROOT/'continuation-round-20261011.json');progress=p.read(ROOT/'progress.json')
progress.update({'updatedAt':p.now(),'status':'verified_second_candidate_checkpoint_remaining_repairs','candidateCount':4,'nativeCount':64,'formalAcceptedCount':0,'internalFullyPassedTileCount':0,'currentCoordinate':roundstate['currentCoordinate'],'firstNewOutputThisRound':roundstate['firstNewOutputThisRound'],'newRawOutputCountThisRound':8,'savedRawOutputCountAcrossRestoration':12,'integratedRawRepairSourceCountAcrossRestoration':8,'latestContinuationRecord':str(ROOT/'continuation-round-20261011.json'),'latestNeighborInventory':roundstate['latestNeighborInventory'],'verificationReport':str(HERE/'checkpoint-v2/delivery-verification.json'),'nextStep':roundstate['nextStep'],'gitOperationsThisRound':0})
p.replace_json(ROOT/'progress.json',progress)
p.put_json(HERE/'checkpoint-v2/closeout.json',{'createdAt':p.now(),'newActualRawOutputsThisRound':8,'rawOutputsAcrossRestoration':12,'integratedRepairSourcesAcrossRestoration':8,'newlyUpdatedCandidates':['r03_c05','r04_c05'],'resolvedDefects':['E3','E4','E5','E6','D2','D3'],'pendingOwnedRepairs':['r03_c05 D1/D4/D5','r03_c03 unavailable; r03_c04/r03_c05 E1/E2','r03_c04 left roof returns','r04_c04 minor rail facet','r04_c05 minor internal residuals and inherited south blurry green stripe'],'formalAcceptedCount':0,'deliveryManifest':str(mf),'newOutputsRetained':True,'originalsRetained':True,'unmergedAcceptedRepairCount':0,'generationErrorsThisRound':[],'resolvedImplementationIssues':['Created missing owned receipts directories before successful publish','Replaced image-only reference helper for JSON audit reference with explicit path and SHA'], 'scopeExpanded':False,'gitOperations':0})
print({'deliveryVerified':True,'tiles':4,'selectedPatches':64,'formalAccepted':0})

