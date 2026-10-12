from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,csv,re
O=Path(__file__).resolve().parent;R=O.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
extra=read(O/'southeast-remaining/summary.json')
for e in extra['newEdgeReviews']:
 pending=e['tiles']==['r12_c12','r13_c12']
 e.update(status='geometry_pass_material_review_required' if pending else 'local_shared_edge_visual_passed',actuallyViewed=True,viewedAtOriginalPixelScale=True,finding='西端木桩旁水面有矩形明暗带，轮廓连续但材质待核。' if pending else '四段共享边轮廓和局部材质接续，未见新的共享边断线。')
 for s in e['segments']:s.update(actuallyViewed=True,status='material_review_required' if pending and s['segment']==1 else 'local_shared_edge_visual_passed')
for e in extra['newCrossReviews']:e.update(status='local_junction_visual_passed',actuallyViewed=True,viewedAtOriginalPixelScale=True)
extra.update(completedAtUtc=now,newEdgePairCount=13,newSeamSegmentCount=52,newCrossCount=5,priorInternalIssuesRetained=True)
new_se_issue={'id':'r12c12-r13c12-water-rectangle','pair':['r12_c12','r13_c12'],'status':'material_review_required','worldApproxBox':[45056,48896,45256,49408],'finding':'West-end water adjacent to timber pilings contains a vertical rectangular light/dark strip. Shared-edge outlines remain continuous.','evidence':str(O/'southeast-remaining/r12_c12__r13_c12/segment-1-100pct.png')}
extra['issues']=[new_se_issue];write(O/'southeast-remaining/summary.json',extra)
(O/'southeast-remaining/review.md').write_text('''# 八仙岛东南剩余共享边检查

此前两组局部拼接以外的13对完整候选共享边已补查，涵盖52段原像素裁片及5个四交汇。12对共享边及5个交汇局部通过；r12_c12与r13_c12西端木桩旁水面存在矩形明暗带，保持材质待核。图块内部既有待修问题继续保留。

所有来源采用本次东南冻结输入，15张既有成图hash已由[来源复核](../southeast/baseline-candidate-reuse.json)确认未变。每对边、裁片、世界坐标与实际目检状态见[汇总](summary.json)。本补查没有重建大图、生成或编辑图像，没有提高正式验收数。
''',encoding='utf-8')
baseline=read(R/'coverage-inventory-v01.json');tiles={t['tileId']:dict(t) for t in baseline['tiles']}
for t in tiles.values():
 t['baselineCoreCount']=t['coreCount'];t['coreCoverageComplete']=t['fullCoverage'];t['productionAdoptedFull']=t['fullCoverage'] and t['tileId']!='r12_c13';t['evidence']=t['originInventory']
w=read(O/'west/summary.json');se=read(O/'southeast/summary.json');ne=read(O/'northeast/summary.json');res=read(O/'residences/summary.json')
for z,data in w['zones'].items():
 for q in data['tiles']:
  t=tiles[q['tileId']];t.update(coreCount=q['coreCount'],coreCoverageComplete=q['fullCoreCoverage'],fullCoverage=q['fullCoreCoverage'],productionAdoptedFull=q['adopted4kCandidate'] is not None,evidence=str(O/'west/source-delta.json'))
  if q['adopted4kCandidate']:
   t.update(file=q['adopted4kCandidate']['path'],sha256=q['adopted4kCandidate']['sha256'])
for a in w['newDiagnosticAssemblies']:
 t=tiles[a['tileId']];t.update(file=a['path'],sha256=a['sha256'],dimensions=a['dimensions'],coverageArtifactType='independent_diagnostic_core_assembly',adopted=False,sourcePixelsVerified=True)
for q in ne['tiles']:
 t=tiles[q['tileId']];t.update(evidence=str(O/'northeast/summary.json'),sourcePixelsVerified=True)
for tid,count in [('r13_c11',14),('r14_c12',16)]:
 t=tiles[tid];t.update(coreCount=count,coreCoverageComplete=count==16,fullCoverage=count==16,evidence=str(O/'southeast/summary.json'))
a=se['coordinateDelta']['r14_c12'];tiles['r14_c12'].update(file=a['candidate'],sha256=a['sha256'],dimensions=[4096,4096],productionAdoptedFull=False,coverageArtifactType='production_pending_candidate',independentInternalPassed=True)
for tid in ['r12_c13','r14_c12']:tiles[tid]['coverageArtifactType']='production_pending_candidate'
for q in res['currentTiles']:
 t=tiles[q['tileId']];assert t['coreCount']==0,('coordinate selection conflict',q['tileId'])
 t.update(coreCount=q['selectedCoreCount'],coreCoverageComplete=False,fullCoverage=False,productionAdoptedFull=False,evidence=str(O/'residences/summary.json'),allocationOwner='parallel-residences',selectedCoreMatrix=q['selectedCoreMatrix'])
coverage=[]
for tid,t in sorted(tiles.items()):
 for k in ['baselineState','baselineMissingCoreCount','snapshotStale','storedPixelsStale','currentStoredFileSha256']:t.pop(k,None)
 t.update(missingCoreCount=16-t['coreCount'],coreCountDelta=t['coreCount']-t['baselineCoreCount'],reviewCountsScope='versioned regional frozen snapshots; later production excluded',formalAccepted=False)
 if not t.get('coverageArtifactType'):t['coverageArtifactType']='production_adopted_candidate' if t['productionAdoptedFull'] else 'partial_selected_cores' if t['coreCount'] else 'no_selected_core'
 coverage.append(t)
counts={'targetTiles':196,'fullCoreCoverageTiles':sum(t['coreCoverageComplete'] for t in coverage),'productionAdoptedFullCandidates':sum(t['productionAdoptedFull'] for t in coverage),'unadoptedProductionFullCandidates':sum(t['coverageArtifactType']=='production_pending_candidate' for t in coverage),'independentDiagnosticFullAssemblies':sum(t['coverageArtifactType']=='independent_diagnostic_core_assembly' for t in coverage),'partialTiles':sum(0<t['coreCount']<16 for t in coverage),'emptySelectedCoreTiles':sum(t['coreCount']==0 for t in coverage),'declaredSelectedOrCandidateCoreCount':sum(t['coreCount'] for t in coverage),'baselineCoreCount':953,'coreIncrease':sum(t['coreCountDelta'] for t in coverage),'targetCores':3136,'missingCores':sum(t['missingCoreCount'] for t in coverage),'formalAcceptedCount':0,'mapComplete':False}
assert len(coverage)==196 and counts['declaredSelectedOrCandidateCoreCount']==968 and counts['fullCoreCoverageTiles']==57 and counts['partialTiles']==9 and counts['emptySelectedCoreTiles']==130,counts
write(O/'coverage-inventory.json',{'createdAtUtc':now,'counts':counts,'scope':'coordinate-deduplicated regional frozen snapshots; complete core coverage is not visual acceptance; two independent diagnostic assemblies are not production candidates','regionReports':{z:str(O/z/'summary.json') for z in ['west','northeast','southeast','residences']},'tiles':coverage})
with (O/'coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['tileId','coreCount','coreCountDelta','missingCoreCount','coreCoverageComplete','productionAdoptedFull','coverageArtifactType','file','sha256','formalAccepted','evidence'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:t.get(k) for k in fields} for t in coverage)
write(O/'missing-tiles.json',{'scope':'same frozen regional snapshots as coverage-inventory.json','missingFullCoverage':[t for t in coverage if t['coreCount']<16],'partialTileIds':[t['tileId'] for t in coverage if 0<t['coreCount']<16],'emptyTileIds':[t['tileId'] for t in coverage if not t['coreCount']]})
write(O/'repair-queue.json',{'priorIssuesRetained':str(R/'seam-repair-queue-v01.json'),'newOrReconfirmedWestIssues':w['issues'],'newSoutheastMaterialIssue':new_se_issue,'southeastPendingCandidateReview':str(O/'southeast/r12_c13-proposal-delta.json'),'residenceFailuresAndUnadoptedStatus':str(O/'residences/visual-review.json'),'formalAcceptedCount':0,'repairsRemainProductionOwnerResponsibility':True})
regions=[]
for name,z in [('west',w),('northeast',ne),('southeast',se),('residences',res),('southeast-remaining',extra)]:
 p=O/name/'summary.json';regions.append({'region':name,'file':p.as_posix(),'sha256':sha(p)})
write(O/'completion.json',{'status':'existing_material_incremental_review_complete_for_frozen_inputs','createdAtUtc':now,'counts':counts,'reports':regions,'newFullCoverageCoordinates':['r05_c02','r12_c03','r14_c12'],'laterProductionExcluded':True,'generationCalls':0,'productionWrites':False,'gitOperations':False,'newSidebarChats':0,'priorArtifactsRetained':True})
report='''# 八仙岛恢复后的独立检查结果

本批增量检查已完成。各区冻结输入合并去重后，196坐标中57处已具备16个原生核心，9处部分覆盖，130处尚无选用核心；共968个核心，比上批增加15个，距3136目标还缺2168个。57处完整覆盖包含53张生产采用候选、2张未采用生产候选、2张本检查目录的诊断拼接，正式验收仍为0。

三处新增完整覆盖为r05_c02、r12_c03和r14_c12。r05_c02及r12_c03用选用核心按原像素拼成4096诊断图，逐核心回裁零差异，外围问题仍开放。r14_c12已有完整生产候选，新增6段内缝和4个交点通过独立检查，其余有效证据复用；冻结时尚未列入生产采用清单。r13_c11保持14/16，缺末排第3、第4核心。

本批补查东北7对共享边及3个交汇，东南13对此前未覆盖的共享边及5个交汇；新增图块、部分核心及民居的可用边另有原像素裁片。旧选用成图hash未变的检查继续复用，5组既有8192局部图保持原版本。

待修重点为r12_c03北侧距顶边115像素的水面和石壁矩形材质带，r05_c02北边花朵断口，r08_c02邻边红柱材质竖带，以及r12_c12与r13_c12木桩旁水面明暗矩形带。海岸水纹、r03_c10石面、r12_c13地板与帆桁等旧问题仍未关闭。缺邻图和材质待核项保持未通过，详见[待修清单](repair-queue.json)。

新划拨的东西民居12坐标在所记截点已有7张原生图，其中仅r02_c11选用1个核心；其余区分失败、未采用或快照后尚未查的新图，没有据落盘数量提高完整块数。r02_c12新提案的南东边及交汇局部连续仍不等同整块通过。

- [196坐标覆盖记录](coverage-inventory.json)及[CSV](coverage.csv)
- [缺块清单](missing-tiles.json)
- [西北和西南增量](west/review.md)
- [东北增量与剩余边界](northeast/review.md)
- [东南新增核心与候选](southeast/review.md)及[剩余共享边](southeast-remaining/review.md)
- [东西民居落盘与边缘检查](residences/review.md)
- [已有8192局部拼接清单](../local-deliverables-v01.json)

计数采用各区记录的冻结输入，主要截点为2026年10月13日美东时间04:23至04:29；之后继续落盘的素材单独留在增量记录，不套用旧结论。这是独立检查结果，不是全图完成或生产采用通知。

所有新增记录与机械裁片仅保存在本检查目录。未生图或AI修图、未覆盖原素材、未改生产progress和共享Git。西区子工末步遇到“application network permission was revoked”；本地已保存证据由根窗口收尾，未重试网络或修改权限。
'''
(O/'review.md').write_text(report,encoding='utf-8')
broken=[];links=0
for p in [O/'review.md']+[O/z/'review.md' for z in ['west','northeast','southeast','residences','southeast-remaining']]:
 for dest in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
  if dest.startswith(('http:','https:','#')):continue
  q=Path(dest) if re.match(r'^[A-Za-z]:[/\\]',dest) else p.parent/dest
  links+=1
  if not q.exists():broken.append({'report':str(p),'link':dest})
write(O/'delivery-check.json',{'checkedAtUtc':now,'uniqueCoordinateCount':len(coverage),'countsSumCorrect':counts['fullCoreCoverageTiles']+counts['partialTiles']+counts['emptySelectedCoreTiles']==196,'reportLinksChecked':links,'brokenLinks':broken,'requiredRegionReportsExist':all(Path(r['file']).exists() for r in regions),'priorArtifactsNotRebuilt':True})
assert not broken,broken
print(json.dumps(counts,ensure_ascii=False));print('links',links,'broken',len(broken))
