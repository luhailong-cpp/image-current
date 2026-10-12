from review_tools_v1 import *
from zoneinfo import ZoneInfo
import csv

now=datetime.now(timezone.utc)
groups={d.name:read(d/'manifest-v1.json') for d in OUT.glob('G0[1234]-*')}
g2=OUT/'G02-jewelry-east-r04-r05-v1';g3=OUT/'G03-jewelry-south-and-east-r06-v1';g4=OUT/'G04-southwest-southeast-r10-r11-v1'
issues=[
 dict(id='FV-SEAM-001',status='needs_AI_material_repair',priority=1,coordinates=['r05_c11','r05_c12'],global_observation_box=[44800,17152,45312,18432],seam='x=45056; r05_c12 west roof, strongest segment 2 and junction 1',finding='屋瓦大轮廓基本连续；左侧宽柔高光与右侧细碎高光在直线边界突变。',required_action='原制作方统一屋瓦高光和笔触，保留瓦弧、金柱、金边以及已选木墙修复；修后重新检查完整西边和节点。',evidence=[record(g2/n) for n in ['V06-100pct.png','VJ05-100pct.png']],second_review=record(OUT/'audit-ne-accel-v1/visual-second-review-v1.json')),
 dict(id='FV-SEAM-002',status='needs_AI_material_repair',priority=1,coordinates=['r04_c12','r05_c12'],global_observation_box=[45056,16128,47104,16640],seam='y=16384; north seam of r05_c12, available x45056..47104',finding='东北主区上下候选的蓝瓦纹理、高光在水平线硬切；四块交点右半明确受影响，追加原尺寸横裁片显示可查的2048像素范围也需统一。',required_action='由东北原制作方重画连续蓝瓦材质过渡，不修改已复用的加速区源；至少复核上下相邻2列核心和global(45056,16384)交点。',evidence=[record(g2/n) for n in ['VJ04-100pct.png','NORTH-extension-H01-100pct.png','NORTH-extension-H02-100pct.png','NORTH-extension-HJ01-100pct.png']],second_review=record(OUT/'audit-ne-accel-v1/visual-second-review-v1.json')),
 dict(id='FV-SEAM-003',status='needs_AI_material_repair',priority=1,coordinates=['r11_c07','r11_c08'],global_observation_box=[28416,41984,28928,44032],seam='x=28672; r11 c07/c08 stone ground',finding='轮廓大体相接；左侧暖黄细碎地面与右侧灰青大块石地沿精确竖线切换，涉及色温和纹理材质。',required_action='由原制作方协调统一两侧地面材质与底色，保持石缝、木栏、木板和阴影几何；不能仅靠RGB偏移、模糊或拉伸。',evidence=[record(g4/n) for n in ['V06-100pct.png','V07-100pct.png','VJ06-100pct.png']],second_review=record(OUT/'audit-se-v1/visual-second-review-v1.json')),
]
write(OUT/'seam-repair-list-v1.json',dict(created_at_utc=now.isoformat(),issues=issues,scope='Independent review only. Original producers retain adoption and repair authority.',repair_performed=False,model_policy='现有免费入口2.5优先；不可用时允许现有内置2.0。本任务不生图。'))
with (OUT/'seam-repair-list-v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','status','coordinates','global_observation_box','finding','required_action']);w.writeheader()
    for i in issues:w.writerow({k:(';'.join(i[k]) if k=='coordinates' else json.dumps(i[k]) if k=='global_observation_box' else i[k]) for k in w.fieldnames})

reviews=[]
for d in [g2,g3,g4]:
    files=sorted(p for p in d.glob('*100pct.png') if '-sheet-' not in p.name and p.name not in ['V-segments-sheet-100pct.png','H-segments-sheet-100pct.png','junctions-sheet-100pct.png'])
    assert all(Image.open(p).width<=1024 and Image.open(p).height<=1024 for p in files)
    results=[]
    for p in files:
        status='local_join_passed_for_pinned_inputs'
        finding='已按100%像素查看：在此裁片内未发现阻断拼接的轮廓错位或硬性材质边界；仅为局部结论。'
        if d==g2 and p.name in ['V06-100pct.png','VJ05-100pct.png']:
            status='needs_AI_material_repair';finding='FV-SEAM-001 屋瓦竖向材质/高光断层。'
        if d==g2 and (p.name=='VJ04-100pct.png' or p.name.startswith('NORTH-extension-')):
            status='needs_AI_material_repair';finding='FV-SEAM-002 东北侧上下蓝瓦横向高光/材质硬切；不将G01内部结论扩展到此节点。'
        if d==g4 and p.name in ['V06-100pct.png','V07-100pct.png','VJ05-100pct.png','VJ06-100pct.png']:
            status='needs_AI_material_repair';finding='FV-SEAM-003 或其相邻观察范围；地面色温和细部材质不连续，轮廓基本相接。'
        results.append(dict(crop=record(p),status=status,finding=finding,trace=record(str(p)+'.trace.json')))
    review=dict(reviewed_at_utc=now.isoformat(),reviewed_at_new_york=now.astimezone(ZoneInfo('America/New_York')).isoformat(),group=d.name,native_crops_viewed=len(results),viewing_method='Direct original-resolution crops and 1:1 labelled sheets <=1536x1536; larger first-pass sheets were orientation only, then reviewed at native resolution.',results=results,formal_accepted=False,full_map_complete=False,limits='Only the 512-pixel seam corridors, recorded junction windows and 2048-pixel north extension were inspected. No whole-tile internal re-acceptance. Missing neighbors are not passed.',source_manifest=record(d/'manifest-v1.json'))
    if d==g3:review['missing_neighbor_extent']='r06_c11 p11 absent: r05_c11 south local x0..1024 unreviewable; available x1024..4096 and east edge passed locally.'
    write(d/'visual-review-v1.json',review);reviews.append(review)
assert sum(r['native_crops_viewed'] for r in reviews)==46

# Update the changed partial selection without converting a metadata check into visual acceptance.
aggregate=read(OUT/'audit-nw-sw-v1/coverage-aggregate-v1.json')
selected=SRC/'southeast/r08_c09/selected-patches.json';sel=read(selected)
partial_sources=[]
for slot,relative in sel['patches'].items():
    p=selected.parent/relative;r=record(p,slot=slot);assert r['dimensions']==[1254,1254];partial_sources.append(r)
patch_audit=dict(created_at_utc=now.isoformat(),tile='r08_c09',superseded_recorded_count=1,current_selected_count=len(partial_sources),selection=record(selected),sources=partial_sources,dimension_and_hash_check_only=True,visual_acceptance_granted=False,whole_tile_complete=False,existing_metadata_policy_text_is_not_global_authority=True)
write(OUT/'r08-c09-selection-refresh-v1.json',patch_audit)
for r in aggregate['coordinates']:
    if r['coordinate']=='r08_c09':
        r.update(selectedNativeCoreCount=len(partial_sources),sourceSnapshotStale=False,sourceSnapshotStalenessReason='',sourceReport=str(OUT/'r08-c09-selection-refresh-v1.json'),sourceReportSha256=sha(OUT/'r08-c09-selection-refresh-v1.json'),sourceSection='metadata and native header/hash refresh only',note='原快照1片已过期；本次补核现场2片1254²。未新增视觉验收或完整覆盖。')
aggregate.update(createdAtUtc=now.isoformat(),supersedes=str(OUT/'audit-nw-sw-v1/coverage-aggregate-v1.json'),staleCoordinates=[],aggregateSnapshotStaleForLiveUse=False,snapshotCoverageNote='Fixed independent inventory snapshot, refreshed r08_c09 selection to two native cores. Full-candidate counts unchanged. Production may advance after timestamp; rerun validation before using as current status.',latestModelPolicy='Free/existing 2.5 preferred; existing builtin2.0 fallback allowed. No generation in this review.')
write(OUT/'coverage-snapshot-v2.json',aggregate)
with (OUT/'coverage-snapshot-v2.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(aggregate['coordinates'][0].keys()));w.writeheader();w.writerows(aggregate['coordinates'])

# Reference choices are checked as recorded declarations; external files remain outside this read scope.
expected={'layout':'cf450f0afe784b4700f2dfc19b3af35867765403e8f1d81741e78b3116583d42','detail':'db47c3d1699c4163734fb4cd155cecc8529ea6adb56f3e7533d375764cf9152c','mail_style':'c1ab2e50b271e5c5590a92fe68bd6cf7d2c64cbd0d369b25b4ff5c6619033b63'}
refdocs=[SRC/'production-contract.json',SRC/'southwest/references.json',SRC/'accelerated-jewelry-approach/coordinate-plan.json',SRC/'southeast/r11_c08/coordinate-plan.json',OUT/'audit-ne-accel-v1/audit-report-v4.json']
refchecks=[]
for p in refdocs:
    txt=p.read_text(encoding='utf-8-sig');refchecks.append(dict(document=record(p),expected_hashes_declared={k:v in txt for k,v in expected.items()}))
write(OUT/'reference-consistency-v1.json',dict(created_at_utc=now.isoformat(),expected_recorded_reference_hashes=expected,declarations=refchecks,dimensions='native sources 1254x1254; formal cores 4096x4096; subcore1024, halo115, overlap230. Preview and layout-guide pixels excluded.',scope_limit='Reference paths outside fishing-village production tree were not read. This verifies declared reference consistency and source geometry, not current bytes or full-map style/layout accuracy of external approved references. Existing images retain actual-model unknown where not returned.',no_reference_image_substitution=True))

checks=[];metadata=[]
for name,m in groups.items():
    seen=set()
    for s in m['sources']:
        p=s['file']
        if p in seen:continue
        seen.add(p);actual=sha(p);checks.append(dict(group=name,file=p,expected_sha256=s['sha256'],actual_sha256=actual,pixels_unchanged=actual==s['sha256']))
    for s in m.get('selection_records',[]):
        actual=sha(s['file']);metadata.append(dict(group=name,file=s['file'],expected_sha256=s['sha256'],actual_sha256=actual,metadata_unchanged=actual==s['sha256']))
g1=OUT/'G01-jewelry-six-reused-native-v1'
for k in ['original','output']:
    s=groups[g1.name][k];checks.append(dict(group='G01-assembly',file=s['file'],expected_sha256=s['sha256'],actual_sha256=sha(s['file']),pixels_unchanged=sha(s['file'])==s['sha256']))
validation=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),review_inputs=checks,selection_metadata=metadata,all_review_pixel_hashes_current=all(c['pixels_unchanged'] for c in checks),changed_selection_metadata=[m for m in metadata if not m['metadata_unchanged']],stale_groups=sorted(set(c['group'] for c in checks if not c['pixels_unchanged'])|set(m['group'] for m in metadata if not m['metadata_unchanged'])),policy='Changed pixel or selection metadata marks group stale for current use; no previous pass transfers to new versions. Review remains evidence only for pinned hashes.',inventory_snapshot_fixed=True,production_not_paused=True)
write(OUT/'source-validity-final-v1.json',validation)

summary=dict(created_at_utc=now.isoformat(),map='fishing-village-game-20261009',task_status='Existing-material review batch completed; map incomplete',coverage=aggregate['summary'],coverage_table=record(OUT/'coverage-snapshot-v2.json'),native_reviewed_crop_count=46,groups=[record(OUT/n/'manifest-v1.json') for n in groups],visual_reviews=[record(OUT/r['group']/'visual-review-v1.json') for r in reviews],repair_list=record(OUT/'seam-repair-list-v1.json'),source_validity=record(OUT/'source-validity-final-v1.json'),native_local_candidate=record(g1/'jewelry-six-8192x12288-native-candidate-reused-v1.png'),native_candidate_classification='Byte-identical existing six-tile native assembly; internal/within-region prior QA reused; outer region joins pending and defects listed. Not formal map acceptance.',new_image_generation_calls=0,production_files_modified=False,git_operations=0,formal_acceptance_granted=False,full_map_complete=False,latest_model_policy='Free/existing GPTImage2.5 preferred, builtin2.0 fallback permitted; original producers continue, this window only reviews.',missing_boundaries='NW r07/c07; NE-SE row7/8; SW-SE all rows except10/11; acceleration other outer neighbors absent or incomplete. Exact missing tile IDs in coverage table.')
write(OUT/'review-summary-v1.json',summary)
txt=f'''渔村已有素材独立收尾检查 v1
快照时间：{now.astimezone(ZoneInfo('America/New_York')).isoformat()}（纽约时间）

本批检查完成，地图尚未完成或正式验收。
196个坐标已去重：56块完整原生候选，140块缺完整源（8块部分、132块未报告可用原生覆盖）。
内部已有通过证据46块；正式通过0块。首饰店加速区6坐标仅计一次。
西北13完整/12内部；西南14/12；东北主区9/7；加速区6/6；东南14/9。
原报告r08_c09的1片记录已过期；现场现选2片，已补做尺寸和SHA检查，未给予视觉通过。

独立检查：G02/G03/G04共46张100%原生裁片，逐片保留输入SHA、全局坐标和裁切来源；较大的首次总览只用于定位，随后在原尺寸裁片/无缩放小联系表完成检查。
G01：复用首饰店6块现有8192×12288原生拼接，字节一致SHA cd927854c447e2feffcba1b006d6b87778a9f4a6872adb2f941cd5892a5cb135。
本地PNG为局部候选；preview-downsampled-labelled-v1.png仅为明确标注的缩小预览。

需原制作方AI返修的3项：
FV-SEAM-001：r05_c11/c12，x45056，蓝瓦宽柔高光与细碎亮纹竖向硬切；观察框[44800,17152,45312,18432]。
FV-SEAM-002：r04_c12/r05_c12，y16384，蓝瓦横向高光/材质硬切；可查观察框[45056,16128,47104,16640]。交点右半需返修，G01内部既有证据不延伸到该交点。
FV-SEAM-003：r11_c07/c08，x28672，左暖黄细碎纹与右灰青石材沿竖线切换；观察框[28416,41984,28928,44032]。
以上观察框不是直接返修蒙版，原制作方仍须结合周围原生上下文确定修复范围。

局部可复用检查：r04c11/c12西接缝4段；r10c07/c08桥木接缝4段；G03 r06c11/c12东接4段、r05c11/r06c11南接可用3段及四块交点。
G03 r06c11缺p11，北边左1024像素无法验收。其他缺邻范围和140缺完整坐标详见coverage-snapshot-v2.json/.csv。
任何源SHA或选用记录变化即使本批检查对当前使用过期，不能把旧通过结论迁移到新版本。

交付入口：review-summary-v1.json；source-validity-final-v1.json；seam-repair-list-v1.json/.csv；coverage-snapshot-v2.json/.csv。
已重读最新模型澄清：现有免费2.5优先、不可用允许内置2.0继续；本检查窗口未生图、不抢坐标、未修改原生产/progress/AGENTS，未Git提交/push、未删除素材。
'''
(OUT/'REVIEW-RESULT-v1.txt').write_text(txt,encoding='utf-8')
print(json.dumps(dict(summary=summary['coverage'],native_crops=46,issues=len(issues),pixel_sources_current=validation['all_review_pixel_hashes_current'],stale_groups=validation['stale_groups'],output=str(OUT)),ensure_ascii=False))
