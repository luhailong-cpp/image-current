from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,csv
O=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths=[O/'northwest-audit-v01/inventory.json',O/'southwest-audit-v01/inventory.json',O/'root-audit-v01/inventory.json',O/'southeast-audit-v01/inventory.json']
inventories=[read(p) for p in paths];actual={};coverage=[]
def zone(r,c):return ('north' if r<=7 else 'south')+('west' if c<=7 else 'east')
for p,d in zip(paths,inventories):
 for t in d['tiles']:
  tid=t['tileId'];r,c=int(tid[1:3]),int(tid[5:7]);core=t['coreCount']
  if tid in actual:raise AssertionError('duplicate '+tid)
  entry={'tileId':tid,'zone':t.get('zone',zone(r,c)),'worldBox':[(c-1)*4096,(r-1)*4096,c*4096,r*4096],'coreCount':core,'fullCoverage':t['fullCoverage'],'file':t.get('file'),'sha256':t.get('sha256'),'dimensions':t.get('dimensions'),'formalAccepted':False,'originInventory':p.as_posix(),'snapshotStale':t.get('snapshotStale',False),'baselineState':'complete_pending_candidate' if tid=='r12_c13' else 'complete_candidate' if t['fullCoverage'] else 'partial' if core else 'empty','baselineMissingCoreCount':16-core}
  if t.get('missingCoreCoordinates'):entry['missingCoreCoordinates']=t['missingCoreCoordinates']
  if t.get('missingCores'):entry['missingCores']=t['missingCores']
  if entry['file']:
   current=sha(entry['file']);entry['currentStoredFileSha256']=current;entry['storedPixelsStale']=current!=entry['sha256']
  else:entry['storedPixelsStale']=False
  actual[tid]=entry
for r in range(1,15):
 for c in range(1,15):
  tid=f'r{r:02d}_c{c:02d}'
  if tid not in actual:actual[tid]={'tileId':tid,'zone':zone(r,c),'worldBox':[(c-1)*4096,(r-1)*4096,c*4096,r*4096],'coreCount':0,'fullCoverage':False,'file':None,'sha256':None,'dimensions':None,'formalAccepted':False,'originInventory':paths[2].as_posix(),'baselineState':'empty','baselineMissingCoreCount':16,'snapshotStale':False,'storedPixelsStale':False}
  coverage.append(actual[tid])
assert len(coverage)==196
assign=read(O.parent.parent/'acceleration-20261010/assignments.json')
assigned=next(a for a in assign['assignments'] if a['map']=='island-game-20261009')['coordinates']
assert sorted(assigned)==['r01_c13','r01_c14','r02_c13','r02_c14']
delta=read(O/'southeast-finalize-v01/live-delta.json')
summary={'targetTiles':196,'fullCoverageCandidateTiles':sum(t['fullCoverage'] for t in coverage),'adoptedFullCoverageCandidateTiles':sum(t['fullCoverage'] and t['tileId']!='r12_c13' for t in coverage),'fullCoverageUnadoptedPendingCandidateTiles':1,'partialTiles':sum(0<t['coreCount']<16 for t in coverage),'emptyTiles':sum(t['coreCount']==0 for t in coverage),'baselineSelectedCoreCount':sum(t['coreCount'] for t in coverage),'requiredCoreCount':196*16,'missingCoreCount':sum(16-t['coreCount'] for t in coverage),'missingFullTileCount':sum(not t['fullCoverage'] for t in coverage),'formalAcceptedCount':0,'finalMapComplete':False,'readOnlyProduction':True,'generationCalls':0,'sourceChangedDuringReview':True,'countsScope':'frozen versioned inputs; live continuation delta separate'}
assert summary['fullCoverageCandidateTiles']==54 and summary['baselineSelectedCoreCount']==953
write(O/'coverage-inventory-v01.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'summary':summary,'accelerationDeduplication':{'coordinates':assigned,'owner':'accelerated-northeast-coast','removedFromMainNortheastCount':4,'deduplicatedMapTargetCount':196},'sourceReports':[{'file':p.as_posix(),'sha256':sha(p)} for p in paths],'tiles':coverage,'liveDeltaReport':(O/'southeast-finalize-v01/live-delta.json').as_posix()})
with (O/'coverage-v01.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['tileId','zone','coreCount','fullCoverage','baselineState','baselineMissingCoreCount','file','sha256','storedPixelsStale','snapshotStale','formalAccepted']);w.writeheader();w.writerows({k:t.get(k) for k in w.fieldnames} for t in coverage)
write(O/'missing-tiles-v01.json',{'scope':'baseline selected-source snapshot; new production is recorded separately','missingFullTiles':[t for t in coverage if not t['fullCoverage']],'partialTiles':[t for t in coverage if 0<t['coreCount']<16],'emptyTiles':[t['tileId'] for t in coverage if t['coreCount']==0],'delta':{'r13_c11':delta['r13_c11'],'r14_c12':delta['r14_c12'],'newNativeImages':delta['newNativeImagesNotInSnapshot']}})
cross=[]
for c in range(1,15):
 a,b=f'r07_c{c:02d}',f'r08_c{c:02d}'
 cross.append({'pair':[a,b],'worldLine':['y',28672],'baselineCoreCounts':[actual[a]['coreCount'],actual[b]['coreCount']],'status':'shared4096_edge_geometry_material_passed_tile_internals_open' if c==3 else 'neighbor_missing_or_incomplete'})
for r in range(1,15):
 a,b=f'r{r:02d}_c07',f'r{r:02d}_c08'
 cross.append({'pair':[a,b],'worldLine':['x',28672],'baselineCoreCounts':[actual[a]['coreCount'],actual[b]['coreCount']],'status':'neighbor_missing_or_incomplete'})
for c in [13,14]:cross.append({'pair':[f'r02_c{c}',f'r03_c{c}'],'status':'south_north_border_passed_8_legacy_crops_pixel_identical','group':(O/'root-audit-v01/g02-cross-zone-r02-r03-c13-c14/manifest.json').as_posix()})
for r in [1,2]:cross.append({'pair':[f'r0{r}_c12',f'r0{r}_c13'],'status':'west_main_neighbor_missing'})
write(O/'cross-zone-edges-v01.json',{'edges':cross,'centralFourWayJunction':{'worldPoint':[28672,28672],'tiles':['r07_c07','r07_c08','r08_c07','r08_c08'],'status':'all_four_neighbors_missing'},'formalAcceptedCount':0})
nw=inventories[0];sw=inventories[1]
rootissues=read(O/'root-audit-v01/repair-queue.json')
seissues=[
 {'tileId':'r12_c13','status':'needs_AI_native_repair','worldApproxPoint':[50176,47223],'tileLocalPoint':[1024,2167],'finding':'deck groove mismatch','evidence':(O/'southeast-audit-v01/breakpoints/r12_c13-floor-groove-x1024-y2167-100pct.png').as_posix()},
 {'tileId':'r12_c13','status':'needs_AI_native_repair','worldApproxPoint':[52224,48786],'tileLocalPoint':[3072,3730],'finding':'low sail batten line mismatch','evidence':(O/'southeast-audit-v01/breakpoints/r12_c13-low-sail-batten-x3072-y3730-100pct.png').as_posix()},
 {'tiles':['r12_c11','r12_c12','r13_c11','r13_c12'],'status':'geometry_continuous_material_pending_partial_neighbor','worldPoint':[45056,49152],'finding':'current selected p14 junction preserves column outline; material acceptance and incomplete r13c11 remain open','evidence':(O/'southeast-audit-v01/breakpoints/r12-r13-c11-c12-selected-core-junction-100pct.png').as_posix()}]
write(O/'seam-repair-queue-v01.json',{'scope':'current review snapshots; repair responsibility remains with original production windows','northeast':rootissues,'northwest':nw['issueCrops'],'southwest':sw['normalizedRepairQueue'],'southeast':seissues,'southeastReview':(O/'southeast-finalize-v01/visual-review.json').as_posix(),'missingNeighborEdges':(O/'cross-zone-edges-v01.json').as_posix()})
deliver=[
 ('西北 r04 r05 c03 c04',O/'northwest-audit-v01/middle_r04-r05_c03-c04_native8192_internal-pass_perimeter-pending_v01.png','共享内边通过 外围待验'),
 ('西南 r10 r11 c03 c04',O/'southwest-audit-v01/native-assemblies/current-r10-r11-c03-c04-native-8192-v01.png','最新来源局部拼接 以区域报告限制为准'),
 ('东北 r03 r04 c11 c12',O/'root-audit-v01/g03-main-r03-r04-c11-c12/native-hard-join-8192.png','本批共享边和交叉点通过 外围待验'),
 ('东北 r04 r05 c13 c14',O/'root-audit-v01/g04-main-r04-r05-c13-c14/native-hard-join-8192.png','本批共享边和交叉点通过 外围待验'),
 ('东南 r09 r10 c12 c13',O/'southeast-audit-v01/g01-r09-r10-c12-c13/native-hard-assembly-8192x8192-v01.png','共享边局部通过 外围待验')]
outputs=[]
for label,p,status in deliver:
 assert p.exists(),p
 outputs.append({'label':label,'file':p.as_posix(),'sha256':sha(p),'dimensions':[8192,8192],'status':status,'formalAccepted':False,'operation':'source native pixels hard-pasted without scaling; not native 8192 model generation'})
write(O/'local-deliverables-v01.json',{'deliverables':outputs,'diagnosticGroups':['root-audit-v01/g01-coast-r01-r02-c13-c14','root-audit-v01/g02-cross-zone-r02-r03-c13-c14','southeast-audit-v01/g02-r11-r12-c11-c12'],'diagnosticReason':'open material issues or incomplete neighbor acceptance','formalAcceptedCount':0})
rows=['# 八仙岛已有素材独立收尾报告','',
'本批已完成已有素材的来源核对、去重清单、原像素局部拼接及未验收接缝检查。全图196坐标的冻结基线为54张完整覆盖候选，其中53张位于当前采用清单，另1张r12_c13为完整待修未采用候选；10坐标部分覆盖，132坐标无选用核心。完整覆盖未等同画面通过，正式验收仍为0。','',
'953个1024核心已有选择来源，3136个目标核心中缺2183个。加速区r01 r02 c13 c14只记一次，东北主区目标为45，加速区为4；四象限合计196。详细196行见[覆盖清单](coverage-inventory-v01.json)，逐坐标缺块见[缺块清单](missing-tiles-v01.json)。','',
'生产在检查期间继续。冻结基线后的东南r13_c11选择已从12增至14核心；r14_c12另有p33和p43原生图落盘，但工作与选用字段未同步，未擅自提高整块完成数。东南5个元数据JSON变化，旧全区快照标过期；755张旧PNG未变，两组拼接直接来源仍有效。东北海岸选择文件亦变化，根审计标记其选择元数据过期；已有成图像素保持对应hash。后续版本必须按[来源变化记录](southeast-finalize-v01/live-delta.json)重新选择和验边。','',
'跨区已实查西北r07_c03与西南r08_c03的4096共享边，4个1024段轮廓和石缝连续。右上r07_c04仍缺，四交叉点不能验收。东北海岸与主区两条南北接边8张旧裁片与当前像素完全相等，可复用。主地图中线其余边与中央四交叉仍缺邻图，列表见[跨区边界](cross-zone-edges-v01.json)。','',
'需修位置已写入[接缝待修清单](seam-repair-queue-v01.json)：西北红墙脚线、雕座、花叶和屋瓦断口；西南竹院石缝、金木框保留带和矮墙高度；东北海水x53248约y7900至8050直线材质带、r03_c10石面直带；东南r12_c13木地板x1024 y2167及帆桁x3072 y3730小错接。材质待核与邻图缺失分别保留，不用模糊、程序补画或插值掩盖。','',
'以下局部图保持8192乘8192原像素，均由四张4096成图机械拼接。只作为列明版本的局部交付，外围和全图验收状态见各区域报告：','']
for e in outputs:rows.append(f"- [{e['label']}]({e['file']})：{e['status']}。")
rows.extend(['','[全部局部图hash清单](local-deliverables-v01.json)记录原像素来源。预览文件均标明缩略用途，不能替代4K图块。','',
'本批来源审计由[西北](northwest-audit-v01/review.md)、[西南](southwest-audit-v01/review.md)、[东北及跨区](root-audit-v01/review.md)、[东南收尾](southeast-finalize-v01/review.md)给出尺寸、hash、像素回放和检查证据。未修改原制作目录、progress、共享索引、AGENTS或Git，未删除或恢复素材。新规则为免费现有入口2.5优先、不可用允许内置2.0，本独立检查未调用生图，已有图实际型号仍按原回执记录。'])
(O/'review-v01.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
write(O/'completion-v01.json',{'status':'authorized_existing_material_review_batch_complete','createdAtUtc':datetime.now(timezone.utc).isoformat(),'mapComplete':False,'formalAcceptedCount':0,'summary':summary,'sourceSnapshotStale':True,'report':(O/'review-v01.md').as_posix(),'productionWrites':False,'generationCalls':0,'gitOperations':False})
print(json.dumps(summary,ensure_ascii=False))
