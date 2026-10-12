from pathlib import Path
import sys,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
tid='r03_c11';tile=ZONE/'tiles'/f'{tid}.png';der=read(tile.with_suffix('.png.derivation.json'));sel=read(ZONE/f'selection-{tid}.json');qa=ZONE/'qa/r03_c11-round2-final';idx=read(qa/'crop-index.json')
assert sha(tile)==idx['sha256']=='38a2deea4cef7b0ee4285819849b0ace38d0112e34c81b70af92c9455650746b'; assert sha(Path(idx['rightNeighbor']))==idx['rightNeighborSha256']
replay=Image.new('RGB',(4096,4096));checks=[]
for s in der['sources']:
 p=Path(s['file']); assert sha(p)==s['sha256']; rec=read(s['generationRecord']); assert rec['actualModel'] is None and rec['actualQuality'] is None
 original=Path(rec['evidence']['originalToolPath']); assert sha(original)==s['sha256'];assert Path(rec['prompt']).is_file();assert Path(rec['evidence']['receipt']).is_file()
 for ref in rec['references']:assert sha(ref['file'])==ref['sha256']
 replay.paste(Image.open(p).crop(s['coreCrop']),s['tileLocalPaste']);checks.append({'id':s['id'],'sha256':s['sha256'],'originalBytesEqual':True,'referenceHashesValid':True})
for s in der['requiredOverlays']:
 assert sha(s['source'])==s['sha256']; replay.paste(Image.open(s['source']).crop(s['coreCrop']),s['tileLocalPaste']);checks.append({'id':Path(s['source']).stem,'sha256':s['sha256'],'nativeOverlay':True})
diff=int(np.count_nonzero(np.any(np.array(replay)!=np.array(Image.open(tile)),axis=2)));assert diff==0
evidence=[]
for p in sorted(qa.glob('*.png')):
 if p.name=='preview.png':continue
 evidence.append({'file':p.as_posix(),'sha256':sha(p),'size':list(Image.open(p).size),'status':'passed_manual_visual_100percent'})
assert len(evidence)==53
review={'tileId':tid,'file':tile.as_posix(),'sha256':sha(tile),'size':[4096,4096],'status':'passed_full_internal_native_QA_and_right_neighbor_edge','formalAccepted':False,'internalReview':'passed','inspection':{'cores':16,'internalSeamSegments':24,'internalFourCoreCrosses':9,'rightOuterEdgeSegments':4},'evidence':evidence,'repairedIssues':[{'id':'r03_c11-stair-riser','resolution':'native v5 gives bottom step a coherent squared vertical terminal face while preserving right-hand higher stair and outer anchors'},{'id':'r03_c11-paving-junction','resolution':'native v5 reconnects paving lines at the four-core corner and removes the central stitch'}],'requiredOverlayIds':sel['overlays'],'repairIndependentReview':{'reviewer':'root','source':'collaboration message in current round','finding':'v5 full1254 and four perimeters reviewed, square terminal geometry and four edges passed'},'externalEdges':{'right':{'status':'passed_complete4096_edge','neighbor':idx['rightNeighbor'],'neighborSha256':idx['rightNeighborSha256'],'evidenceFiles':[str(qa/f'external-right-{i}.png') for i in range(1,5)]},'top':{'status':'pending_adjacent_full_tile'},'left':{'status':'pending_adjacent_full_tile'},'bottom':{'status':'pending_adjacent_full_tile'}},'nativeProvenance':{'checks':checks,'reconstructionPixelDifferences':diff,'resized':False,'feathered':False},'actualModel':None,'actualQuality':None,'reviewedAtUtc':now()}
write(ZONE/'qa/r03_c11-acceptance.json',review)
der.update(status='complete_native_coverage_internal_QA_passed',internalReview='passed',qa=(ZONE/'qa/r03_c11-acceptance.json').as_posix(),externalSeams=review['externalEdges'],formalAccepted=False,reviewedAtUtc=now());write(tile.with_suffix('.png.derivation.json'),der)
sel['pendingIssues']=[];sel.update(selectionIsPartialCandidate=False,internalReview='passed',formalAccepted=False,updatedAtUtc=now());write(ZONE/f'selection-{tid}.json',sel)
p=ZONE/'qa/r03_c11-progress.json';q=read(p);q.update(status='complete_native_coverage_internal_QA_passed',currentId=sel['overlays'][-1],generated=[p.stem for p in (ZONE/'native').glob('r03_c11*.png')],generatedCoordinateCount=16,selectedCoreIds=sel['cores'],selectedCoreCount=16,accepted=[i for row in sel['cores'] for i in row],acceptedDefinition='All16 selected core regions pass within final assembly with the required v5 repair overlay; not a claim that older unoverlaid variants pass.',requiredOverlays=sel['overlays'],pendingIssues=[],internalReview='passed',candidate=tile.as_posix(),candidateSha256=sha(tile),qa=(ZONE/'qa/r03_c11-acceptance.json').as_posix(),externalEdges=review['externalEdges'],updatedAtUtc=now(),formalAccepted=False);write(p,q)
for i in ['r03_c11_cross_03_03_stair_paving_repair','r03_c11_cross_03_03_stair_return_repair_v2','r03_c11_cross_03_03_stair_return_repair_v3','r03_c11_cross_03_03_stair_finish_v4']:
 p=ZONE/'native'/f'{i}.png.generation.json';q=read(p);q.update(status='superseded_unselected_repair_history',selected=False,supersededBy='r03_c11_cross_03_03_stair_finish_v5');write(p,q)
 for p in [ZONE/'qa'/f'{i}.overlay.json']:
  if p.exists():q=read(p);q['review']='not_selected_superseded_by_passed_v5';write(p,q)
for i in ['r03_c11_p03_03_v3','r03_c11_p04_03_v2']:
 p=ZONE/'native'/f'{i}.png.generation.json';q=read(p);q.update(status='used_with_required_native_repair_overlay',requiredRepairOverlay='r03_c11_cross_03_03_stair_finish_v5',reviewedTileSha256=sha(tile));write(p,q)
idx.update(status='passed_manual_visual_100percent',finalTile=tile.as_posix(),finalTileSha256=sha(tile),reviewRecord=(ZONE/'qa/r03_c11-acceptance.json').as_posix(),reviewedAtUtc=now());write(qa/'crop-index.json',idx)
print(json.dumps({'tile':tile.as_posix(),'sha256':sha(tile),'internalReview':'passed','rightNeighborSha256':idx['rightNeighborSha256'],'inspectedCrops':53,'reconstructionPixelDifferences':diff,'formalAccepted':False}))
