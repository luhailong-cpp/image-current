from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=read(O/'source-delta.json');partial=read(O/'partial-edges.json')
issues=[
 {'id':'r12c03-north-retained-band','tileId':'r12_c03','pair':['r11_c03','r12_c03'],'status':'material_repair_required','worldApproxBox':[8192,45150,9216,45195],'finding':'At r12_c03 local y115, a straight horizontal water/stone texture step remains south of the actual tile boundary.','evidence':str(O/'crops/r12_c03/neighbor-north-r11_c03-segment-1-100pct.png')},
 {'id':'r05c02-north-blossom-cut','tileId':'r05_c02','pair':['r04_c02','r05_c02'],'status':'prior_geometry_issue_retained','worldApproxBox':[4096,16360,5120,16420],'finding':'Prior blossom cut at the northern border remains open; newly completed other cores do not change that border.','evidence':str(O/'crops/r05_c02/neighbor-north-r04_c02-segment-1-100pct.png')},
 {'id':'r08c02-red-column-material-band','tileId':'r08_c02','pair':['r08_c02','r08_c03'],'status':'material_review_required','worldApproxBox':[8050,28672,8110,29280],'finding':'Shared-edge geometry remains continuous, but the red pillar shows a straight vertical change of paint texture about 115 px west of x8192.','evidence':partial['edges'][0]['path']}
]
for i,e in enumerate(partial['edges']):
 e.update(actuallyViewed=True,reviewer='root',viewedAtOriginalPixelScale=True,status='geometry_pass_material_review_required' if i==0 else 'local_shared_edge_visual_passed')
write(O/'partial-edges-reviewed.json',partial)
assemblies=[]
for a in d['newDiagnosticAssemblies']:
 b={k:v for k,v in a.items() if k not in ['boards','crossingBoard','neighborBoards']}
 b.update(status='internal_geometry_initial_review_no_obvious_break_external_issues_open',formalAccepted=False,internalGeometryReview={'reviewer':'west_resume_delta','basis':'Subagent reported actual original-resolution inspection of 24 seam segments and nine junctions per tile before its final network-permission error.','segmentCount':24,'junctionCount':9,'materialAcceptance':False},outerBordersReviewedByRoot=[n['path'] for n in a['neighborBoards']])
 assemblies.append(b)
zones={}
for name,z in d['zones'].items():
 zones[name]={k:v for k,v in z.items() if not isinstance(v,(list,dict))}
 zones[name]['tiles']=[{k:v for k,v in t.items() if k!='selectedSources'} for t in z['tiles']]
metadata_changes=[]
for m in d['metadata']:
 s=sha(m['path'])
 if s!=m['sha256']:metadata_changes.append({'file':m['path'],'frozenSha256':m['sha256'],'endSha256':s,'includedInCounts':False})
summary={'startedAtUtc':d['startedAtUtc'],'snapshotCompletedAtUtc':d['finishedCaptureAtUtc'],'completedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'frozen_incremental_review_complete','zones':zones,'inputImageHashCount':d['inputImageHashCount'],'unchangedAdoptedCandidateCount':23,'newDiagnosticAssemblies':assemblies,'newPartialEdgesReviewed':5,'newOuterNeighborPairsReviewed':3,'issues':issues,'laterMetadataChanges':metadata_changes,'formalAcceptedCount':0,'generationCalls':0,'productionWrites':False,'gitOperations':False,'workerInterruption':{'error':'Fatal error: application network permission was revoked','followupNetworkAttempt':False,'recovery':'Root finished saved local crop reviews and summary using local filesystem only.'}}
write(O/'summary.json',summary)
write(O/'repair-queue.json',issues)
(O/'review.md').write_text('''# 八仙岛西区恢复检查

本批冻结选择中，西北192个核心、12坐标核心完整，其中11张为原采用成图；西南225个核心、13坐标核心完整，其中12张为原采用成图。两个区各比上批增加5核心。西南另有3个部分覆盖坐标，西北部分覆盖为0。正式验收仍为0。

440张当前选用图片已核对hash，23张原采用4K均未变，旧通过和未通过检查均保留。r05_c02由11补到16核心，r12_c03由15补到16核心；独立诊断拼接均为4096原像素，逐核心回裁零差异，尚未生产采用。子工实际查看每块24段内缝和9个交点后报告几何初查未见明显断线；材质和外围仍未验收。

r05_c02北侧花朵断口继续待修，东侧4段共享边局部连续。r12_c03北侧新增明确问题：距图块顶边115像素处，水面与石壁纹理出现水平矩形带，约全图y45171，保持待修。

新增部分核心为r08_c02上排第4片、r09_c01上排第4片、r09_c06上排第2及第3片。5条可用相邻边已按原比例查看：4条局部连续；r08_c02与r08_c03几何连续，但红柱在约全图x8077处有竖直材质变化，保留待核。未落盘邻片的边继续未查。

裁片来源与世界坐标见[来源快照](source-delta.json)、[新核心证据](new-core-evidence.json)、[部分核心边检查](partial-edges-reviewed.json)、[待修项](repair-queue.json)。计数和冻结后元数据变化见[汇总](summary.json)。子工最后一步遇到网络权限撤销，根窗口使用已保存本地证据完成收尾，没有重试网络、改变权限或调用生图。
''',encoding='utf-8')
print(json.dumps({'zones':{z:{k:v for k,v in q.items() if k!='tiles'} for z,q in zones.items()},'laterMetadataChanges':len(metadata_changes)},ensure_ascii=False))
