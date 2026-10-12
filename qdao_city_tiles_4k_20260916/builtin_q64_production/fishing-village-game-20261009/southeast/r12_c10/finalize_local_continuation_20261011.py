from pathlib import Path
import json,sys,hashlib
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import review_external_seams as ex
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
S=T/'selected-continuation-20261011.json';sel=read(S)
Q=T/'qa'/'continuation-20261011'; im=read(Q/'manifest.json')
g1=['p12--p13','p13--p23','p22--p23','cross-r1-c2']; g2=['p41--p42']; g3=['p21--p31']
for r in im['evidence']:
 name=Path(r['file']).stem
 r['visualReview']={'reviewedAt':now,'reviewer':'south10_restore','native100PercentViewed':True,'status':'structural_repair_required' if name in g1+g2 else 'independent_joint_bottom_check_required' if name in g3 else 'no_structural_break_seen','issueIds':['G1'] if name in g1 else ['G2'] if name in g2 else ['G3'] if name in g3 else [],'colorAcceptance':'pending_final_bounded_matching','formalAccepted':False}
write(Q/'visual-review.json',dict(tile='r12_c10',selectedCount=14,sourceManifest=str(Q/'manifest.json'),sourceManifestSha256=sha(Q/'manifest.json'),evidence=im['evidence'],availableInternalSeams=20,availableIntersections=7,viewedNativeCrops=27,noStructuralBreakSeenCrops=21,structuralIssueVisibleCrops=5,independentJointBottomCheckCrops=1,full24And9Complete=False,internalReady=False,formalAccepted=False))
E=T/'qa'/'external-continuation-20261011';em=read(E/'manifest.json')
for r in em['evidence']:
 if r['sourceComplete']:
  issue=r['id'] in ['west-segment-3','intersection-x36864-y47104']
  review={'reviewedAt':now,'reviewer':'south10_restore','native100PercentViewed':True,'status':'joint_bottom_geometry_and_texture_review_required' if issue else 'no_structural_break_seen','structuralBlockers':['G3'] if issue else [],'colorOnlyRisks':['bounded material matching remains pending'],'candidateUsable':False if issue else None,'formalAccepted':False}
  r['visualReview']=review
  p=Path(r['report']);d=read(p);d['visualReview']=review;write(p,d)
write(E/'visual-review.json',dict(tile='r12_c10',selection=str(S),selectionSha256=sha(S),evidence=em['evidence'],availableSegments=8,availableIntersections=7,viewedNativeCrops=15,missingIntersections=2,formalAccepted=False))
# Current shared stairs use the independently reviewed west candidate exactly in relevant region.
same=[]
for pid in ['p11','p21']:
 cur=Image.open(T/sel['patches'][pid]).convert('RGB');base=T/'processed'/'weststairs-v2-preview'/f'{pid}-weststairs-v2-candidate.png'
 a=Image.open(base).convert('RGB')
 assert cur.crop((0,0,627,1254)).tobytes()==a.crop((0,0,627,1254)).tobytes()
 same.append(dict(patch=pid,selected=str(T/sel['patches'][pid]),selectedSha256=sha(T/sel['patches'][pid]),reviewedSource=str(base),reviewedSha256=sha(base),nativeCrop=[0,0,627,1254],byteIdentical=True))
write(T/'qa'/'shared-stairs-current-verification-20261011.json',dict(createdAt=now,checks=same,independentReview=str(Z/'seam-qa'/'independent-20261010'/'r12_c09-c10-weststairs-v2-independent.json'),note='Exact west-stair shared geometry preserved. This does not clear G3 newly observed below the joint bottom.'))
src=ex.Sources();cache=src.tile('r12_c10');cache.update(selection=sel,selectedPath=S,selectedSha256=sha(S))
inspect=[]
for name,box in [('G1-eaststairs-current',[38400,45400,39654,46654]),('G2-foreground-railing-current',[37440,47898,38694,49152]),('G3-westjoint-bottom-current',[36237,46719,37491,47973])]:
 out,pieces,missing=src.extract(box);assert not missing
 p=T/'repairs'/f'{name}-inspection-1254.png';out.save(p)
 d=dict(file=str(p),sha256=sha(p),globalBox=box,dimensions=[1254,1254],sources=pieces,operation='unscaled current native core inspection crop; not generated and not a repair',resamplingApplied=False)
 write(p.with_suffix('.png.derivation.json'),d);inspect.append(d)
issues=[
 dict(id='G1',status='confirmed_structural_blocker',globalRegion=[38912,45465,39360,46619],exactAdoptionRightX=39027,description='The three tall risers from the saved eaststairs-v3 repair terminate on a rectangular vertical line against the former smaller stair system. Top and right adoption corner needs coherent stair endpoints at stone sidewall.',affected=['p12','p13','p22','p23'],action='New built-in joint repair after permission restored; preserve exterior endpoints, do not blur or color-correct geometry.'),
 dict(id='G2',status='confirmed_structural_blocker',globalRegion=[37773,48500,38250,49152],exactConditionStripRightX=38003,description='Two foreground railing beams in p42 stop abruptly at the 230-pixel conditioning strip against the neighboring rocks; a coherent end connection/occlusion is missing.',affected=['p41','p42'],action='Native joint edit to join beams to existing left support or give physically correct rock occlusion; preserve rock/rail exterior edges.'),
 dict(id='G3',status='geometry_and_texture_issue_requires_independent_review',globalRegion=[36237,47104,37491,47347],jointBottomY=47219,description='New west-segment-3 evidence shows a straight horizontal repair-bottom line with board-seam endpoints slightly shifted. This is below the previously approved main three-stair silhouettes; do not classify as color-only without independent check.',affected=['r12_c09:p34','r12_c10:p31'],action='Coordinate with c09 owner and independent QA; do not edit c09 files from this task.')
]
write(T/'qa'/'structural-issues-20261011.json',dict(createdAt=now,issues=issues,inspectionCrops=inspect,internalReady=False))
audit=read(T/'continuation-native-audit-20261011.json')
existing=[]
for tile in ['r10_c10','r11_c10']:
 d=read(Z/tile/'selected-patches.json');p=Path(d['candidate']);assert sha(p)==d['candidateSha256']
 existing.append(dict(tile=tile,candidate=str(p),sha256=sha(p),internalReady=d['internalReady'],formalAccepted=False))
native=list((T/'native').glob('*.png.generation.json'));repairs=list((T/'repairs').glob('*.png.generation.json'))
missing=[]
plan=read(T/'coordinate-plan.json')
for pid in ['p43','p44']:
 p=next(p for p in plan['patches'] if p['id']==pid)
 missing.append(dict(tile='r12_c10',patch=pid,coreBox=p['coreBox'],nativeBox=p['globalBox'],status='request_failed_network_permission_revoked_no_output' if pid=='p43' else 'not_requested'))
partial=T/'candidate'/'r12_c10-partial-14cores-4096.png';proof=read(partial.with_suffix('.png.derivation.json'))
handoff=dict(createdAt=now,scope='southeast c10 local continuation; no Git operations',status='local_work_saved_waiting_for_network_generation',canonicalSelectionWriteFailure='selected-patches.json existing file write returns Errno22; no workaround against migration lock attempted',activeReviewableSelection=str(S),activeSelectionSha256=sha(S),canonicalSelectionPositions=len(read(T/'selected-patches.json')['patches']),continuationPositions=14,currentR12Complete4kCandidates=0,currentR12InternalPassed=0,existingColumnFullCandidates=2,existingColumnInternalPassed=2,existingColumnFormalAccepted=0,existingCandidates=existing,newNativeSuccessCount=8,newNativeOutputs=audit['records'],newSourcesCopiedByteIdentical=True,unmappedRawSuccesses=audit['unmappedRawOutputs'],p43Failure=str(T/'p43-v1.failure.json'),partialAssembly=dict(path=str(partial),sha256=sha(partial),dimensions=[4096,4096],coverageFraction=0.875,complete=False,missingPixels='alpha zero; never filled or enlarged overview',proof=str(partial.with_suffix('.png.derivation.json'))),allActualGeneratedSourcesR12=len(native)+len(repairs),nativeGenerationRecords=len(native),jointGenerationRecords=len(repairs),generatedNotInCanonicalSelection=['p41-v1','p42-v1'],historicalNotDirectlySelected=[p.name.replace('.png.generation.json','') for p in native if ('native/'+p.name.replace('.generation.json','')) not in sel['patches'].values()],historicalInventoryNote='Historical native versions may be bases of selected processed repairs; not all are rejected. All original files remain.',missingCoordinates=missing,laterAssignedTilesRequiringGeneration=['r13_c10','r14_c10'],internalQA=dict(seamsViewed=20,seamsRequired=24,crossesViewed=7,crossesRequired=9,report=str(Q/'visual-review.json')),externalQA=dict(availableNorthSegmentsViewed=4,availableWestSegmentsViewed=4,intersectionsViewed=7,intersectionsMissing=2,eastAndSouth='pending missing center/neighbor pixels',report=str(E/'visual-review.json')),externalEdgesNotFinallyAccepted=4,confirmedStructuralIssues=['G1','G2'],independentReviewRequired=['G3'],issueReport=str(T/'qa'/'structural-issues-20261011.json'),boundedColorPass='not run; geometry unresolved and tile incomplete',blockers=['application network permission was revoked during p43 request; stopped further network requests','Missing p43 and p44 genuine pixels','G1 and G2 need native generative repair','G3 needs independent geometry check and cross-owner coordination'],nextSteps=['Restore network authorization before requesting generation','Inspect saved p43 conditioned guide and reuse saved p43 prompt/request; no previous successful result exists','Condition p44 from p34 and successful p43, then generate','Repair G1 and G2 preserving fixed external geometry; resolve G3 with c09 owner','Run complete 24 internal seams and 9 intersections, bounded color audit, then current north/west external QA','Promote only after evidence passes; continue r13_c10 then r14_c10'],formalAccepted=False,wholeRegionComplete=False,gitTouched=False)
write(T/'local-continuation-20261011.json',handoff)
write(T/'progress-continuation-20261011.json',dict(tile='r12_c10',updatedAt=now,selectedNativeCount=14,canonicalSelectedCount=12,complete4kCount=0,internalReady=False,formalAcceptedCount=0,status=handoff['status'],currentSelection=str(S),handoff=str(T/'local-continuation-20261011.json'),nextPatch='p43',networkFailure=handoff['p43Failure']))
print(json.dumps(dict(handoff=str(T/'local-continuation-20261011.json'),partial=str(partial),partialSha256=sha(partial),actualGeneratedSources=len(native)+len(repairs),newNative=8,selected=14)))

