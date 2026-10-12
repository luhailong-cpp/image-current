from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
OUT=Path(__file__).parent;REVIEW=OUT.parent.parent;PROD=REVIEW.parent.parent/'island-game-20261009/southeast'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();s=read(OUT/'summary.json');tiles={t['tileId']:t for t in s['tiles']};crops=read(OUT/'crop-manifest.json')
issues=[
 {'id':'r12_c11-r13_c11-north-water-guide-band','tiles':['r12_c11','r13_c11'],'status':'material_repair_required','worldApproxBox':[41984,49240,43008,49295],'finding':'北侧第二段水面在共享线南侧约115像素处出现水平直线色阶/细节带；实际共享线波纹轮廓连续。','evidence':str(OUT/'r13_c11/north-2.png'),'formalAccepted':False},
 {'id':'r13_c11-r13_c12-east-water-detail-strip','tiles':['r13_c11','r13_c12'],'status':'material_repair_required','worldApproxBox':[44910,51200,44970,52360],'finding':'东侧第三段至第四段上端，西侧水纹密度与亮度沿近竖直线变化，位置约在实际共享线西侧115像素处。轮廓接续，但局部材质不能判定通过。','evidence':[str(OUT/'r13_c11/east-3.png'),str(OUT/'r13_c11/east-4.png')],'formalAccepted':False},
 {'id':'r12c12-r13c12-water-rectangle','tiles':['r12_c12','r13_c12','r13_c11'],'status':'prior_material_issue_retained','worldApproxBox':[45040,48896,45256,49408],'finding':'东北四块交点的木柱旁直线水面明暗带仍可见，与v02记录相同；木柱轮廓连续，材质问题保留。','evidence':str(OUT/'r13_c11/northeast-junction.png'),'priorEvidence':str(REVIEW/'resume-v02/southeast-remaining/summary.json'),'formalAccepted':False},
 {'id':'r12_c13-v03-wood-material-pending','tiles':['r12_c13'],'status':'prior_internal_issue_retained','worldApproxBox':[50150,46556,50200,47506],'finding':'当前完整待修候选切换为v03最佳几何版，原像素hash与上轮未采用提案一致；木纹竖直明暗带及未修帆横杆问题继续保留。','evidence':str(REVIEW/'resume-v02/southeast/r12_c13-proposal-delta.json'),'formalAccepted':False}
]
for c in crops['cuts']:
 n=Path(c['file']).stem;c['actuallyViewed']=True;c['viewedAtOriginalPixelScale']=True
 if n in ['north-2','east-3','east-4']:c['visualReview']='geometry_continuous_material_repair_required'
 elif n=='northeast-junction':c['visualReview']='geometry_continuous_prior_material_issue_retained'
 else:c['visualReview']='local_geometry_and_material_visual_passed'
 c['reviewedAtUtc']=now
write('crop-manifest.json',crops)
# Preserve previous 2 groups and internal candidate checks when candidate hashes match.
old=read(REVIEW/'resume-v02/southeast/summary.json');groups=[]
for g in old['reuse']['groups']:
 g=dict(g);g['sourceHashesStillMatch']=all(tiles[x['tile']]['sha256']==x['sha256'] for x in g['sources']);g['reused']=g['sourceHashesStillMatch'];g['rebuilt']=False;groups.append(g)
v3=read(REVIEW/'resume-v02/southeast/r12_c13-proposal-delta.json');v3same=tiles['r12_c13']['sha256']==v3['proposalSha256'];assert v3same
r14same=tiles['r14_c12']['sha256']==old['coordinateDelta']['r14_c12']['sha256'];assert r14same
# Cross-junction crops from v02 are reusable when all exact source pixels match.
prev=read(REVIEW/'resume-v02/southeast-remaining/summary.json');crosschecks=[]
for c in prev['newCrossReviews']:
 oldimage=Image.open(c['file']).convert('RGB');w,h=oldimage.size;cx,cy=c['worldPoint'];box=[cx-w//2,cy-h//2,cx+w//2,cy+h//2];current=Image.new('RGB',(w,h));covered=0
 for tid in c['tiles']:
  t=tiles[tid];tb=t['worldBox'];x1=max(tb[0],box[0]);y1=max(tb[1],box[1]);x2=min(tb[2],box[2]);y2=min(tb[3],box[3])
  if x1<x2 and y1<y2:
   with Image.open(t['file']) as im:current.paste(im.convert('RGB').crop((x1-tb[0],y1-tb[1],x2-tb[0],y2-tb[1])),(x1-box[0],y1-box[1]))
   covered+=(x2-x1)*(y2-y1)
 same=covered==w*h and oldimage.tobytes()==current.tobytes();crosschecks.append({'tiles':c['tiles'],'file':c['file'],'hashMatchesPrior':sha(c['file'])==c['sha256'],'pixelsMatchCurrent':same,'reused':same,'priorStatus':c['status']})
assert all(c['reused'] and c['hashMatchesPrior'] for c in crosschecks)
# Verify current producer quick checks only against the exact frozen original hashes, without reinterpreting quick pass as full-tile approval.
sup=read(OUT/'supplemental-metadata-snapshot.json');q=sup['documents']['qa/returned-batch-resume-20261013/root-visual-review.json'];quick=[]
for x in q['entries']:
 p=PROD/'native'/(x['patch']+'.png');n=PROD/'native'/(x['neighbor']+'.png')
 quick.append({'patch':x['patch'],'neighbor':x['neighbor'],'recordedStatus':x['status'],'sourceHashMatches':sha(p)==x['patchSha256'],'neighborHashMatches':sha(n)==x['neighborSha256'],'evidenceHashMatches':sha(x['file'])==x['sha256'],'evidence':x['file'],'independentlyViewedThisBatch':False,'scope':'Reused producer quick inspection with unchanged exact sources; not whole-tile acceptance'})
assert all(x['sourceHashMatches'] and x['neighborHashMatches'] and x['evidenceHashMatches'] for x in quick)
write('additional-evidence-reuse.json',{'groups':groups,'r14_c12InternalAndNorthChecksReused':r14same,'r12_c13V03PreviousReviewReused':v3same,'oldCrosses':crosschecks,'producerQuickChecks':quick})
# End-of-batch stability is reported separately and never mutates the capture.
checksets=[read(OUT/'metadata-snapshot.json')['checks'],sup['checks'],read(OUT/'source-checks.json')['checks']];seen={}
for arr in checksets:
 for c in arr:seen[c['file']]=c
changes=[]
for p,c in seen.items():
 h=sha(p) if Path(p).exists() else None
 if h!=c['sha256']:changes.append({'file':p,'frozenSha256':c['sha256'],'endSha256':h,'includedInFrozenCounts':False})
write('end-of-batch-changes.json',{'checkedAtUtc':now,'checkedDistinctCurrentInputs':len(seen),'changes':changes,'frozenCaptureRetained':True,'newFilesAfterCaptureNotPursued':True})
for t in s['tiles']:
 t['baselineCoreCount']=next(x['coreCount'] for x in read(REVIEW/'resume-v02/coverage-inventory.json')['tiles'] if x['tileId']==t['tileId']);t['missingCoreCount']=16-t['coreCount']
 if t['tileId']=='r13_c11':t['independentDeltaVisual']={'internalDelta':'8 new necessary internal seam/junction/source-boundary crops visually passed','northEast':'geometry continuous; material issues open','externalPassed':False,'evidence':str(OUT/'crop-manifest.json')}
s.update(status='incremental_audit_complete_for_frozen_capture',completedAtUtc=now,baselineCounts=old['frozenCurrentCounts'],visual={'newExactPixelCropsViewed':17,'allAtOriginalPixelScale':True,'internalDeltaCropsPassed':8,'externalEdgeSegmentsViewed':8,'externalJunctionsViewed':1,'newMaterialIssues':2,'priorMaterialIssuesRetained':True,'formalAccepted':False},reuse={'priorFullCandidateHashesUnchanged':15,'previous8192GroupsReused':2,'remainingSharedEdgePairsReused':13,'remainingSharedEdgeSegmentsReused':52,'previousCrossJunctionsReused':5,'r14_c12PriorInternalAndNorthChecksReused':True,'r12_c13V03PriorProposalVisualEvidenceReused':True},issues=issues,sourceStability={'changesAfterFrozenCapture':changes,'unchangedInputsReusable':True,'laterChangesExcluded':True},metadataConflicts=[{'tileId':'r14_c11','olderSelectionCount':2,'effectiveSelectedCount':3,'authority':'newer progress-r14_c11 selectedVersions plus returned-batch QA, p42 passed','productionMetadataModified':False},{'tileId':'r13_c13','olderProgressCount':1,'effectiveSelectedCount':2,'authority':'newer resume-right-current-batch selected plus returned-batch QA, p24-v02 recovered and passed','productionMetadataModified':False},{'tileId':'r14_c12','olderProgressCoreCount':14,'effectiveCandidateCoreCount':16,'authority':'exact candidate/native manifest verified v02, current adoption table confirms','productionMetadataModified':False},{'tileId':'r12_c13','olderProgressCandidate':'v02','effectivePendingCandidate':'v03-local-ownership','authority':'current-zone-counts pendingCandidates; still internalPassed false','productionMetadataModified':False}],reports={n:str(OUT/n) for n in ['metadata-snapshot.json','supplemental-metadata-snapshot.json','source-checks.json','candidate-reuse.json','shared-edge-reuse.json','additional-evidence-reuse.json','r13_c11-source-proof.json','crop-manifest.json','unselected-saved-sources.json','end-of-batch-changes.json','repair-queue.json']})
write('summary.json',s);write('repair-queue.json',{'issues':issues,'priorProductionUnpassedSources':str(OUT/'unselected-saved-sources.json'),'formalAcceptanceNotGranted':True})
print(json.dumps({'summary':str(OUT/'summary.json'),'counts':s['counts'],'sourceInputsChecked':len(seen),'endChanges':len(changes),'newViewedCrops':17,'newMaterialIssues':2,'priorCrossesReusable':len(crosschecks),'quickReviewsHashVerified':len(quick)},ensure_ascii=False))
