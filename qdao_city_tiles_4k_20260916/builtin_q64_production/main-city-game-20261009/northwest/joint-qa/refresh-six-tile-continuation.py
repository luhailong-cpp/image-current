from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
f=p.ZONE/'continuation-round-20261011.json';r=p.read(f);progress=p.read(p.ZONE/'progress.json')
delivery=p.ZONE/'joint-six-tile-review/ac2031be4f9bb37b/delivery-summary.json'
r.update({'updatedAt':p.now(),'currentCoordinate':'r07_c05/s01_01','status':'six_contiguous_4k_tiles_packaged_continuing_remaining_coordinates','currentCandidates':{'complete4k':progress['currentComplete4kCandidateCount'],'internallyReviewed':progress['internalQAPassedCount'],'formalAccepted':progress['formalAcceptedCount']},'currentPatchQA':{'tile':'r06_c06','status':'internal_passed','candidate':p.read(p.ZONE/'r06_c06/qa/acceptance.json')['candidate'],'initialFirstOutputWasRejected':True,'selectedRepair':'s01_04_fix03','sourceSelectionUnchangedDuringFinalCenterCutQA':True},'peripheralSeams':{'withinFirst2x2':'passed','threeNewSharedTileEdges':'passed; 12 native seam segments plus 10 junction crops actually viewed','remainingOuterSides':'pending actual neighboring tiles'},'currentDelivery':{'file':str(delivery),'sha256':p.sha(delivery),'tileCount':6,'package':p.read(delivery.parent/'package.json')},'nextStep':'Continue r07_c05 and r05_c07 drawing; finish r05_c03 and r07_c04 specific repairs; package next passed tiles.','errors':[],'wholeZoneComplete':False,'gitMutations':False})
p.write_json(f,r,replace=True)
print(f)
