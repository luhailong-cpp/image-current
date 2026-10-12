from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,datetime
O=Path(__file__).resolve().parent
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=read(O/'inspection-prepared.json');snap=read(O/'input-snapshot.json')
reviewtime=now();views=[]
for b in d['boards']:
    b.update(actuallyViewed=True,inspectionTool='view_image',inspectionDetail='original',viewedAtUtc=reviewtime)
    views.append(dict(file=b['file'],sha256=b['sha256'],displayMode='original',operation=b['operation'],panelFiles=b['panels']))
boardmap={p:b['file'] for b in d['boards'] for p in b['panels']}
for e in d['evidence']:
    e.update(actuallyViewed=True,viewedAtUtc=reviewtime,inspectionScale=1,inspectionTool='view_image',inspectionDetail='original',status='local_visual_passed')
    e['viewedVia']=boardmap.get(e['file'],e['file'])
    if e['file'] not in boardmap:views.append(dict(file=e['file'],sha256=e['sha256'],displayMode='original'))
    kind=e['kind']
    if kind.startswith('new_column'):e['finding']='新增首列与相邻核心的地砖缝、栏杆和植被轮廓连续；未见沿接缝的直线色差或焦距突变。'
    elif kind=='changed_overlay_with_all_four_edges_and_corners':e['finding']='修复区中心、四边及四角地砖、砖缝和树影连续，旧直线材质接痕未见残留。'
    elif kind.startswith('lantern'):
        e.update(status='requires_native_material_repair',geometry='continuous',material='failed',finding='p01_04_v2 的虚化地砖与左侧、下侧清晰石纹在矩形核心边界跳变；灯笼轮廓和流苏几何连续。')
    elif kind=='complete_neighbor_fourway':e.update(finding='四块交点附近的门柱、流苏、灌木轮廓连续；北边整段仍受灯笼细棱小台阶待修约束。',status='local_junction_passed_with_adjacent_edge_issue')
    elif e.get('tiles')==['r04_c11','r05_c11'] and e['segment']==4:
        e.update(status='requires_local_geometry_review',finding='顶边灯笼靠左及中央金色细棱在 y=16384 接缝处有轻微折点/台阶，维持原生产 pending 标记。',geometry='minor_step_pending',material='local_no_new_failure')
    elif e.get('tiles')==['r04_c11','r05_c11']:e['finding']='地砖与树叶枝干连续，未见接缝缺口。'
    elif e.get('tiles')==['r05_c11','r05_c12']:e['finding']='四段灯笼、植被、门柱和地砖轮廓与色调连续。'
emap={e['file']:e for e in d['evidence']}
for e in d['edges']:
    e['segments']=[emap.get(x['file'],x) for x in e['segments']]
    e.update(status='shared_edge_local_visual_passed' if e['tiles']!=['r04_c11','r05_c11'] else 'requires_segment4_gold_rib_review',formalAccepted=False)
    if e['tiles']==['r03_c10','r03_c11']:e['status']='passed_reused_identical_independent_evidence'

repairs=[
 dict(id='NE-r05c11-p14-focus-boundaries',tiles=['r05_c11'],status='requires_native_material_repair',priority='repair_before_internal_acceptance',candidateSha256=d['tiles'][1]['sha256'],tileLocalAffectedBox=[3072,0,4096,1024],worldAffectedBox=[44032,16384,45056,17408],boundaryCoordinates=dict(leftWorldX=44032,bottomWorldY=17408),finding='灯笼下的地砖虚化与左邻清晰石纹在 x=3072 形成明显直边；下侧 y=1024 同时存在清晰度跃变。左下十字表明虚化范围沿 p01_04 核心矩形边界终止。',evidence=[e['file'] for e in d['evidence'] if e['kind'].startswith('lantern')],alreadyKnownLeftBoundary=True,newlyConfirmedBottomBoundary=True),
 dict(id='NE-r04c11-r05c11-north-lantern-ribs',tiles=['r04_c11','r05_c11'],status='requires_local_geometry_review',priority='repair_before_shared_edge_acceptance',worldAffectedBox=[44352,16352,44608,16416],finding='第 4 段灯笼靠左和中央金色细棱在北邻边附近有轻微接线折点；不把原 pending 改为通过。',evidence=[e['file'] for e in d['evidence'] if e.get('tiles')==['r04_c11','r05_c11'] and e.get('segment')==4])
]

# Reuse only current-pixel-matching passing evidence. Mark findings that supersede a prior pass.
for t in d['tiles']:
    t['inspectionCompletedAtUtc']=reviewtime
    t['newEvidence']=[e for e in d['evidence'] if e.get('tileId')==t['tileId'] or t['tileId'] in e.get('tiles',[])]
    t['productionEvidencePixelVerifiedCount']=len(t['evidence'])
    t['productionPassingEvidenceCount']=sum(e['reusable'] for e in t['evidence'])
    t['internalReview']='passed_changed_overlay_and_verified_reused_unchanged_evidence' if t['tileId']=='r03_c10' else 'requires_native_background_detail_repair'
    t['independentReviewScope']='changed overlay interior plus all four boundaries/corners; unchanged 24 seam/9 cross evidence pixel verified; east edge independently reused' if t['tileId']=='r03_c10' else 'new first-column 7 seams and 3 crosses; changed lantern core with left/bottom boundaries and lower-left cross; full north/east neighbors and fourway'
    if t['tileId']=='r03_c10':
        t['resolvedPriorFinding']='旧候选 local x≈2957 材质直线接痕已由合法 1024 原生覆盖修复，本次实际查看通过。'
        t['reusedIndependentEvidence']=d['reused']
        q=read(O/'frozen/r03_c10-native-v2-20261013-review.json');proof=[]
        for e in q['inspectedCrops']:
            if e['status']!='passed_inherited_identical_hash':continue
            p=Path(e['priorEvidence']);h=sha(p)
            with Image.open(p) as a,Image.open(e['file']) as b:same=a.size==b.size and ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
            assert same and h==e['sha256']
            proof.append(dict(file=e['file'],priorEvidence=p.as_posix(),sha256=h,priorStatus=e['priorStatus'],currentPixelsIdentical=True))
        t['verifiedUnchangedInheritedEvidenceCount']=len(proof);write(O/'r03_c10-unchanged-evidence-reuse.json',proof)
    else:
        t['repairIds']=[r['id'] for r in repairs]
        for e in t['evidence']:
            name=Path(e['file']).name
            if name in ['horizontal-1-segment-4-100pct.png','cross-1-3-100pct.png']:
                e.update(reusable=False,independentStatus='requires_native_material_repair',supersededBy='NE-r05c11-p14-focus-boundaries')

changes=[]
for e in snap['files']:
    p=Path(e['file']);live=sha(p) if p.exists() else None
    if live!=e['sha256']:changes.append(dict(file=e['file'],snapshotSha256=e['sha256'],currentSha256=live))
recheck=dict(checkedAtUtc=now(),checkedFileCount=len(snap['files']),unchangedFileCount=len(snap['files'])-len(changes),changes=changes,snapshotStale=bool(changes),policy='Frozen versions define this batch. Later changes are listed without repeated generation or an endless live audit.')
write(O/'source-recheck.json',recheck)
write(O/'visual-review.json',dict(reviewedAtUtc=reviewtime,tool='view_image',detail='original',viewedFiles=views,evidence=d['evidence'],boards=d['boards'],notes='All boards use unscaled exact crops. Reused evidence is identified separately; no current viewing is claimed for reused legacy images.'))
write(O/'repair-queue.json',repairs)
summary=dict(capturedAtUtc=d['capturedAtUtc'],completedAtUtc=now(),status='batch_review_complete_with_open_art_issues',tiles=d['tiles'],fullCoverageCount=2,selectedCoreCount=32,adoptedCandidateCount=2,formalAcceptedCount=0,newEvidenceCount=len(d['evidence']),actuallyViewedNewEvidenceCount=len(d['evidence']),reusedIndependentEdgeSegmentCount=len(d['reused']),edgeReviews=d['edges'],repairs=repairs,sourceRecheck=recheck,generationCalls=0,productionWrites=0,gitOperations=0,writeScope=O.as_posix(),scopeLimitations=['Only r03_c10 and r05_c11 and their known complete neighbors.', 'Partial neighboring edges excluded and assigned to parent auditor.', 'No formal map acceptance.'],outputs=dict(visualReview=(O/'visual-review.json').as_posix(),sourceRecheck=(O/'source-recheck.json').as_posix(),repairQueue=(O/'repair-queue.json').as_posix(),inputSnapshot=(O/'input-snapshot.json').as_posix()))
write(O/'summary.json',summary)
print(json.dumps(dict(status=summary['status'],tiles=[dict(tileId=t['tileId'],sha256=t['sha256'],internalReview=t['internalReview']) for t in summary['tiles']],sourceChangedCount=len(changes),actualEvidenceViewed=24,repairCount=2),ensure_ascii=False))
