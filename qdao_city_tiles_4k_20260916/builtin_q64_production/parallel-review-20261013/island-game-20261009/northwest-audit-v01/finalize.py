exec((__import__('pathlib').Path(__file__).parent/'audit.py').read_text(encoding='utf-8').split('snapnames=')[0])
from collections import Counter
inv=read(OUT/'inventory.json')
full={t['tileId']:t for t in inv['tiles'] if t['fullCoverage']}
P='visual_pass_current_crop_only';R='repair_required';M='geometry_pass_material_pending'
decisions={
 'r03_c02--r03_c03':[(P,'屋瓦、红梁和窗框在本裁片接续；局部高光差保留。'),(R,'竖接边 x8192 上红墙脚线约 y9860..10060 阶跃，阴影和下方基脚缝重复；需按整段墙脚线返修。'),(P,'石墙、烟花盒与地砖接续，无新增几何断点。'),(P,'本段地砖缝与裂纹接续。')],
 'r03_c02--r04_c02':[(P,'本段石柱及花叶在横接边接续。'),(P,'本段花丛、地砖轮廓接续。'),(R,'横接边 y12288、x约6280..6900，石雕基座立面被水平截断，面板边线错位并重复；需整座基脚返修。'),(P,'本段地砖缝、花叶无明显新断点。')],
 'r04_c02--r04_c03':[(R,'竖接边 x8192、y12288..13312 花丛和石栏硬切，左清晰右模糊且叶片截断；共享整簇花叶/栏头需统一。'),(R,'竖接边 x8192、y13312..14336 花叶轮廓与笔触突然切换；下端红金檐还有明显色阶。'),(R,'竖接边 x8192、y14336..15360 蓝瓦纹理、瓦筒弧线和红檐高光出现硬切/小阶跃；需连续屋面返修。'),(R,'竖接边 x8192、y15360..16384 蓝瓦及黄色脊瓦出现清楚截线，约y16000附近脊瓦断续；需整段脊瓦返修。')],
 'r05_c03--r06_c03':[(M,'大块砖缝几何接续，细部规则方格肌理仍在，不能记材质闭合。'),(M,'砖缝接续；横接边附近纹理相位/色阶及规则细格仍需统一。'),(M,'砖缝几何接续，规则细格与下方自然化斑驳交界仍可见。'),(M,'砖缝几何接续，规则细格和自然化斑驳交界仍需整体材质验收。')],
 'r05_c04--r06_c04':[(M,'大块砖缝接续，规则细格及浅水平纹理切换仍在。'),(R,'横接边 y20480、x13312..14336 地面阴影/色阶硬切，约x14230红纸屑被截断；需共享地砖与纸屑返修。'),(R,'本段共享石栏的北锚接回线附近约(14400..14520,20560..20700)存在竖截/帽石阶跃；需按整段栏体处理，不能只改一条边。'),(P,'本段石柱、地砖和花叶未见明显新增共享几何断点。')],
 'r06_c03--r06_c04':[(R,'竖接边 x12288、y约21300..21504 石栏左半明显模糊、右半清晰，帽石高度/轮廓接续差；整段栏体待修。'),(R,'竖接边 x12288、y21504..22528 两道石栏与地砖发生强烈错位、截断和重复，需连同两侧柱锚统一重建共享栏体。'),(M,'粗砖缝基本接续，但x12288两侧规则网格/自然斑驳差异明显，材质未闭合。'),(P,'本段树干、枝叶在竖接边连续，无明显硬切。')],
 'r06_c03--r07_c03':[(P,'本段蓝瓦轮廓与高光接续。'),(P,'本段蓝瓦筒弧线接续。'),(R,'横接边 y24576 右屋角红金侧脊错位，约x10880..11264出现矩形复制块/檐边截断；上下屋角需整体修复。'),(R,'横接边 y24576 及其下115像素约x11264..11650，金色脊瓦与花叶有矩形截条、重复脊端和突兀终止；与上一段合并返修。')]
}
junctions={
 'junction_r03-04_c02-03_100pct.png':(R,'交叉点(8192,12288)下方左右花叶清晰度突变并硬切；归入r04c02/r04c03共享花丛返修。'),
 'junction_r03-04_c03-04_100pct.png':(P,'交叉点(12288,12288)粗石砖轮廓和阴影接续；现有细纹理如实保留。'),
 'junction_r04-05_c03-04_100pct.png':(P,'交叉点(12288,16384)灯笼、红柱及墙脚连续，复核当前采用组合可用。'),
 'junction_r05-06_c03-04_100pct.png':(M,'交叉点(12288,20480)粗砖缝接续，细部规则方格/自然斑驳仍不统一。')}
for crop in inv['crops']:
 if crop['status'].startswith('reused'):
  crop['reviewMethod']='prior 100% visual PASS reused only after exact current crop pixel equality and stored evidence hash check';continue
 name=Path(crop['file']).name
 status,note=decisions[crop['pair']][crop['segment']-1] if crop['kind']=='pair' else junctions[name]
 crop.update(status=status,note=note,actuallyViewedAtNative100Percent=True,reviewMethod='view_image original; actual current 100% crop inspected')
for pair in inv['pairs']:
 states=[c['status'] for c in inv['crops'] if c.get('pair')==pair['pair']]
 pair['status']=R if R in states else M if M in states else 'shared_pair_visual_pass_only'
pair_counts=Counter(p['status'] for p in inv['pairs'])
inv['reviewSummary']={'currentPairCount':len(inv['pairs']),'pairStatusCounts':dict(pair_counts),'cropCount':len(inv['crops']),'exactPriorPassedCropsReused':28,'newCropsActuallyViewedAtNative100Percent':32,'cropStatusCounts':dict(Counter(c['status'] for c in inv['crops'])),'formalAcceptedCount':0}
inv['issueCrops']=[c for c in inv['crops'] if c['status'] in [R,M]]
inv['partialTileOpenIssues']=[{'tileId':'r05_c02','status':'partial_native_11_of_16_internal_QA_pending','missingCores':full.get('r05_c02',{}).get('missingCores',next(t for t in inv['tiles'] if t['tileId']=='r05_c02')['missingCores']),'knownOpenIssue':'Original west selection records r04c02/r05c02 north external flower cutoff near west end in minerror pair. No full4K present; not reassembled or marked passed in this audit.','evidence':meta(BASE/'west-current-selection-20261012.json')}]
inv['neighborMissingEdges']=[]
for tid,t in full.items():
 r,c=coord(tid)
 for dr,dc,d in [(-1,0,'north'),(1,0,'south'),(0,-1,'west'),(0,1,'east')]:
  nr,nc=r+dr,c+dc
  if not (1<=nr<=14 and 1<=nc<=14):continue
  n=f'r{nr:02d}_c{nc:02d}'
  if n not in full:inv['neighborMissingEdges'].append({'tileId':tid,'direction':d,'neighborTileId':n,'neighborCoreCountInNorthwestScope':next((x['coreCount'] for x in inv['tiles'] if x['tileId']==n),None),'status':'root_cross_zone_check_required' if nr>7 or nc>7 else 'partial_neighbor_missing' if n=='r05_c02' else 'no_adopted_neighbor_source_in_scope'})
inv['southernBoundary']=[{'tileId':f'r07_c{c:02d}','coreCount':next(t['coreCount'] for t in inv['tiles'] if t['tileId']==f'r07_c{c:02d}'),'file':next(t['file'] for t in inv['tiles'] if t['tileId']==f'r07_c{c:02d}')} for c in range(1,8)]
inv['eastBoundaryCoreCount']=0
# Mechanically export the existing internally closed middle 2x2 sample.
ids=['r04_c03','r04_c04','r05_c03','r05_c04'];b=[8192,12288,16384,20480]
im=Image.new('RGB',(8192,8192))
for tid in ids:
 tb=box(tid)
 with Image.open(full[tid]['file']) as src:im.paste(src,(tb[0]-b[0],tb[1]-b[1]))
p=OUT/'middle_r04-r05_c03-c04_native8192_internal-pass_perimeter-pending_v01.png';im.save(p);im.close();gc.collect()
gm=meta(p);gm.update(tiles=ids,globalBoxHalfOpen=b,method='exact_core_pixel_paste_no_resize_no_blend_no_synthesis',gameReady=False,scope='4 current selected tiles; all four internal shared tile boundaries reused from exact prior 100% PASS and current junction inspected; perimeter/final map acceptance pending',internalSharedBoundaryVisualPassed=True,perimeterAccepted=False)
inv['mechanicalNativeGroups'].append(gm)
for group in inv['mechanicalNativeGroups']:
 checks=[]
 with Image.open(group['file']) as g:
  for tid in group['tiles']:
   tb=box(tid);gb=group['globalBoxHalfOpen'];cb=(tb[0]-gb[0],tb[1]-gb[1],tb[2]-gb[0],tb[3]-gb[1])
   part=g.crop(cb)
   with Image.open(full[tid]['file']) as source:equal=ImageChops.difference(part,source.convert('RGB')).getbbox() is None
   checks.append({'tileId':tid,'cropBoxHalfOpen':cb,'decodedPixelsExactlyEqualToSelectedTile':equal,'selectedSha256':full[tid]['sha256']});part.close()
 group['corePixelEqualityVerification']=checks;group['allCorePixelsEqual']=all(q['decodedPixelsExactlyEqualToSelectedTile'] for q in checks)
 gc.collect()
# Summarize reference choices from archived generation evidence, without re-labelling models.
reference_counter=Counter();actual_models=Counter()
for t in inv['tiles']:
 for s in t['selectedSources']:
  ev=s.get('referenceEvidence',{});actual_models[str(ev.get('actualModel'))]+=1
  def refs(obj):
   if isinstance(obj,dict):
    if 'path' in obj and any(k in str(obj['path']).lower() for k in ['penglai-natural-stone','mail']):reference_counter[(str(obj['path']).replace('\\','/'),obj.get('sha256',''))]+=1
    for v in obj.values():refs(v)
   elif isinstance(obj,list):
    for v in obj:refs(v)
  refs(ev)
inv['referenceSelectionAudit']={'method':'archived generation metadata read only; no new generation and no external reference bytes replayed','actualModelValueCounts':dict(actual_models),'recordedPrimaryReferences':[{'file':f,'sha256':h,'occurrencesInNestedEvidence':n} for (f,h),n in reference_counter.items()],'interpretation':'Archived native sources consistently name the existing penglai layout/detail references and mail style variants. Neighbor anchor revisions are separately pinned; their compatibility is supported by current exact crop comparison. Historical PNG/JPG variants and actual model evidence are not silently substituted.'}
changes=[]
for m in inv['inputFiles']:
 f=Path(m['file']);final_hash=sha(f) if f.exists() else None
 if final_hash!=m.get('sha256'):changes.append({'file':m['file'],'snapshotSha256':m.get('sha256'),'finalSha256':final_hash})
inv['completedAtUtc']=now();inv['finalInputRehash']={'checkedFileCount':len(inv['inputFiles']),'changedInputs':changes,'stale':bool(changes)}
inv['allGroupsStale']=bool(changes)
for group in inv['mechanicalNativeGroups']:group['stale']=bool(changes)
(OUT/'inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
rep=['# 八仙岛西北区独立审计 v01','',f"完成时间（UTC）：{inv['completedAtUtc']}。所有新文件只在本审计目录；原生产文件、progress、AGENTS 与 Git 未操作。没有生图或 AI 修图，历史实际型号未确认。",'',
'实际去重覆盖为 **11 张完整4096×4096候选 + r05_c02 的11/16核心**，共 **187/784核心，缺597核心**。49图块中38块尚非完整候选。原采用记录报告9块内部通过，r06_c04 v8和r07_c03 v1内部未闭合；正式接受仍0。progress记录的10张/185核心及r07_c03 14/16已滞后，未修改原progress。','',
'每张采用图、原始4×4矩阵子图、生成证据及采用记录的尺寸/sha256见inventory.json。完整候选11张实测均4096²；原始选片187个核心位置的源图实测均1254²。当前候选包含既有同坐标和跨图块修复，原始矩阵标明为修复前基线；本次没有重新执行全递归来源重放，也没有把裁剪/拼接称作新生图。','',
'现行接边检查：14对相邻完整图块、56张边界分段和4张交叉点。28张通过旧验收裁片与当前实际像素完全相等及证据hash核对后复用；另外32张均用view_image original实际查看。详细结论、全图坐标、裁片sha256、采用输入在inventory.json。','',
'## 待修与待材质统一','',
'| 相邻图块 | 结论 | 主要位置与原因 |','|---|---|---|']
for pair in inv['pairs']:
 if pair['status'] in [R,M]:
  notes=[c['note'] for c in inv['crops'] if c.get('pair')==pair['pair'] and c['status'] in [R,M]]
  rep.append(f"| {pair['pair']} | {'需返修' if pair['status']==R else '几何局部过，材质待验'} | {' '.join(notes)} |")
rep+=['','r07_c03当前已有33张内部检查记录：21过、12待修；檐口高度、右屋角/花树复制截条、米墙条带和门框重复转角仍保留。r06_c04 v8来源清单明确保持内部未闭合；v1旧检结论不能直接替代v8修复边界验收。','',
'## 局部原生拼接','',
'所有输出均机械硬拼接，零缩放、零羽化、零改色、零补画。每组4块，总尺寸8192²；逐块回裁与当前采用图解码像素完全相等。原生图组不能等同整地图或外围验收完成。','',
'- `middle_r04-r05_c03-c04_native8192_internal-pass_perimeter-pending_v01.png`：四块间内接边全部复用现行相同像素的通过证据，中心交叉点本次实际查看通过；可交付为**局部内部接边样段，外围待验**。',
'- `upper-left_r03-r04_c02-c03_native8192_candidate_v01.png`：保留西侧已确认断点的独立候选，待修，不能记内部接边通过。',
'- `lower_r05-r06_c03-c04_native8192_candidate_v01.png`：保留石栏、纸屑裁断及材质差异的独立候选，待修。',
'- `*_preview1024_NOT_NATIVE.png` 为缩小概览，仅导览；所有结论用100%裁片。','',
'## 缺片、边界与接续','',
'r05_c02缺 s02_04、s03_03、s03_04、s04_03、s04_04。原西侧选择清单还记录它与r04_c02北边西端花朵截断；本次未缺图硬补或把局部拼成完整4K。其余未覆盖块和全部597核心缺单在inventory.json。','',
'南界r07_c01..c07只有r07_c03完整，其余0核心；c07东界整列0核心。r07_c03/r08_c03跨区邻接由根审计核对；本报告不读取SW原区或加速区。完整图块四周缺邻/partial的边逐条保留，缺邻不能记通过。','',
f"结束时重算 {len(inv['inputFiles'])} 个输入文件hash；变更 {len(changes)} 个，stale={bool(changes)}。如果生产窗口之后更新任何来源，本版本基于固定输入快照需重新核对。"]
(OUT/'review.md').write_text('\n'.join(rep)+'\n',encoding='utf-8')
print(json.dumps({'inventory':str(OUT/'inventory.json'),'review':str(OUT/'review.md'),'summary':inv['reviewSummary'],'finalInputRehash':inv['finalInputRehash'],'groups':[(g['file'],g['allCorePixelsEqual']) for g in inv['mechanicalNativeGroups']]},ensure_ascii=False,indent=2))
