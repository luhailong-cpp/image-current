exec((__import__('pathlib').Path(__file__).parent/'prepare.py').read_text(encoding='utf-8').split('snapshot=freeze')[0])
d=read(OUT/'prepared.json'); replay=read(OUT/'native-repair-pixel-replay.json');focus=read(OUT/'focus-crops.json')
def cp(n):return str(OUT/'crops'/n)
issues=[
 {'id':'r07c04-north-flower-cut','tiles':['r06_c04','r07_c04'],'status':'geometry_and_material_repair_required','worldApproxBox':[13312,24550,14336,24610],'finding':'At the actual north/south tile join, yellow flowers/leaves still change abruptly across the horizontal cut. v10 does not repair that shared-edge line; the last 16 rows of r06_c04 are exactly unchanged from v8.','evidence':[cp('r06_c04-neighbor-south-r07_c04-seg2.png')],'relationshipToPrior':'same issue retained, new current-v10 context visually checked'},
 {'id':'r07c04-north-paving-material','tiles':['r06_c04','r07_c04'],'status':'material_review_required','worldApproxBox':[14336,24520,15360,24680],'finding':'Paving contours remain connected, while the pattern and texture transition remains pending paired material acceptance. The nearby v10 edit is inside r06_c04; it does not establish an accepted border.','evidence':[cp('r06_c04-neighbor-south-r07_c04-seg3.png')],'relationshipToPrior':'same issue retained, current-v10 context checked'},
 {'id':'r05c02-north-blossom-cut','tiles':['r04_c02','r05_c02'],'status':'prior_issue_not_closed','worldApproxBox':[4096,16360,5120,16420],'finding':'Prior blossom-edge issue is retained as open. Current adopted v4 differs from the old diagnostic assembly, so the old border result is not automatically transferred. New original-scale crops were examined; that limited review does not establish whole-object/material acceptance or authorize closing the prior issue.','evidence':[cp('r05_c02-neighbor-north-r04_c02-seg1.png'),cp('r05_c02-north-blossom-focus.png')],'relationshipToPrior':'prior unresolved issue retained; not asserted to be a newly introduced failure'},
 {'id':'west-late-r06c03-roof-patch-vertical-line','tiles':['r06_c03','r07_c03'],'status':'localized_material_and_geometry_review_required','worldApproxBox':[10928,24320,10968,24510],'finding':'A straight vertical repair boundary remains visible through the blue roof/red diagonal trim in the northern half of the paired native crop, about world x10946. It lies in unchanged r06_c03, not in the new r07_c03 pixels; the r06/r07 pair must remain open until its roofline context is accepted.','evidence':[cp('r07_c03-north-roof-focus.png'),cp('r07_c03-neighbor-north-r06_c03-seg3.png')],'relationshipToPrior':'observed in unchanged neighboring candidate; does not attribute regression to v7'},
 {'id':'r06c04-west-railing-pending','tiles':['r06_c03','r06_c04'],'status':'prior_geometry_issue_retained','finding':'Production selection still records stepped/blind western stone-railing courses and a pending upper-left repair after two masks. West 256-pixel strip of v10 equals v8 exactly. This delta review does not reopen unchanged historic pixels or declare the railing accepted.','evidence':[str(NW/'right-current-selection-20261012.json')],'relationshipToPrior':'preserved production finding, unchanged western strip reused'}
]
specific={
 ('r06_c04','neighbor-south-r07_c04-seg2'):('geometry_and_material_repair_required','Yellow foliage hard cut remains across the tile boundary.'),
 ('r06_c04','neighbor-south-r07_c04-seg3'):('geometry_continuous_material_pending','Stone contours connect; texture/pattern acceptance remains open.'),
 ('r05_c02','neighbor-north-r04_c02-seg1'):('prior_issue_not_closed','Blossom-edge issue retained pending full paired acceptance; actual current crop inspected.'),
 ('r07_c03','neighbor-north-r06_c03-seg3'):('neighbor_patch_boundary_pending','Vertical repair edge remains in the unchanged north-neighbor roof/trim context.'),
}
for c in d['crops']:
 status,note=specific.get((c['tileId'],c['name']),('reviewed_no_obvious_large_geometry_break','Original-resolution crop inspected. This localized observation does not close existing whole-object or material issues.'))
 c['visualStatus']=status;c['visualFinding']=note;c['actuallyViewedAtOriginalResolution']=True
for b in d['boards']:b['visualStatus']='actually_viewed_original_pixels';b['viewerDetail']='original'
for c in focus:c['actuallyViewedAtOriginalResolution']=True;c['sha256']=sha(c['path'])
for t in d['tiles']:
 t['internalChangedSegmentsReviewed']=sum(s['changedPixels']>0 for s in t['internalSeams'])
 t['internalUnchangedSegmentsReused']=sum(s['changedPixels']==0 for s in t['internalSeams'])
 t['internalClosurePassed']=False;t['formalAccepted']=False
 t['status']='adopted_full_coverage_delta_reviewed_open_issues_retained'
 t['priorEvidenceReusable']='only pixel-identical subregions, with prior pass/pending status preserved'
 t['reviewScope']='changed native core seams, declared repair contexts, available changed neighbor bands; no whole-map acceptance'
 t['issues']=[x['id'] for x in issues if t['tileId'] in x['tiles']]
 t['selectedCoreCountChanged']=False
 if t['tileId']=='r05_c02':
  t['adoptionDelta']=1;t['coverageDelta']=0
  t['baselineCaveat']='Baseline is an independently hard-pasted selected-core diagnostic, not a production-adopted candidate; v4 also incorporates the production native seam selection. The broad difference bbox is not 16 new cores.'
  t['missingAdjacentTiles']=['r05_c01','r06_c02']
 elif t['tileId']=='r06_c04':
  t['adoptionDelta']=0;t['coverageDelta']=0
  t['productionPending']='v10 southmid upper-right coarse grout locally recorded passed; upper-left remains pending after two masks; cross-top railing belongs connected_resume.'
 else:
  t['adoptionDelta']=0;t['coverageDelta']=0
  t['productionPending']='6 native repair sources applied; production says final roofline repair in preparation and updated internal review pending.'
checks=[]
unique={x['path']:x for x in d['sourceImages']}
for path,info in unique.items():
 h=sha(path);checks.append({'path':path,'snapshotSha256':info['sha256'],'endSha256':h,'unchanged':h==info['sha256']})
metaPath=NW/'current-adopted-20261012.json'; endData=metaPath.read_bytes();endHash=hashlib.sha256(endData).hexdigest();(OUT/'snapshots/current-adopted-end-read.json').write_bytes(endData)
endObj=json.loads(endData.decode('utf-8-sig'));endTiles={t['tileId']:t for t in endObj['tiles']};late=[]
for t in d['tiles']:
 e=endTiles.get(t['tileId']);same=e and e['image']['path']==t['file'] and e['image']['sha256']==t['sha256'];late.append({'tileId':t['tileId'],'frozenImage':t['file'],'endImage':e['image'] if e else None,'selectionUnchanged':bool(same)})
for n in ['right-current-selection-20261012.json','root-current-selection-20261012.json']:freeze(NW/n)
d['crossZone']['status']='prior_geometry_and_material_pass_reused_for_this_edge_only'
d['crossZone']['reviewBasis']='r07_c03 bottom 256 rows pixel SHA256 identical; complete r08_c03 source SHA256 identical to previously reviewed pair; no visual rescan.'
d['crossZone']['doesNotAcceptWholeTiles']=True
d.update({'status':'completed_frozen_three_tile_delta_review','completedAtUtc':datetime.now(timezone.utc).isoformat(),'generationCalls':0,'productionWrites':0,'gitOperations':0,'formalAcceptedCount':0,'adoptedCandidateDelta':1,'fullCoverageDelta':0,'uniqueSelectedCoreDelta':0,'reviewedChangedInternalSegments':40,'unchangedInternalSegmentsReused':32,'reviewedNeighborSegments':10,'reusedNeighborSegments':4,'reviewedRepairContexts':11,'reviewedFocusCrops':3,'viewedBoards':7,'issues':issues,'focusCrops':focus,'pixelReplay':{'recordCount':len(replay),'allPixelExact':all(x['rawPixelReplayExact'] for x in replay),'allSourceAndMaskHashesMatch':all(x['sourceHashMatches'] and x['maskHashMatches'] for x in replay),'details':str(OUT/'native-repair-pixel-replay.json')},'endInputImageChecks':checks,'frozenImagesUnchangedAtEnd':all(x['unchanged'] for x in checks),'endSelectionCheck':{'metadataHash':endHash,'metadataChanged':endHash!=d['metadata']['sha256'],'tiles':late,'readOnceOnly':True,'laterSelectionsNotAutomaticallyReviewed':True},'limitations':['No image generation, repainting, material blending, global map build, or production metadata writes.','Pending internal closures and whole-object issues remain pending despite locally continuous changed geometry.','Partial r07_c04 neighbor pixels are the frozen v03 native edge evidence; no later production selection is silently substituted.','Missing adjacent tiles prevent whole-perimeter acceptance.','Actual image model not reclassified; this is mechanical audit of existing materials.']})
write(OUT/'summary.json',d);write(OUT/'repair-queue.json',issues);write(OUT/'end-input-check.json',{'images':checks,'metadata':d['endSelectionCheck']})
print(json.dumps({'status':d['status'],'tiles':[{'tileId':t['tileId'],'file':t['file'],'sha256':t['sha256'],'changedPixels':t['changedPixelCount'],'bbox':t['diffBbox'],'reviewedInternal':t['internalChangedSegmentsReviewed'],'reusedInternal':t['internalUnchangedSegmentsReused']} for t in d['tiles']],'crossZoneReusable':d['crossZone']['priorPassReusable'],'all11RepairReplaysExact':d['pixelReplay']['allPixelExact'],'allFrozenImagesUnchanged':d['frozenImagesUnchangedAtEnd'],'endSelectionUnchanged':all(x['selectionUnchanged'] for x in late)},ensure_ascii=False,indent=2))
